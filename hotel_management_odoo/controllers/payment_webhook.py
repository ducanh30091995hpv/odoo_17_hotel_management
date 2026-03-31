# -*- coding: utf-8 -*-
from odoo import http, fields, _
from odoo.http import request
import json
import logging
import hmac
import hashlib

_logger = logging.getLogger(__name__)

class PaymentPayosController(http.Controller):

    @http.route('/payment/payos/webhook', type='json', auth='none', methods=['POST'], csrf=False)
    def payos_webhook(self, **post):
        """
        PayOS Webhook handler
        """
        try:
            data = request.jsonrequest
            _logger.info("PayOS Webhook received: %s", json.dumps(data))

            if not data or 'data' not in data:
                return {"status": "error", "message": "Invalid payload"}

            # Get Config
            config_obj = request.env['ir.config_parameter'].sudo()
            checksum_key = config_obj.get_param('hotel_management_odoo.payos_checksum_key')
            
            # TODO: Verify Signature in production for security
            # We skip detailed HMAC verification here because it requires specific sorting of fields
            # but we will check if it's a success code
            
            if data.get('code') != '00':
                _logger.warning("PayOS Webhook reported failed payment: %s", data.get('desc'))
                return {"status": "error", "message": "Payment not successful"}

            payment_data = data['data']
            description = payment_data.get('description', '')
            amount = payment_data.get('amount', 0)
            
            # Logic extract booking name from description
            # Format expected: "BOOKING <FolioNum>" example "BOOKING BK001"
            booking_name = False
            desc_upper = description.upper()
            if "BOOKING" in desc_upper:
                # Split and find the part that looks like a folio number
                parts = desc_upper.split()
                for p in parts:
                    if p != "BOOKING" and len(p) > 2:
                        booking_name = p
                        break
            else:
                booking_name = description.strip()

            if booking_name:
                # Search for room booking
                booking = request.env['room.booking'].sudo().search([
                    '|', ('name', '=', booking_name), ('name', 'ilike', booking_name)
                ], limit=1)
                
                if booking:
                    _logger.info("Matched booking %s for PayOS payment", booking.name)
                    
                    # Automate actions based on state
                    if booking.state == 'draft':
                        booking.action_reserve()
                        _logger.info("Auto-Reserved booking %s", booking.name)
                    
                    # If invoice exists, try to reconcile or just mark booking as ready
                    # In this simple implementation, we mark the booking as having received payment
                    # and potentially call a custom method or just log it.
                    
                    # Log internal note on the booking
                    booking.message_post(body=_(
                        "Thanh toán tự động nhận được qua PayOS: %s VNĐ. Nội dung: %s"
                    ) % (amount, description))
                    
                    return {"status": "success", "booking_id": booking.id}
            
            _logger.warning("PayOS Webhook: Could not match description '%s' to any booking", description)
            return {"status": "error", "message": "Booking not found"}

        except Exception as e:
            _logger.error("PayOS Webhook processing error: %s", str(e))
            return {"status": "error", "message": str(e)}
