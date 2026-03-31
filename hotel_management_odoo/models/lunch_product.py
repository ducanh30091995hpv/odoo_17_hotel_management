# -*- coding: utf-8 -*-
from odoo import fields, models

class LunchProduct(models.Model):
    _inherit = 'lunch.product'

    product_id = fields.Many2one(
        'product.product', 
        string='Sản phẩm trong Kho',
        help='Liên kết món ăn này với một sản phẩm trong Kho để theo dõi tồn kho.'
    )
