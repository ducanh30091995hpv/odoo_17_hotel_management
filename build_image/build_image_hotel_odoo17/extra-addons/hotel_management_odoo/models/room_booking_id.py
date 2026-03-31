# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models, _

class RoomBooking(models.Model):
    _inherit = "room.booking"

    def action_scan_cccd(self):
        """Returns a client action to open the camera and scan CCCD"""
        return {
            'type': 'ir.actions.client',
            'tag': 'cccd_scanner_action',
            'params': {
                'res_id': self.id,
                'model': self._name,
            }
        }

    @api.model
    def process_cccd_data(self, booking_id, qr_data):
        """
        Parses the QR string from Vietnamese CCCD and updates the partner.
        Format: CCCD_ID|Old_ID|Full_Name|DOB|Gender|Address|IssueDay
        """
        if not qr_data:
            return False
            
        parts = qr_data.split('|')
        if len(parts) < 6:
            return {'error': 'Định dạng mã QR không hợp lệ'}

        cccd_no = parts[0]
        full_name = parts[2]
        dob_str = parts[3] # DDMMYYYY
        gender_str = parts[4]
        address = parts[5]
        
        dob = False
        try:
            if len(dob_str) == 8:
                dob = datetime.strptime(dob_str, '%d%m%Y').date()
        except:
            pass

        gender = 'other'
        if gender_str.lower() in ['nam', 'male']:
            gender = 'male'
        elif gender_str.lower() in ['nữ', 'female']:
            gender = 'female'

        booking = self.browse(booking_id)
        if booking.exists():
            partner = booking.partner_id
            vals = {
                'name': full_name,
                'cccd_number': cccd_no,
                'gender': gender,
                'cccd_address': address,
            }
            if dob:
                vals['birthdate_date'] = dob
            
            partner.write(vals)
            return {'success': True, 'partner_name': full_name}
            
        return False
