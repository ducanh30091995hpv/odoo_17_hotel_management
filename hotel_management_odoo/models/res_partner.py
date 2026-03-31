# -*- coding: utf-8 -*-
from odoo import fields, models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    cccd_number = fields.Char(string='Số CCCD', help='Số thẻ Căn cước công dân')
    birthdate_date = fields.Date(string='Ngày sinh')
    gender = fields.Selection([
        ('male', 'Nam'),
        ('female', 'Nữ'),
        ('other', 'Khác')
    ], string='Giới tính')
    cccd_address = fields.Char(string='Địa chỉ trên CCCD')
    date_of_issue = fields.Date(string='Ngày cấp')
