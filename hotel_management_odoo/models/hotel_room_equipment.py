# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class HotelRoomEquipment(models.Model):
    _name = 'hotel.room.equipment'
    _description = 'Hotel Room Equipment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Tên thiết bị', required=True, help="Ví dụ: TV Sony 45 inch, Điều hòa Daikin...")
    room_id = fields.Many2one('hotel.room', string='Phòng', ondelete='cascade', required=True)
    category = fields.Selection([
        ('electronics', 'Điện tử (TV, WiFi...)'),
        ('hvac', 'Điện lạnh (Điều hòa, Tủ lạnh...)'),
        ('furniture', 'Nội thất (Giường, Tủ, Bàn...)'),
        ('sanitary', 'Thiết bị vệ sinh'),
        ('other', 'Khác')
    ], string='Phân loại', default='other', tracking=True)
    
    serial_no = fields.Char(string='Số Serial/Model')
    status = fields.Selection([
        ('working', 'Đang hoạt động'),
        ('broken', 'Đang hỏng'),
        ('repairing', 'Đang sửa chữa')
    ], string='Tình trạng', default='working', tracking=True)
    
    note = fields.Text(string='Ghi chú tình trạng')
    last_check_date = fields.Date(string='Ngày kiểm tra gần nhất', default=fields.Date.today)

    def action_report_broken(self):
        """Báo hỏng thiết bị và tự động tạo phiếu sửa chữa"""
        for record in self:
            record.status = 'broken'
            # Tự động tạo bảo trì
            maintenance_vals = {
                'date': fields.Date.today(),
                'type': 'room',
                'state': 'draft',
                'remarks': f"Báo hỏng thiết bị: {record.name} tại {record.room_id.name}",
            }
            # Tìm team kỹ thuật mặc định nếu có
            team = self.env['maintenance.team'].search([], limit=1)
            if team:
                maintenance_vals['team_id'] = team.id
            
            maintenance = self.env['maintenance.request'].create(maintenance_vals)
            # Gán phòng vào maintenance (Many2many)
            maintenance.room_maintenance_ids = [(4, record.room_id.id)]
            
            # Ghi log vào chatter của thiết bị
            record.message_post(body=_(f"Thiết bị được báo hỏng. Phiếu sửa chữa #{maintenance.sequence} đã được tạo."))
