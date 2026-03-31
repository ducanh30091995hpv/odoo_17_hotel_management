# -*- coding: utf-8 -*-
from odoo import fields, models

class HotelHoliday(models.Model):
    _name = 'hotel.holiday'
    _description = 'Hotel Holiday'

    name = fields.Char(string='Tên ngày lễ', required=True)
    date_from = fields.Date(string='Từ ngày', required=True)
    date_to = fields.Date(string='Đến ngày', required=True)
    active = fields.Boolean(default=True)
