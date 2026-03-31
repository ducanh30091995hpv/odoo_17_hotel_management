# -*- coding: utf-8 -*-
import logging
import requests
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class RoomBooking(models.Model):
    _inherit = "room.booking"

    is_zns_sent_reserved = fields.Boolean(copy=False, string="ZNS Reserved Sent")
    is_zns_sent_checkout = fields.Boolean(copy=False, string="ZNS Checkout Sent")

    def _send_zalo_notification(self, notification_type):
        """Helper to send ZNS notification via Zalo API"""
        config_obj = self.env['ir.config_parameter'].sudo()
        enable = config_obj.get_param('hotel_management_odoo.enable_zalo_notification')
        if not enable:
            return False

        oa_id = config_obj.get_param('hotel_management_odoo.zalo_oa_id')
        access_token = config_obj.get_param('hotel_management_odoo.zalo_access_token')
        
        template_id = False
        if notification_type == 'reserved':
            template_id = config_obj.get_param('hotel_management_odoo.zalo_template_reserved')
        elif notification_type == 'checkout':
            template_id = config_obj.get_param('hotel_management_odoo.zalo_template_checkout')
            
        if not template_id or not access_token:
            return False

        phone = self.partner_id.mobile or self.partner_id.phone
        if not phone:
            return False

        # Format phone number for Zalo (remove leading 0 and add 84)
        if phone.startswith('0'):
            phone = '84' + phone[1:]
        elif not phone.startswith('84'):
            phone = '84' + phone

        # Prepare payload for ZNS
        payload = {
            "phone": phone,
            "template_id": template_id,
            "template_data": {
                "customer_name": self.partner_id.name,
                "order_id": self.name,
                "hotel_name": self.company_id.name,
                "checkin_date": self.checkin_date.strftime('%d/%m/%Y %H:%M') if self.checkin_date else '',
                "checkout_date": self.checkout_date.strftime('%d/%m/%Y %H:%M') if self.checkout_date else '',
            },
            "tracking_id": f"{self.name}_{notification_type}"
        }

        # Mock Sending (Actual API call)
        try:
            # url = "https://openapi.zalo.me/v2.0/oa/message/zns"
            # headers = {"Content-Type": "application/json", "access_token": access_token}
            # response = requests.post(url, headers=headers, json=payload, timeout=10)
            # return response.json()
            _logger.info(f"SIEMENS: Sending Zalo ZNS {notification_type} to {phone}: {payload}")
            return True
        except Exception as e:
            _logger.error(f"Error sending Zalo message: {str(e)}")
            return False
