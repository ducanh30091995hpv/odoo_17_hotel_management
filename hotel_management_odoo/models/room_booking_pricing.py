# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, timedelta
import pytz

class RoomBooking(models.Model):
    _inherit = "room.booking"

    @api.depends('room_line_ids.price_total', 'food_order_line_ids.price_total',
                 'vehicle_line_ids.price_total', 'event_line_ids.price_total',
                 'service_line_ids.price_total', 'phutroi_line_ids.price_total', 'phuthu_line_ids.price_total', 'tratruoc')
    def _compute_amount_untaxed(self, is_invoice=False):
        """
        Compute the total amounts of the booking. Optimized multi-record version.
        """
        # PRE-FETCH: Get all move lines for all bookings in self in one query
        all_names = self.mapped('name')
        move_lines_by_ref = {}
        if all_names:
            all_move_lines = self.env['account.move.line'].search_read(
                domain=[('ref', 'in', all_names),
                        ('display_type', '!=', 'payment_term')],
                fields=['name', 'quantity', 'price_unit', 'product_type', 'ref'], )
            for aml in all_move_lines:
                ref = aml['ref']
                if ref not in move_lines_by_ref:
                    move_lines_by_ref[ref] = []
                if 'id' in aml:
                    del aml['id']
                move_lines_by_ref[ref].append(aml)

        # We will return the booking_list for the last record if called functionally
        last_booking_list = []
        
        for rec in self:
            # Initialize totals for this record
            vals = {
                'room': {'untaxed': 0.0, 'tax': 0.0, 'total': 0.0},
                'food': {'untaxed': 0.0, 'tax': 0.0, 'total': 0.0},
                'phuthu': {'untaxed': 0.0, 'tax': 0.0, 'total': 0.0},
                'phutroi': {'untaxed': 0.0, 'tax': 0.0, 'total': 0.0},
                'service': {'untaxed': 0.0, 'tax': 0.0, 'total': 0.0},
                'fleet': {'untaxed': 0.0, 'tax': 0.0, 'total': 0.0},
                'event': {'untaxed': 0.0, 'tax': 0.0, 'total': 0.0},
            }
            
            booking_list = []
            account_move_line = move_lines_by_ref.get(rec.name, [])
            
            # Map of lines to their total fields
            line_mapping = [
                ('room_line_ids', 'room'),
                ('food_order_line_ids', 'food'),
                ('phuthu_line_ids', 'phuthu'),
                ('phutroi_line_ids', 'phutroi'),
                ('service_line_ids', 'service'),
                ('vehicle_line_ids', 'fleet'),
                ('event_line_ids', 'event'),
            ]
            
            for field_name, key in line_mapping:
                lines = getattr(rec, field_name)
                if not lines:
                    continue
                
                vals[key]['untaxed'] = sum(lines.mapped('price_subtotal'))
                vals[key]['tax'] = sum(lines.mapped('price_tax'))
                vals[key]['total'] = sum(lines.mapped('price_total'))
                
                # Special logic for room_line_ids to handle invoice sync and uom
                if field_name == 'room_line_ids':
                    for room_line in lines:
                        booking_dict = {}
                        uom_name = room_line.uom_id.name
                        if uom_name == "Giờ":
                            apply_after_2h = self.env['ir.config_parameter'].sudo().get_param('hotel_management_odoo.tinh_tien_cac_tieng_mac_dinh_ap_dung_sau_2h_dau')
                            price_unit = room_line.price_unit_gio_ht if apply_after_2h else room_line.price_unit_gio
                            booking_dict = {'name': room_line.room_id.name, 'quantity': room_line.uom_qty, 'price_unit': price_unit, 
                                          'product_type': 'room', 'tax_ids': room_line.tax_ids, 'uom_id': room_line.uom_id.id, 'type': uom_name}
                        elif uom_name == "Đêm":
                            booking_dict = {'name': room_line.room_id.name, 'quantity': room_line.uom_qty, 'price_unit': room_line.price_unit_dem,
                                          'product_type': 'room', 'tax_ids': room_line.tax_ids, 'uom_id': room_line.uom_id.id, 'type': uom_name}
                        else:
                            booking_dict = {'name': room_line.room_id.name, 'quantity': room_line.uom_qty, 'price_unit': room_line.price_unit,
                                          'product_type': 'room', 'tax_ids': room_line.tax_ids, 'uom_id': room_line.uom_id.id, 'type': uom_name}
                        
                        # Invoice matching logic
                        if booking_list is not None:
                            if booking_dict not in account_move_line:
                                if not account_move_line:
                                    booking_list.append(booking_dict)
                                else:
                                    match_found = False
                                    for move_rec in account_move_line:
                                        if move_rec['product_type'] == 'room' and booking_dict['name'] == move_rec['name'] and booking_dict['price_unit'] == move_rec['price_unit'] and booking_dict['quantity'] != move_rec['quantity']:
                                            booking_list.append({'name': room_line.room_id.name, "quantity": booking_dict['quantity'] - move_rec['quantity'], 
                                                               "price_unit": room_line.price_unit, "product_type": 'room', 'uom_id': room_line.uom_id.id, 
                                                               'tax_ids': room_line.tax_ids, 'type': uom_name})
                                            match_found = True
                                            break
                                    if not match_found:
                                        booking_list.append(booking_dict)
            
            # Final assignment for the record
            rec.amount_untaxed_room = vals['room']['untaxed']
            rec.amount_untaxed_food = vals['food']['untaxed']
            rec.amount_untaxed_phuthu = vals['phuthu']['untaxed']
            rec.amount_untaxed_phutroi = vals['phutroi']['untaxed']
            rec.amount_untaxed_service = vals['service']['untaxed']
            rec.amount_untaxed_fleet = vals['fleet']['untaxed']
            rec.amount_untaxed_event = vals['event']['untaxed']
            
            rec.amount_taxed_room = vals['room']['tax']
            rec.amount_taxed_food = vals['food']['tax']
            rec.amount_taxed_event = vals['event']['tax']
            rec.amount_taxed_service = vals['service']['tax']
            rec.amount_taxed_phutroi = vals['phutroi']['tax']
            rec.amount_taxed_phuthu = vals['phuthu']['tax']
            rec.amount_taxed_fleet = vals['fleet']['tax']
            
            rec.amount_total_room = vals['room']['total']
            rec.amount_total_food = vals['food']['total']
            rec.amount_total_event = vals['event']['total']
            rec.amount_total_service = vals['service']['total']
            rec.amount_total_phutroi = vals['phutroi']['total']
            rec.amount_total_phuthu = vals['phuthu']['total']
            rec.amount_total_fleet = vals['fleet']['total']
            
            rec.amount_untaxed = sum(v['untaxed'] for v in vals.values())
            rec.amount_tax = sum(v['tax'] for v in vals.values())
            rec.amount_total = sum(v['total'] for v in vals.values()) - rec.tratruoc
            
            last_booking_list = booking_list

        if is_invoice:
            return last_booking_list

    @api.onchange('need_service')
    def _onchange_need_service(self):
        """Unlink Service Booking Line if Need Service is False"""
        if not self.need_service and self.service_line_ids:
            for serv in self.service_line_ids:
                serv.unlink()

    @api.onchange('need_phutroi')
    def _onchange_need_phutroi(self):
        """Unlink Service Booking Line if Need Service is False"""
        if not self.need_phutroi and self.phutroi_line_ids:
            for serv in self.phutroi_line_ids:
                serv.unlink()

    @api.onchange('need_phuthu')
    def _onchange_need_phuthu(self):
        """Unlink Service Booking Line if Need Service is False"""
        if not self.need_phuthu and self.phuthu_line_ids:
            for serv in self.phuthu_line_ids:
                serv.unlink()

    @api.onchange('need_fleet')
    def _onchange_need_fleet(self):
        """Unlink Fleet Booking Line if Need Fleet is False"""
        if not self.need_fleet:
            if self.vehicle_line_ids:
                for fleet in self.vehicle_line_ids:
                    fleet.unlink()

    @api.onchange('need_event')
    def _onchange_need_event(self):
        """Unlink Event Booking Line if Need Event is False"""
        if not self.need_event:
            if self.event_line_ids:
                for event in self.event_line_ids:
                    event.unlink()

    @api.onchange('food_order_line_ids', 'room_line_ids',
                  'service_line_ids', 'phutroi_line_ids', 'phuthu_line_ids', 'vehicle_line_ids', 'event_line_ids')
    def _onchange_room_line_ids(self):
        """Invokes the Compute amounts function"""
        self._compute_amount_untaxed()
        self.invoice_button_visible = False
