# -*- coding: utf-8 -*-
from odoo import fields, models

class HotelRoomPriceSpecial(models.Model):
    _name = 'hotel.room.price.special'
    _description = 'Special Room Price'

    room_id = fields.Many2one('hotel.room', string='Phòng', ondelete='cascade', required=True)
    type = fields.Selection([
        ('weekend', 'Ngày cuối tuần'),
        ('holiday', 'Ngày lễ')
    ], string='Loại', required=True, default='weekend')
    
    day_of_week = fields.Selection([
        ('0', 'Thứ 2'),
        ('1', 'Thứ 3'),
        ('2', 'Thứ 4'),
        ('3', 'Thứ 5'),
        ('4', 'Thứ 6'),
        ('5', 'Thứ 7'),
        ('6', 'Chủ nhật')
    ], string='Thứ trong tuần')
    
    holiday_id = fields.Many2one('hotel.holiday', string='Ngày lễ')
    
    calculation_method = fields.Selection([
        ('fixed', 'Giá cố định'),
        ('add_amount', 'Cộng thêm tiền'),
        ('add_percent', 'Cộng thêm %')
    ], string='Phương thức tính giá', required=True, default='fixed')

    fixed_amount_to_add = fields.Float(string='Số tiền cộng thêm (VNĐ)')
    percent_to_add = fields.Float(string='Phần trăm cộng thêm (%)')
    
    # These are only used if calculation_method == 'fixed'
    price_unit = fields.Float(string='Giá ngày', digits='Product Price')
    price_unit_dem = fields.Float(string='Giá qua đêm', digits='Product Price')
    price_unit_gio = fields.Float(string='Giá giờ', digits='Product Price')
