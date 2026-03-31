# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Vishnu K P (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from datetime import timedelta, datetime
import pytz
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class RoomBookingLine(models.Model):
    """Model that handles the room booking form"""
    _name = "room.booking.line"
    _description = "Hotel Folio Line"
    _rec_name = 'room_id'

    @tools.ormcache()
    def _set_default_uom_id(self):
        return self.env.ref('uom.product_uom_day')

    booking_id = fields.Many2one("room.booking", string="Booking",
                                 help="Indicates the Room",
                                 ondelete="cascade")
    partner_id = fields.Many2one(
        'res.partner', 'Customer',
        related='booking_id.partner_id', readonly=False)

    phone = fields.Char('Phone', related='partner_id.phone')
    mobile = fields.Char('Mobile', related='partner_id.mobile')

    checkin_date = fields.Datetime(string="Check In",
                                   help="You can choose the date,"
                                        " Otherwise sets to current Date",
                                   required=True,
                                   index=True)
    checkout_date = fields.Datetime(string="Check Out",
                                    help="You can choose the date,"
                                         " Otherwise sets to current Date",
                                    required=True,
                                    index=True)
    room_id = fields.Many2one('hotel.room', string="Room",help="Indicates the Room",required=True)

    status = fields.Selection('Tình trạng phòng', related='room_id.status')

    uom_qty = fields.Float(string="Duration",
                           help="The quantity converted into the UoM used by "
                                "the product")
    uom_id = fields.Many2one('uom.uom',
                             default=_set_default_uom_id,
                             string="Unit of Measure",
                             help="This will set the unit of measure used")
    price_unit = fields.Float(string='Rent', digits='Product Price',
                               help="The rent price of the selected room.")
    price_unit_dem = fields.Float(string='Giá qua đêm', digits='Product Price',
                                  help="Giá qua đêm.")
    price_unit_gio = fields.Float(string='Giá giờ', digits='Product Price',
                                  help="Giá giờ.")
    price_unit_gio_ht = fields.Float(string='Giá giờ HT', compute='_compute_price_subtotal', help="Giá giờ HT.")
    tax_ids = fields.Many2many('account.tax',
                               'hotel_room_order_line_taxes_rel',
                               'room_id', 'tax_id',
                               related='room_id.taxes_ids',
                               string='Taxes',
                               help="Default taxes used when selling the room."
                               , domain=[('type_tax_use', '=', 'sale')])
    currency_id = fields.Many2one(string='Currency',
                                  related='booking_id.pricelist_id.currency_id'
                                  , help='The currency used')
    price_subtotal = fields.Float(string="Subtotal",
                                  compute='_compute_price_subtotal',
                                  help="Total Price excluding Tax")
    price_tax = fields.Float(string="Total Tax",
                             compute='_compute_price_subtotal',
                             help="Tax Amount")
    price_total = fields.Float(string="Total",
                               compute='_compute_price_subtotal',
                               help="Total Price including Tax")
    state = fields.Selection(related='booking_id.state',
                             string="Order Status",
                             help=" Status of the Order",
                             copy=False)
    booking_line_visible = fields.Boolean(default=False,
                                          string="Booking Line Visible",
                                          help="If True, then Booking Line "
                                               "will be visible")
    extra_guest_ids = fields.Many2many('res.partner', 'room_booking_line_guest_rel', 
                                     'line_id', 'partner_id', string='Khách lưu trú bổ sung',
                                     help="Danh sách các khách ở cùng trong phòng này")

    available_room_ids = fields.Many2many('hotel.room', compute='_compute_available_room_ids')

    @api.depends('checkin_date', 'checkout_date')
    def _compute_available_room_ids(self):
        for line in self:
            if line.checkin_date and line.checkout_date:
                domain = [
                    ('checkin_date', '<', line.checkout_date),
                    ('checkout_date', '>', line.checkin_date),
                    ('booking_id.state', 'in', ['reserved', 'check_in'])
                ]
                line_id = line._origin.id if hasattr(line, '_origin') and line._origin else line.id
                if line_id and not isinstance(line_id, models.NewId):
                    domain.append(('id', '!=', line_id))

                overlapping_lines = self.env['room.booking.line'].search(domain)
                occupied_room_ids = overlapping_lines.mapped('room_id.id')
                
                if occupied_room_ids:
                    available_rooms = self.env['hotel.room'].search([('id', 'not in', occupied_room_ids)])
                else:
                    available_rooms = self.env['hotel.room'].search([])
                
                line.available_room_ids = [(6, 0, available_rooms.ids)]
            else:
                line.available_room_ids = [(6, 0, self.env['hotel.room'].search([]).ids)]


    @api.onchange("uom_qty")
    def _onchange_uom_qty(self):
        """Update checkout_date based on uom_qty change"""
        for line in self:
            if line.uom_qty and line.checkin_date:
                if line.uom_id.name == 'Giờ':
                    line.checkout_date = line.checkin_date + timedelta(hours=line.uom_qty)
                elif line.uom_id.name in ['Ngày', 'Đêm']:
                    line.checkout_date = line.checkin_date + timedelta(days=line.uom_qty)

    @api.onchange("checkin_date", "checkout_date")
    def _onchange_checkin_date(self):
        """When you change checkin_date or checkout_date it will check
        and update the qty of hotel service line
        -----------------------------------------------------------------
        @param self: object pointer"""
        for line in self:
            # if line.checkout_date < line.checkin_date:
            #     raise ValidationError(
            #         _("Checkout must be greater or equal checkin date"))
            if line.checkout_date and line.checkin_date:
                diffdate = line.checkout_date - line.checkin_date
                qty = diffdate.days
                if diffdate.total_seconds() > 0:
                    qty = qty + 1
                line.uom_qty = qty

    @api.depends('uom_qty', 'price_unit', 'tax_ids', 'uom_id', 'checkin_date', 'checkout_date')
    def _compute_price_subtotal(self):
        """Compute the amounts of the room booking line."""
        user = self.env.user
        tz = pytz.timezone(user.tz) or pytz.utc
        
        # --- Batch-fetch all config parameters once instead of in the loop ---
        config_params = self.env['ir.config_parameter'].sudo()
        tutiengthu3 = float(config_params.get_param('hotel_management_odoo.so_tien_ap_dung_tieng_thu_3') or 0)
        apdung_auto_quadem_khi_nhanphong = config_params.get_param('hotel_management_odoo.tu_dong_chon_qua_dem_khi_nhan_phong')
        config_autogio = config_params.get_param('hotel_management_odoo.tu_dong_gio') or '0'
        config_autophut = config_params.get_param('hotel_management_odoo.tu_dong_phut') or '0'
        
        tu_dong_chon_qua_dem_khi_tra_phong = config_params.get_param('hotel_management_odoo.tu_dong_chon_qua_dem_khi_tra_phong')
        config_autogio_tra = config_params.get_param('hotel_management_odoo.tu_dong_tra_gio') or '0'
        config_autophut_tra = config_params.get_param('hotel_management_odoo.tu_dong_tra_phut') or '0'

        mot_ngay_du_24h = config_params.get_param('hotel_management_odoo.mot_ngay_du_24h', default='True') == 'True'
        khong_tinh_tien_phong_voi_hoa_don_time_khong_qua = config_params.get_param('hotel_management_odoo.khong_tinh_tien_phong_voi_hoa_don_time_khong_qua')
        so_phut_khong_tinh_tien = int(config_params.get_param('hotel_management_odoo.so_phut_khong_tinh_tien') or 30)

        uom_dem = self.env['uom.uom'].search([('name', '=', 'Đêm')], limit=1).id
        # ---------------------------------------------------------------------

        for line in self:
            if not line.checkin_date or not line.checkout_date:
                continue
            giodau = pytz.utc.localize(line.checkin_date).astimezone(tz)
            giocuoi = pytz.utc.localize(line.checkout_date).astimezone(tz)

            # Assign price_unit_gio_ht
            line.price_unit_gio_ht = tutiengthu3

            # --- Restore original auto-switch logic for 'Đêm' ---
            if apdung_auto_quadem_khi_nhanphong:
                autogio = config_autogio
                autophut = config_autophut
                if giodau.hour <= int(autogio):
                    if uom_dem: line.uom_id = uom_dem
            
            if tu_dong_chon_qua_dem_khi_tra_phong:
                autogio_tra = config_autogio_tra
                autophut_tra = config_autophut_tra
                if giocuoi.hour >= int(autogio_tra):
                    if uom_dem: line.uom_id = uom_dem
            # ---------------------------------------------------

            # 1. Calculate quantity based on unit of measure
            uom_qty = 1.0
            if line.uom_id.name == "Giờ":
                if (giocuoi - giodau).total_seconds() / 3600 <= 0:
                    uom_qty = 2.0
                else:
                    uom_qty = round((giocuoi - giodau).total_seconds() / 3600, 1)
            elif line.uom_id.name in ["Đêm", "Ngày"]:
                total_hours = (giocuoi - giodau).total_seconds() / 3600.0
                if total_hours <= 0:
                    uom_qty = 1.0
                else:
                    if mot_ngay_du_24h:
                        uom_qty = round(total_hours / 24.0, 1)
                        if uom_qty < 1.0:
                            uom_qty = 1.0
                    else:
                        days_diff = (giocuoi.date() - giodau.date()).days
                        if days_diff <= 0:
                            uom_qty = 1.0
                        else:
                            uom_qty = float(days_diff)

            # 2. Calculate subtotal based on quantity and configuration
            price_subtotal = 0.0
            if line.uom_id.name == "Giờ":
                apdungmacdinh = self.env['ir.config_parameter'].sudo().get_param('hotel_management_odoo.tinh_tien_cac_tieng_mac_dinh_ap_dung_sau_2h_dau')
                if apdungmacdinh:
                    giagiodau = float(self.env['ir.config_parameter'].sudo().get_param('hotel_management_odoo.so_tien_ap_dung') or 0)
                    tutiengthu3 = float(self.env['ir.config_parameter'].sudo().get_param('hotel_management_odoo.so_tien_ap_dung_tieng_thu_3') or 0)
                    if uom_qty <= 2:
                        price_subtotal = giagiodau
                    else:
                        price_subtotal = giagiodau + tutiengthu3 * (uom_qty - 2)
                else:
                    price_subtotal = uom_qty * line.price_unit_gio
            elif line.uom_id.name == "Đêm":
                price_subtotal = uom_qty * line.price_unit_dem
            else: # Ngày or others
                price_subtotal = uom_qty * line.price_unit

            # 2.5 Áp dụng quy tắc không tính tiền nếu ở quá ngắn
            if khong_tinh_tien_phong_voi_hoa_don_time_khong_qua:
                if (giocuoi - giodau).total_seconds() / 60.0 <= so_phut_khong_tinh_tien:
                    price_subtotal = 0.0

            # 3. Calculate taxes (respecting apdungthue)
            line_taxes = line.tax_ids if line.booking_id.apdungthue else self.env['account.tax']
            # We use price_subtotal as the base and quantity=1.0 to get the exact tax/total for the entire line amount
            tax_results = line_taxes.compute_all(price_subtotal, line.currency_id, 1.0, product=None, partner=line.booking_id.partner_id)
            price_tax = tax_results['total_included'] - tax_results['total_excluded']
            price_total = tax_results['total_included']

            # 4. Update the line
            line.update({
                'uom_qty': uom_qty,
                'price_subtotal': price_subtotal,
                'price_tax': price_tax,
                'price_total': price_total,
            })

            if self.env.context.get('import_file',
                                    False) and not self.env.user. \
                    user_has_groups('account.group_account_manager'):
                line.tax_id.invalidate_recordset(
                    ['invoice_repartition_line_ids'])

    def _convert_to_tax_base_line_dict(self):
        """ Convert the current record to a dictionary in order to use the
        generic taxes computation method
        defined on account.tax.
        :return: A python dictionary."""
        self.ensure_one()
        gia = 0
        price_subtotal = 0

        if self.ensure_one().uom_id.name == "Đêm":
            gia = self.price_unit_dem
            price_subtotal = gia * self.uom_qty
        if self.ensure_one().uom_id.name == "Ngày":
            gia = self.price_unit
            price_subtotal = gia * self.uom_qty
        return self.env['account.tax']._convert_to_tax_base_line_dict(
            self,
            partner=self.booking_id.partner_id,
            currency=self.currency_id,
            taxes=self.tax_ids if self.booking_id.apdungthue else self.env['account.tax'],
            price_unit=float(gia),
            quantity=self.uom_qty,
            price_subtotal=float(price_subtotal),
        )

    @api.onchange('room_id','checkin_date','checkout_date')
    def onchange_checkin_date(self):
        user = self.env.user
        tz = pytz.timezone(user.tz) or pytz.utc
        for line in self:
            if not line.checkin_date or not line.checkout_date:
                continue
            checkindate = pytz.utc.localize(line.checkin_date).astimezone(tz)
            checkoutdate = pytz.utc.localize(line.checkout_date).astimezone(tz)
            
            # Fetch Dynamic Prices
            if line.room_id and line.checkin_date:
                price, price_dem, price_gio = line.room_id.get_price_for_datetime(line.checkin_date)
                line.price_unit = price
                line.price_unit_dem = price_dem
                line.price_unit_gio = price_gio

            records = self.env['room.booking'].search([('state', 'in', ['reserved', 'check_in'])])
            for rec in records:
                if rec.id == line.booking_id._origin.id:
                    continue
                for room in rec.room_line_ids:
                    # Mathematical overlap check: (Start A < End B) and (End A > Start B)
                    if room.room_id.id == line.room_id.id:
                        if (line.checkin_date < room.checkout_date) and (line.checkout_date > room.checkin_date):
                            raise ValidationError(
                                _("Phòng %s đã có người đặt từ %s đến %s.\nVui lòng chọn phòng khác hoặc thay đổi thời gian!") % 
                                (room.room_id.name, 
                                 pytz.utc.localize(room.checkin_date).astimezone(tz).strftime('%d/%m/%Y %H:%M'), 
                                 pytz.utc.localize(room.checkout_date).astimezone(tz).strftime('%d/%m/%Y %H:%M'))
                            )
            # rec_room_id = rec.room_line_ids.room_id
            # rec_checkin_date = rec.room_line_ids.checkin_date
            # rec_checkout_date = rec.room_line_ids.checkout_date
            #
            # if rec_room_id and rec_checkin_date and rec_checkout_date:
            #     #Check for conflicts with existing room lines
            #     for line in self:
            #         if line.id != rec.id and line.room_id == rec_room_id:
            #             # Check if the dates overlap
            #             if (rec_checkin_date <= line.checkin_date <= rec_checkout_date or
            #                     rec_checkin_date <= line.checkout_date <= rec_checkout_date):
            #                 raise ValidationError(
            #                     _("Sorry, You cannot create a reservation for "
            #                       "this date since it overlaps with another "
            #                       "reservation..!!"))
            #             if rec_checkout_date <= line.checkout_date and rec_checkin_date >= line.checkin_date:
            #                 raise ValidationError(
            #                     "Sorry You cannot create a reservation for this"
            #                     "date due to an existing reservation between "
            #                     "this date")
