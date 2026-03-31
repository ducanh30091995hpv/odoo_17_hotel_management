# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class EarlyCheckoutWizard(models.TransientModel):
    _name = 'early.checkout.wizard'
    _description = 'Early Checkout Policy Configuration'

    booking_id = fields.Many2one('room.booking', string="Booking", required=True)
    policy = fields.Selection([
        ('actual', 'Tính tiền thực tế (Giảm thời gian đặt)'),
        ('full', 'Thu đủ tiền như đã đặt (Thời gian không đổi)'),
        ('penalty', 'Tính tiền thực tế + Thu tiền phạt')
    ], string='Chính sách trả phòng', required=True, default='actual')
    penalty_amount = fields.Float(string='Số tiền phạt thêm')

    def action_confirm(self):
        self.ensure_one()
        return self.booking_id.with_context(
            early_checkout_policy=self.policy,
            early_checkout_penalty=self.penalty_amount
        )._process_checkout()
