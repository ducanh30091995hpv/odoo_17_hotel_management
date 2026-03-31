# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class RoomBooking(models.Model):
    _inherit = "room.booking"

    def action_reserve(self):
        """Button Reserve Function"""
        if self.state == 'reserved':
            message = _("Room Already Reserved.")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'warning',
                    'message': message,
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
        if self.room_line_ids:
            for room in self.room_line_ids:
                room.room_id.write({
                    'status': 'reserved',
                })
            self.write({"state": "reserved"})
            if not self.is_zns_sent_reserved:
                self._send_zalo_notification('reserved')
                self.is_zns_sent_reserved = True
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'message': "Rooms reserved Successfully!",
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
        raise ValidationError(_("Please Enter Room Details"))

    def action_checkin(self):
        """
        @param self: object pointer
        """
        if not self.room_line_ids:
            raise ValidationError(_("Please Enter Room Details"))
        else:
            for room in self.room_line_ids:
                room.room_id.write({
                    'status': 'occupied',
                })
            self.write({"state": "check_in"})
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'message': "Booking Checked In Successfully!",
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }

    def action_checkout(self):
        """Button action_checkout function"""
        now = fields.Datetime.now()
        
        # Check for Early Checkout
        is_early = False
        for room in self.room_line_ids:
            if room.checkout_date and now < room.checkout_date:
                time_diff = room.checkout_date - now
                if time_diff.total_seconds() / 3600.0 > 1.0: # Checking out more than 1 hour early
                    is_early = True
                    break
        
        if is_early and not self._context.get('early_checkout_policy'):
            return {
                'name': 'Xử lý Trả phòng sớm',
                'type': 'ir.actions.act_window',
                'res_model': 'early.checkout.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {'default_booking_id': self.id}
            }
            
        return self._process_checkout()

    def _process_checkout(self):
        now = fields.Datetime.now()
        PhuTroi = self.env['hotel.phutroi']
        has_phutroi = False
        
        policy = self._context.get('early_checkout_policy', 'actual')
        penalty_amount = self._context.get('early_checkout_penalty', 0.0)

        for room in self.room_line_ids:
            is_early_room = False
            if room.checkout_date and now < room.checkout_date:
                time_diff = room.checkout_date - now
                if time_diff.total_seconds() / 3600.0 > 1.0:
                    is_early_room = True
                    
                    if policy == 'full':
                        pass
                    elif policy in ['actual', 'penalty']:
                        time_stay = now - room.checkin_date
                        qty = 1.0
                        if room.uom_id.name == "Giờ":
                            if time_stay.total_seconds() / 3600 <= 0:
                                qty = 2.0
                            else:
                                qty = round(time_stay.total_seconds() / 3600, 1)
                        else:
                            if time_stay.days <= 0:
                                qty = 1.0
                            else:
                                qty = round(time_stay.total_seconds() / 86400, 1)
                                
                        room.write({'checkout_date': now, 'uom_qty': float(qty)})
                        
                        if policy == 'penalty' and penalty_amount > 0 and not has_phutroi:
                            phutroi_name = "Phạt trả phòng sớm"
                            phutroi_service = PhuTroi.search([('name', '=', phutroi_name)], limit=1)
                            if not phutroi_service:
                                phutroi_service = PhuTroi.create({'name': phutroi_name, 'unit_price': 0.0})
                            
                            self.write({
                                'phutroi_line_ids': [(0, 0, {
                                    'phutroi_id': phutroi_service.id,
                                    'uom_qty': 1.0,
                                    'price_unit': penalty_amount,
                                })]
                            })
                            has_phutroi = True
            
            if not is_early_room:
                if room.checkout_date and now > room.checkout_date:
                    time_diff = now - room.checkout_date
                    overstay_hours = time_diff.total_seconds() / 3600.0

                    config_params = self.env['ir.config_parameter'].sudo()
                    tinh_phu_troi = config_params.get_param('hotel_management_odoo.tinh_phu_troi_neu_qua_gio_checkin_checkout')
                    is_penalty_enabled = True

                    if tinh_phu_troi:
                        gio_tra_phong = int(config_params.get_param('hotel_management_odoo.gio_tra_phong') or 12)
                        user_tz = pytz.timezone(self.env.user.tz or 'UTC')
                        now_local = pytz.utc.localize(now).astimezone(user_tz)
                        if now_local.hour <= gio_tra_phong:
                            is_penalty_enabled = False
                    
                    if overstay_hours > 1.0 and is_penalty_enabled:
                        fee_ratio = 0.0
                        phutroi_name = ""
                        if overstay_hours <= 3.0:
                            fee_ratio = 0.3
                            phutroi_name = "Phí trả phòng trễ (1-3h)"
                        elif overstay_hours <= 6.0:
                            fee_ratio = 0.5
                            phutroi_name = "Phí trả phòng trễ (4-6h)"
                        else:
                            fee_ratio = 1.0
                            phutroi_name = "Phí trả phòng trễ (>6h)"
                            
                        phutroi_service = PhuTroi.search([('name', '=', phutroi_name)], limit=1)
                        if not phutroi_service:
                            phutroi_service = PhuTroi.create({'name': phutroi_name, 'unit_price': 0.0})
                        
                        base_rate = room.price_unit_dem if room.price_unit_dem > 0 else room.price_unit
                        penalty_amount_late = base_rate * fee_ratio
                        
                        if penalty_amount_late > 0:
                            self.write({
                                'phutroi_line_ids': [(0, 0, {
                                    'phutroi_id': phutroi_service.id,
                                    'uom_qty': 1.0,
                                    'price_unit': penalty_amount_late,
                                })]
                            })
                            has_phutroi = True

            room.room_id.write({
                'status': 'dirty',
            })

        write_vals = {"state": "check_out"}
        if has_phutroi:
            write_vals["need_phutroi"] = True
        self.write(write_vals)
        if not self.is_zns_sent_checkout:
            self._send_zalo_notification('checkout')
            self.is_zns_sent_checkout = True

    def action_cancel(self):
        """Button Cancel Function"""
        for room in self.room_line_ids:
            room.room_id.write({
                'status': 'available',
            })
        self.write({"state": "cancel"})

    def action_done(self):
        """Button Done Function"""
        self.write({"state": "done"})

    def action_maintenance_request(self):
        """
        Function that handles the maintenance request
        """
        room_list = []
        for rec in self.room_line_ids.room_id.ids:
            room_list.append(rec)
        if room_list:
            room_id = self.env['hotel.room'].search([
                ('id', 'in', room_list)])
            self.env['maintenance.request'].sudo().create({
                'date': fields.Date.today(),
                'state': 'draft',
                'type': 'room',
                'room_maintenance_ids': room_id.ids,
            })
            self.maintenance_request_sent = True
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'message': "Maintenance Request Sent Successfully",
                    'next': {'type': 'ir.actions.act_window_close'},
                }
            }
        raise ValidationError(_("Please Enter Room Details"))
