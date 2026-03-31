# -*- coding: utf-8 -*-
import base64
from odoo import http
from odoo.http import request

class HousekeepingController(http.Controller):

    @http.route('/housekeeping', type='http', auth='user', website=False)
    def housekeeping_index(self, **kw):
        """Render the mobile housekeeping list"""
        dirty_rooms = request.env['hotel.room'].sudo().search([
            ('status', '=', 'dirty')
        ], order='floor_id, name')
        
        return request.render('hotel_management_odoo.housekeeping_mobile_template', {
            'dirty_rooms': dirty_rooms,
        })

    @http.route('/housekeeping/mark_clean/<int:room_id>', type='http', auth='user', methods=['POST'], csrf=True)
    def mark_room_clean(self, room_id, **kw):
        """Mark a room as clean and redirect back to list"""
        room = request.env['hotel.room'].sudo().browse(room_id)
        if room.exists() and room.status == 'dirty':
            room.write({'status': 'clean'})
        return request.redirect('/housekeeping')

    @http.route('/housekeeping/upload_image/<int:room_id>', type='http', auth='user', methods=['POST'], csrf=True)
    def upload_room_image(self, room_id, **kw):
        """Upload an image for a room and redirect back to list"""
        room = request.env['hotel.room'].sudo().browse(room_id)
        if room.exists() and 'image' in kw:
            image_file = kw.get('image')
            if image_file:
                image_data = base64.b64encode(image_file.read())
                request.env['hotel.room.cleanup.image'].sudo().create({
                    'room_id': room.id,
                    'image': image_data,
                    'description': kw.get('description', 'Ảnh dọn phòng/báo lỗi')
                })
        return request.redirect('/housekeeping')

    @http.route('/housekeeping/report_broken/<int:equipment_id>', type='http', auth='user', methods=['POST'], csrf=True)
    def report_broken_equipment(self, equipment_id, **kw):
        """Report an equipment as broken and redirect back to list"""
        equipment = request.env['hotel.room.equipment'].sudo().browse(equipment_id)
        if equipment.exists():
            equipment.action_report_broken()
        return request.redirect('/housekeeping')
