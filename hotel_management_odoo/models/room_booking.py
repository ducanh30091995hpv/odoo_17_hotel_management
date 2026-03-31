# -*- coding: utf-8 -*-
import logging
from datetime import timedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class RoomBooking(models.Model):
    """Model that handles the hotel room booking and all operations related
     to booking"""
    _name = "room.booking"
    _description = "Hotel Room Reservation"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _logger = logging.getLogger(__name__)

    name = fields.Char(string="Folio Number", readonly=True, index=True,
                       default="New", help="Name of Folio")
    company_id = fields.Many2one('res.company', string="Company",
                                 help="Choose the Company",
                                 required=True, index=True,
                                 default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', string="Customer",
                                 help="Customers of hotel",
                                 required=True, index=True, tracking=1,
                                 domain="[('type', '!=', 'private'),"
                                        " ('company_id', 'in', "
                                        "(False, company_id))]")
    date_order = fields.Datetime(string="Order Date",
                                 required=True, copy=False,
                                 help="Creation date of draft/sent orders,"
                                      " Confirmation date of confirmed orders",
                                 default=fields.Datetime.now, index=True)
    maintenance_request_sent = fields.Boolean(default=False,
                                              string="Maintenance Request sent"
                                                     "or Not",
                                              help="sets to True if the "
                                                   "maintenance request send "
                                                   "once")
    checkin_date = fields.Datetime(string="Check In",
                                   help="Date of Checkin",
                                   default=fields.Datetime.now())
    checkout_date = fields.Datetime(string="Check Out",
                                    help="Date of Checkout",
                                    default=fields.Datetime.now() + timedelta(
                                        hours=23, minutes=59, seconds=59))
    hotel_policy = fields.Selection([("prepaid", "On Booking"),
                                     ("manual", "On Check In"),
                                     ("picking", "On Checkout"),
                                     ],
                                    default="manual", string="Hotel Policy",
                                    help="Hotel policy for payment that "
                                         "either the guest has to pay at "
                                         "booking time, check-in "
                                         "or check-out time.", tracking=True)
    duration = fields.Integer(string="Duration in Days",
                               compute='_compute_duration', store=True,
                               help="Number of days which will automatically "
                                    "count from the check-in and check-out "
                                    "date.")
    invoice_button_visible = fields.Boolean(string='Invoice Button Display',
                                            help="Invoice button will be "
                                                 "visible if this button is "
                                                 "True")
    invoice_status = fields.Selection(
        selection=[('no_invoice', 'Nothing To Invoice'),
                   ('to_invoice', 'To Invoice'),
                   ('invoiced', 'Invoiced'),
                   ], string="Invoice Status",
        help="Status of the Invoice",
        default='no_invoice', tracking=True)
    hotel_invoice_id = fields.Many2one("account.move",
                                       string="Invoice",
                                       help="Indicates the invoice",
                                       copy=False)
    need_phuthu = fields.Boolean(default=False, string="Need Phụ Thu",
                                 help="Check if a Service to be added with"
                                      " the Booking")
    need_service = fields.Boolean(default=False, string="Need Service",
                                  help="Check if a Service to be added with"
                                       " the Booking")
    need_fleet = fields.Boolean(default=False, string="Need Vehicle",
                                help="Check if a Fleet to be"
                                     " added with the Booking")
    need_food = fields.Boolean(default=False, string="Need Food",
                               help="Check if a Food to be added with"
                                    " the Booking")
    need_event = fields.Boolean(default=False, string="Need Event",
                                help="Check if a Event to be added with"
                                     " the Booking")
    need_phutroi = fields.Boolean(default=False, string="Phụ Trội",
                                  help="Phụ Trội")
    service_line_ids = fields.One2many("service.booking.line",
                                       "booking_id",
                                       string="Service",
                                       help="Hotel services details provided to"
                                            "Customer and it will included in "
                                            "the main Invoice.")
    event_line_ids = fields.One2many("event.booking.line",
                                     'booking_id',
                                     string="Event",
                                     help="Hotel event reservation detail.")
    phutroi_line_ids = fields.One2many("phutroi.booking.line",
                                       'booking_id',
                                       string="Phụ trội",
                                       help="Hotel event reservation detail.")
    phuthu_line_ids = fields.One2many("phuthu.booking.line",
                                      'booking_id',
                                      string="Phụ trội",
                                      help="Hotel event reservation detail.")
    vehicle_line_ids = fields.One2many("fleet.booking.line",
                                       "booking_id",
                                       string="Vehicle",
                                       help="Hotel fleet reservation detail.")
    room_line_ids = fields.One2many("room.booking.line",
                                    "booking_id", string="Room",
                                    help="Hotel room reservation detail.")
    food_order_line_ids = fields.One2many("food.booking.line",
                                          "booking_id",
                                          string='Food',
                                          help="Food details provided"
                                               " to Customer and"
                                               " it will included in the "
                                               "main invoice.", )
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('reserved', 'Reserved'),
                                        ('check_in', 'Check In'),
                                        ('check_out', 'Check Out'),
                                        ('cancel', 'Cancelled'),
                                        ('done', 'Done')],
                             string='Trạng thái', default='draft',
                             required=True, tracking=True, index=True)
    user_id = fields.Many2one(comodel_name='res.partner',
                              string="Invoice Address",
                              compute='_compute_user_id',
                              help="Sets the User automatically",
                              required=True,
                              domain="['|', ('company_id', '=', False), "
                                     "('company_id', '=',"
                                     " company_id)]")
    pricelist_id = fields.Many2one(comodel_name='product.pricelist',
                                   string="Pricelist",
                                   compute='_compute_pricelist_id', readonly=False,
                                   required=True,
                                   tracking=1,
                                   store=True,
                                   help="If you change the pricelist,"
                                        " only newly added lines"
                                        " will be affected.")
    currency_id = fields.Many2one(
        string="Currency", help="This is the Currency used",
        related='pricelist_id.currency_id',
        depends=['pricelist_id.currency_id'],
    )
    invoice_count = fields.Integer(compute='_compute_invoice_count',
                                   string="Invoice "
                                          "Count",
                                   help="The number of invoices created")
    account_move = fields.Integer(string='Invoice Id',
                                  help="Id of the invoice created")
    amount_untaxed = fields.Monetary(string="Total Untaxed Amount",
                                     help="This indicates the total untaxed "
                                          "amount",
                                     compute='_compute_amount_untaxed',
                                     tracking=5)
    amount_tax = fields.Monetary(string="Taxes", help="Total Tax Amount",
                                 compute='_compute_amount_untaxed')
    amount_total = fields.Monetary(string="Total",
                                   help="The total Amount including Tax",
                                   compute='_compute_amount_untaxed',
                                   tracking=4)
    amount_untaxed_room = fields.Monetary(string="Room Untaxed",
                                          help="Untaxed Amount for Room",
                                          compute='_compute_amount_untaxed',
                                          tracking=5)
    amount_untaxed_food = fields.Monetary(string="Food Untaxed",
                                          help="Untaxed Amount for Food",
                                          compute='_compute_amount_untaxed',
                                          tracking=5)
    amount_untaxed_event = fields.Monetary(string="Event Untaxed",
                                           help="Untaxed Amount for Event",
                                           compute='_compute_amount_untaxed',
                                           tracking=5)
    amount_untaxed_service = fields.Monetary(
        string="Service Untaxed", help="Untaxed Amount for Service",
        compute='_compute_amount_untaxed', tracking=5)
    amount_untaxed_phutroi = fields.Monetary(
        string="Phu Trội Untaxed", help="Untaxed Amount for Phụ Trội",
        compute='_compute_amount_untaxed', tracking=5)
    amount_untaxed_phuthu = fields.Monetary(
        string="Phu Thu Untaxed", help="Untaxed Amount for Phụ Thu",
        compute='_compute_amount_untaxed', tracking=5)
    amount_untaxed_fleet = fields.Monetary(string="Amount Untaxed",
                                           help="Untaxed amount for Fleet",
                                           compute='_compute_amount_untaxed',
                                           tracking=5)
    amount_taxed_room = fields.Monetary(string="Rom Tax", help="Tax for Room",
                                        compute='_compute_amount_untaxed',
                                        tracking=5)
    amount_taxed_food = fields.Monetary(string="Food Tax", help="Tax for Food",
                                        compute='_compute_amount_untaxed',
                                        tracking=5)
    amount_taxed_event = fields.Monetary(string="Event Tax",
                                         help="Tax for Event",
                                         compute='_compute_amount_untaxed',
                                         tracking=5)
    amount_taxed_service = fields.Monetary(string="Service Tax",
                                           compute='_compute_amount_untaxed',
                                           help="Tax for Service", tracking=5)
    amount_taxed_phutroi = fields.Monetary(string="Phụ Trội Tax",
                                           compute='_compute_amount_untaxed',
                                           help="Tax for Phụ Trội", tracking=5)
    amount_taxed_phuthu = fields.Monetary(string="Phụ Thu Tax",
                                          compute='_compute_amount_untaxed',
                                          help="Tax for Phụ Thu", tracking=5)
    amount_taxed_fleet = fields.Monetary(string="Fleet Tax",
                                         compute='_compute_amount_untaxed',
                                         help="Tax for Fleet", tracking=5)
    amount_total_room = fields.Monetary(string="Total Amount for Room",
                                        compute='_compute_amount_untaxed',
                                        help="This is the Total Amount for "
                                             "Room", tracking=5)
    amount_total_food = fields.Monetary(string="Total Amount for Food",
                                        compute='_compute_amount_untaxed',
                                        help="This is the Total Amount for "
                                             "Food", tracking=5)
    amount_total_event = fields.Monetary(string="Total Amount for Event",
                                         compute='_compute_amount_untaxed',
                                         help="This is the Total Amount for "
                                              "Event", tracking=5)
    amount_total_service = fields.Monetary(string="Total Amount for Service",
                                           compute='_compute_amount_untaxed',
                                           help="This is the Total Amount for "
                                                "Service", tracking=5)
    amount_total_phutroi = fields.Monetary(string="Total Amount for Phụ Trội",
                                           compute='_compute_amount_untaxed',
                                           help="This is the Total Amount for "
                                                "Phụ Trội", tracking=5)
    amount_total_phuthu = fields.Monetary(string="Total Amount for Phụ Thu",
                                          compute='_compute_amount_untaxed',
                                          help="This is the Total Amount for "
                                               "Phụ Thu", tracking=5)
    amount_total_fleet = fields.Monetary(string="Total Amount for Fleet",
                                         compute='_compute_amount_untaxed',
                                         help="This is the Total Amount for "
                                              "Fleet", tracking=5)
    tratruoc = fields.Monetary(string="Số tiền trả trước", tracking=5,
                               help="This is the Total Amount for "
                                    "Fleet")
    apdungthue = fields.Boolean(default=False, string="Áp dụng thuế hay không",
                                help="Áp dụng thuế hay không")

    def unlink(self):
        for rec in self:
            if rec.state != 'cancel' and rec.state != 'draft':
                raise ValidationError('Cannot delete the Booking. Cancel the Booking ')
        return super().unlink()

    @api.model_create_multi
    def create(self, vals_list):
        """Sequence Generation"""
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'room.booking')
        return super().create(vals_list)

    @api.depends('checkin_date', 'checkout_date')
    def _compute_duration(self):
        """Automatically compute duration in days from check-in and check-out dates"""
        for rec in self:
            if rec.checkin_date and rec.checkout_date:
                diff = rec.checkout_date - rec.checkin_date
                rec.duration = max(1, diff.days)
            else:
                rec.duration = 0

    @api.depends('partner_id')
    def _compute_user_id(self):
        """Computes the User id"""
        for order in self:
            order.user_id = \
                order.partner_id.address_get(['invoice'])[
                    'invoice'] if order.partner_id else False

    def _compute_invoice_count(self):
        """Compute the invoice count"""
        for record in self:
            record.invoice_count = self.env['account.move'].search_count(
                [('ref', '=', self.name)])

    @api.depends('partner_id')
    def _compute_pricelist_id(self):
        """Computes PriceList with fallback to default if partner has none"""
        for order in self:
            if not order.partner_id:
                order.pricelist_id = False
                continue
            
            pricelist = order.partner_id.property_product_pricelist
            if not pricelist:
                pricelist = self.env['product.pricelist'].search([
                    '|', ('company_id', '=', order.company_id.id), ('company_id', '=', False)
                ], limit=1)
            order.pricelist_id = pricelist

    @api.constrains("room_line_ids")
    def _check_duplicate_folio_room_line(self):
        for record in self:
            ids = set()
            for line in record.room_line_ids:
                if line.room_id.id in ids:
                    raise ValidationError(
                        _(
                            """Room Entry Duplicates Found!, """
                            """You Cannot Book "%s" Room More Than Once!"""
                        )
                        % line.room_id.name
                    )
                ids.add(line.room_id.id)

    def action_done(self):
        """Button action_confirm function"""
        for rec in self.env['account.move'].search(
                [('ref', '=', self.name)]):
            if rec.payment_state != 'not_paid':
                self.write({"state": "done"})
                self.is_checkin = False
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'type': 'success',
                        'message': "Booking Checked Out Successfully!",
                        'next': {'type': 'ir.actions.act_window_close'},
                    }
                }
        self.write({"state": "done"})

    def action_invoice(self):
        """Method for creating invoice"""
        if not self.room_line_ids:
            raise ValidationError(_("Please Enter Room Details"))
        booking_list = self._compute_amount_untaxed(True)
        if booking_list:
            account_move = self.env["account.move"].create([{
                'move_type': 'out_invoice',
                'invoice_date': fields.Date.today(),
                'partner_id': self.partner_id.id,
                'ref': self.name,
            }])
            for rec in booking_list:
                tong = 0
                if rec['product_type'] == 'room':
                    if self.env['ir.config_parameter'].sudo().get_param(
                            'hotel_management_odoo.tinh_tien_cac_tieng_mac_dinh_ap_dung_sau_2h_dau') and rec[
                        'type'] == 'Giờ':
                        if rec['quantity'] <= 2:
                            rec['price_unit'] = self.env['ir.config_parameter'].sudo().get_param(
                                'hotel_management_odoo.so_tien_ap_dung')
                            tong = rec['price_unit']
                        elif rec['quantity'] > 2:
                            rec['price_unit'] = (int(self.env['ir.config_parameter'].sudo().get_param(
                                'hotel_management_odoo.so_tien_ap_dung')) + (int(self.env[
                                'ir.config_parameter'].sudo().get_param(
                                'hotel_management_odoo.so_tien_ap_dung_tieng_thu_3')) * (rec['quantity'] - 2))) / rec[
                                                    'quantity']
                            tong = self.env['ir.config_parameter'].sudo().get_param(
                                'hotel_management_odoo.so_tien_ap_dung') + (round(rec['quantity']) - 2) * self.env[
                                       'ir.config_parameter'].sudo().get_param(
                                'hotel_management_odoo.so_tien_ap_dung_tieng_thu_3')
                    else:
                        tong = rec['quantity'] * rec['price_unit']
                else:
                    tong = rec['quantity'] * rec['price_unit']
                account_move.invoice_line_ids.create([{
                    'name': rec['name'],
                    'quantity': rec['quantity'],
                    'price_unit': rec['price_unit'],
                    'move_id': account_move.id,
                    'product_uom_id': rec['uom_id'],
                    'price_subtotal': tong,
                    'product_type': rec['product_type'],
                    'tax_ids': rec['tax_ids'],
                }])
            self.write({'invoice_status': "invoiced"})
            self.invoice_button_visible = True
            return {
                'type': 'ir.actions.act_window',
                'name': 'Invoices',
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': account_move.id,
                'context': "{'create': False}"
            }

    def action_view_invoices(self):
        """Method for Returning invoice View"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invoices',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('ref', '=', self.name)],
            'context': "{'create': False}"
        }

    def action_draft(self):
        self.write({"state": "draft"})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': "Đã chuyển về nháp!",
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
