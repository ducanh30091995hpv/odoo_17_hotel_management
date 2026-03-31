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
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class HotelRoom(models.Model):
    """Model that holds all details regarding hotel room"""
    _name = 'hotel.room'
    _description = 'Rooms'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'floor_sequence, name, id'

    @tools.ormcache()
    def _get_default_uom_id(self):
        """Method for getting the default uom id"""
        return self.env.ref('uom.product_uom_unit')

    name = fields.Char(string='Name', help="Name of the Room", index='trigram',
                       required=True, translate=True)
    status = fields.Selection([("available", "Available"),
                               ("reserved", "Reserved"),
                               ("occupied", "Occupied"),
                               ("repair", "Repair"),
                               ("dirty", "Dirty"),
                               ("clean", "Clean")],
                               default="available", string="Status",
                               help="Status of The Room",
                               tracking=True, index=True)
    list_price = fields.Float(string='Rent', digits='Product Price',
                              help="The rent of the room.")
    list_price_dem = fields.Float(string='Giá qua đêm', digits='Product Price',
                              help="Giá qua đêm.")
    list_price_gio = fields.Float(string='Giá giờ', digits='Product Price',
                              help="Giá giờ.")
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure',
                             default=_get_default_uom_id, required=True,
                             help="Default unit of measure used for all stock"
                                  " operations.")
    room_image = fields.Image(string="Room Image", max_width=1920,
                              max_height=1920, help='Image of the room')
    taxes_ids = fields.Many2many('account.tax',
                                 'hotel_room_taxes_rel',
                                 'room_id', 'tax_id',
                                 help="Default taxes used when selling the"
                                      " room.", string='Customer Taxes',
                                 domain=[('type_tax_use', '=', 'sale')],
                                 default=lambda self: self.env.company.
                                 account_sale_tax_id)
    room_amenities_ids = fields.Many2many("hotel.amenity",
                                          string="Room Amenities",
                                          help="List of room amenities.")
    floor_id = fields.Many2one('hotel.floor', string='Floor',
                               help="Automatically selects the Floor",
                               tracking=True, index=True)
    loaiphong_id = fields.Many2one('hotel.loaiphong', string='Loại phòng',
                               help="Automatically selects the Loại phòng",
                               tracking=True, index=True)
    special_price_ids = fields.One2many('hotel.room.price.special', 'room_id', string='Giá đặc biệt')
    cleanup_image_ids = fields.One2many('hotel.room.cleanup.image', 'room_id', string='Cleanup Images')
    equipment_ids = fields.One2many('hotel.room.equipment', 'room_id', string='Vật tư & Thiết bị')
    floor_sequence = fields.Integer(related='floor_id.sequence', store=True, string='Thứ tự tầng')
    user_id = fields.Many2one('res.users', string="User",
                              related='floor_id.user_id',
                              help="Automatically selects the manager",
                              tracking=True)
    room_type = fields.Selection([('single', 'Single'),
                                  ('double', 'Double'),
                                  ('dormitory', 'Dormitory')],
                                 required=True, string="Room Type",
                                 help="Automatically selects the Room Type",
                                 tracking=True,
                                 default="single")
    num_person = fields.Integer(string='Number Of Persons',
                                required=True,
                                help="Automatically chooses the No. of Persons",
                                tracking=True)
    description = fields.Html(string='Description', help="Add description",
                              translate=True)

    @api.constrains("num_person")
    def _check_capacity(self):
        """Check capacity function"""
        for room in self:
            if room.num_person <= 0:
                raise ValidationError(_("Room capacity must be more than 0"))

    @api.onchange("room_type")
    def _onchange_room_type(self):
        """Based on selected room type, number of person will be updated.
        ----------------------------------------
        @param self: object pointer"""
        if self.room_type == "single":
            self.num_person = 1
        elif self.room_type == "double":
            self.num_person = 2
        else:
            self.num_person = 4

    def change_repair_room(self):
        for record in self:
            ob1 = self.env['hotel.room'].search([('id', '=', record.id)])
            if record.id and ob1.status != 'occupied':
                record.write({'status': 'repair'})
                return 0
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _("Thông báo"),
                        'type': 'warning',
                        'message': _("Đã có người thuê"),
                        'sticky': True,
                    },
                }

    def change_repaired_room(self):
        for record in self:
            ob1 = self.env['hotel.room'].search([('id', '=', record.id)])
            if record.id and ob1.status != 'occupied':
                record.write({'status': 'available'})
                return 0
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _("Thông báo"),
                        'type': 'warning',
                        'message': _("Đã có người thuê"),
                        'sticky': True,
                    },
                }

    def change_cleanup_room(self):
        for record in self:
            ob1 = self.env['hotel.room'].search([('id', '=', record.id)])
            if record.id and ob1.status != 'occupied':
                record.write({'status': 'clean'})
                return 0
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _("Thông báo"),
                        'type': 'warning',
                        'message': _("Đã có người thuê"),
                        'sticky': True,
                    },
                }

    def change_cleaned_room(self):
        for record in self:
            ob1 = self.env['hotel.room'].search([('id', '=', record.id)])
            if record.id and ob1.status != 'occupied':
                record.write({'status': 'available'})
                return 0
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _("Thông báo"),
                        'type': 'warning',
                        'message': _("Đã có người thuê"),
                        'sticky': True,
                    },
                }

    def action_cleanroom_id(self):
        self.write({"status": "available"})

    def write(self, vals):
        """Override write to create cleaning request when room becomes dirty"""
        res = super(HotelRoom, self).write(vals)
        if 'status' in vals:
            # Send notification to Odoo Bus for real-time room chart update
            self.env['bus.bus']._sendone('hotel_room_status_channel', 'hotel_room_status_changed', {
                'room_ids': self.ids,
                'new_status': vals['status']
            })

            if vals['status'] == 'dirty':
                # 1. Batch find existing cleaning requests for all rooms in self
                existing_requests = self.env['cleaning.request'].search([
                    ('room_id', 'in', self.ids),
                    ('state', 'in', ['draft', 'assign', 'ongoing'])
                ])
                rooms_with_requests = existing_requests.mapped('room_id.id')
                
                # 2. Get default cleaning team once
                team = self.env['cleaning.team'].search([], limit=1)
                
                if team:
                    for record in self:
                        if record.id not in rooms_with_requests:
                            self.env['cleaning.request'].create({
                                'cleaning_type': 'room',
                                'room_id': record.id,
                                'team_id': team.id,
                                'description': _('Tự động tạo khi phòng chuyển sang bẩn (Dirty)'),
                                'state': 'draft'
                            })
        return res

    def get_price_for_datetime(self, dt):
        """Returns the dynamic prices (Day, Night, Hour) for a given datetime."""
        self.ensure_one()
        
        # Bypass Odoo's onchange proxy wrapper to guarantee ALL fields are accessible
        r_id = self.id
        if hasattr(r_id, 'origin') and r_id.origin:
            r_id = r_id.origin
        elif getattr(self, '_origin', False):
            r_id = self._origin.id
            
        if isinstance(r_id, models.NewId) or not r_id:
            real_room = self
        else:
            real_room = self.env['hotel.room'].browse(r_id)

        if not dt:
            return real_room.list_price, real_room.list_price_dem, real_room.list_price_gio

        def _apply_rule(rule):
            p_day = real_room.list_price
            p_night = real_room.list_price_dem
            p_hour = real_room.list_price_gio
            
            if rule.calculation_method == 'fixed':
                return rule.price_unit or p_day, rule.price_unit_dem or p_night, rule.price_unit_gio or p_hour
            elif rule.calculation_method == 'add_amount':
                amt = rule.fixed_amount_to_add
                return p_day + amt, p_night + amt, p_hour + amt
            elif rule.calculation_method == 'add_percent':
                ratio = 1.0 + (rule.percent_to_add / 100.0)
                return p_day * ratio, p_night * ratio, p_hour * ratio
            return p_day, p_night, p_hour
        
        # 1. Check for Holidays (Priority)
        holiday_rule = real_room.special_price_ids.filtered(
            lambda r: r.type == 'holiday' and getattr(r.holiday_id, 'date_from', False) and getattr(r.holiday_id, 'date_to', False) and r.holiday_id.date_from <= dt.date() <= r.holiday_id.date_to
        )
        if holiday_rule:
            return _apply_rule(holiday_rule[0])
        
        # 2. Check for Weekends
        day_of_week = str(dt.weekday())
        weekend_rule = real_room.special_price_ids.filtered(
            lambda r: r.type == 'weekend' and r.day_of_week == day_of_week
        )
        if weekend_rule:
            return _apply_rule(weekend_rule[0])
        
        # 3. Default prices
        return self.list_price, self.list_price_dem, self.list_price_gio


class HotelRoomCleanupImage(models.Model):
    _name = 'hotel.room.cleanup.image'
    _description = 'Housekeeping Room Images'

    room_id = fields.Many2one('hotel.room', string='Room', ondelete='cascade')
    image = fields.Image(string='Image', required=True)
    description = fields.Char(string='Description')
    create_date = fields.Datetime(string='Date', default=fields.Datetime.now)