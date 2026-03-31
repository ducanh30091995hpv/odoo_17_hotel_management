# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.tools.safe_eval import pytz

class RoomBooking(models.Model):
    _inherit = "room.booking"

    def create_list(self, line_ids):
        """Returns a Dictionary containing the Booking line Values"""
        account_move_line = self.env['account.move.line'].search_read(
            domain=[('ref', '=', self.name),
                    ('display_type', '!=', 'payment_term')],
            fields=['name', 'quantity', 'price_unit', 'product_type'], )
        for rec in account_move_line:
            if 'id' in rec: del rec['id']
        booking_dict = {}
        for line in line_ids:
            name = ""
            product_type = ""
            if line_ids._name == 'food.booking.line':
                name = line.food_id.name
                product_type = 'food'
            elif line_ids._name == 'fleet.booking.line':
                name = line.fleet_id.name
                product_type = 'fleet'
            elif line_ids._name == 'service.booking.line':
                name = line.service_id.name
                product_type = 'service'
            elif line_ids._name == 'phutroi.booking.line':
                name = line.phutroi_id.name
                product_type = 'phutroi'
            elif line_ids._name == 'phuthu.booking.line':
                name = line.phuthu_id.name
                product_type = 'phuthu'
            elif line_ids._name == 'event.booking.line':
                name = line.event_id.name
                product_type = 'event'
            booking_dict = {'name': name,
                            'quantity': line.uom_qty,
                            'price_unit': line.price_unit,
                            'product_type': product_type, 'tax_ids': line.tax_ids, 'uom_id': line.uom_id.id,
                            'type': line.uom_id.name}
        return booking_dict

    def action_print_bill(self):
        return self.env.ref('hotel_management_odoo.action_in_bill').report_action(self)

    def get_value_sotaikhoannganhang(self):
        return self.env['ir.config_parameter'].sudo().get_param('hotel_management_odoo.sotaikhoannganhang')

    def get_value_tennganhang(self):
        return self.env['ir.config_parameter'].sudo().get_param('hotel_management_odoo.tennganhang')

    def return_loichaochantrang(self):
        return self.env['ir.config_parameter'].sudo().get_param('hotel_management_odoo.loichaochantrang_bill')

    def get_name_user(self):
        user = self.env.user
        return "Thu ngân: " + user.name

    def gettimenow(self):
        user = self.env.user
        tz = pytz.timezone(user.tz) or pytz.utc
        ngaygio = pytz.utc.localize(datetime.now()).astimezone(tz).strftime('%d/%m/%Y %H:%M')
        return "In lúc: " + ngaygio

    def get_dongia_gio(self):
        apdunggiagio = self.env['ir.config_parameter'].sudo().get_param(
            'hotel_management_odoo.tinh_tien_cac_tieng_mac_dinh_ap_dung_sau_2h_dau')
        sotien = self.env['ir.config_parameter'].sudo().get_param('hotel_management_odoo.so_tien_ap_dung_tieng_thu_3')
        for line in self.room_line_ids:
            if apdunggiagio and line.uom_id.name == "Giờ":
                return "{:,.0f}".format(float(sotien)).replace(',', '.')
            elif not apdunggiagio and line.uom_id.name == "Giờ":
                return "{:,.0f}".format(line.price_unit_gio).replace(',', '.')
        return ""

    def get_all_booking_lines(self):
        """Returns a combined list of all line items for the bill"""
        res = []
        res.extend(self.room_line_ids)
        res.extend(self.food_order_line_ids)
        res.extend(self.service_line_ids)
        res.extend(self.phutroi_line_ids)
        res.extend(self.phuthu_line_ids)
        res.extend(self.event_line_ids)
        res.extend(self.vehicle_line_ids)
        return res

    def get_amount_in_words(self, amount):
        """Returns Vietnamese text for amount"""
        if not self.currency_id:
            return ""
        return self.currency_id.with_context(lang='vi_VN').amount_to_text(amount)

    def get_vietqr_url(self):
        """Generates a VietQR URL for payment with Booking ID in description"""
        bank_id = self.get_value_tennganhang() or "ICB"
        account_no = self.get_value_sotaikhoannganhang() or ""
        amount = int(self.amount_total)
        info = f"BOOKING {self.name}"
        name = self.company_id.name
        return f"https://img.vietqr.io/image/{bank_id}-{account_no}-compact.jpg?amount={amount}&addInfo={info}&accountName={name}"

    def return_src_image(self):
        """Returns the VietQR URL (Used in reports and UI)"""
        return self.get_vietqr_url()
