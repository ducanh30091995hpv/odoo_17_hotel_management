# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Vishnu K P (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import api, fields, models, tools


class FoodBookingLine(models.Model):
    """Model that handles the food booking"""
    _name = "food.booking.line"
    _description = "Hotel Food Line"
    _rec_name = 'food_id'

    @tools.ormcache()
    def _get_default_uom_id(self):
        """Method for getting the default uom id"""
        return self.env.ref('uom.product_uom_unit')

    booking_id = fields.Many2one("room.booking", string="Booking",
                                 help="Shows the room Booking",
                                 ondelete="cascade")
    food_id = fields.Many2one('lunch.product', string="Product",
                              help="Indicates the Food Product")
    description = fields.Char(string='Description',
                              help="Description of Food Product",
                              related='food_id.display_name')
    uom_qty = fields.Float(string="Qty", default=1,
                           help="The quantity converted into the UoM used by "
                                "the product")
    uom_id = fields.Many2one('uom.uom', readonly=True,
                             string="Unit of Measure",
                             default=_get_default_uom_id, help="This will set "
                                                               "the unit of"
                                                               " measure used")
    price_unit = fields.Float(related='food_id.price', string='Price',
                              digits='Product Price',
                              help="The price of the selected food item.")
    tax_ids = fields.Many2many('account.tax',
                               'hotel_food_order_line_taxes_rel',
                               'food_id', 'tax_id',
                               string='Taxes',
                               help="Default taxes used when selling the food"
                                    " products.",
                               domain=[('type_tax_use', '=', 'sale')])
    currency_id = fields.Many2one(related='booking_id.pricelist_id.currency_id'
                                  , string="Currency",
                                  help='The currency used')
    price_subtotal = fields.Float(string="Subtotal",
                                  compute='_compute_price_subtotal',
                                  help="Total Price Excluding Tax",
                                  store=True)
    price_tax = fields.Float(string="Total Tax",
                             compute='_compute_price_subtotal',
                             help="Tax Amount",
                             store=True)
    price_total = fields.Float(string="Total",
                               compute='_compute_price_subtotal',
                               help="Total Price Including Tax",
                               store=True)
    state = fields.Selection(related='booking_id.state',
                             string="Order Status",
                             help=" Status of the Order",
                             copy=False)

    @api.depends('uom_qty', 'price_unit', 'tax_ids')
    def _compute_price_subtotal(self):
        """Compute the amounts of the room booking line."""
        for line in self:
            tax_results = self.env['account.tax']._compute_taxes(
                [line._convert_to_tax_base_line_dict()])
            totals = list(tax_results['totals'].values())[0]
            amount_untaxed = totals['amount_untaxed']
            amount_tax = totals['amount_tax']
            line.update({
                'price_subtotal': amount_untaxed,
                'price_tax': amount_tax,
                'price_total': amount_untaxed + amount_tax,
            })
            if self.env.context.get('import_file',
                                    False) and not self.env.user. \
                    user_has_groups('account.group_account_manager'):
                line.tax_id.invalidate_recordset(
                    ['invoice_repartition_line_ids'])

    def _convert_to_tax_base_line_dict(self):
        """ Convert the current record to a dictionary in order to use the
        generic taxes computation method
        defined on account.tax.
        :return: A python dictionary."""
        self.ensure_one()
        return self.env['account.tax']._convert_to_tax_base_line_dict(
            self,
            partner=self.booking_id.partner_id,
            currency=self.currency_id,
            taxes=self.tax_ids if self.booking_id.apdungthue else self.env['account.tax'],
            price_unit=self.price_unit,
            quantity=self.uom_qty,
            price_subtotal=self.price_subtotal, )

    def _action_stock_move(self, qty_to_move, move_type='outgoing'):
        """Logic to decrease/increase stock if the inventory module is installed."""
        if 'stock.move' not in self.env:
            return
            
        for line in self:
            if line.food_id.product_id and line.food_id.product_id.type in ['consu', 'product']:
                if qty_to_move == 0:
                    continue
                
                # Determine locations based on move type
                if move_type == 'outgoing':
                    location_id = self.env.ref('stock.stock_location_stock').id
                    location_dest_id = self.env.ref('stock.stock_location_customers').id
                    move_name = f"F&B Xuất: {line.food_id.name} ({line.booking_id.name})"
                else:
                    location_id = self.env.ref('stock.stock_location_customers').id
                    location_dest_id = self.env.ref('stock.stock_location_stock').id
                    move_name = f"F&B Nhập lại: {line.food_id.name} ({line.booking_id.name})"

                move_vals = {
                    'name': move_name,
                    'product_id': line.food_id.product_id.id,
                    'product_uom_qty': abs(qty_to_move),
                    'product_uom': line.uom_id.id or line.food_id.product_id.uom_id.id,
                    'location_id': location_id,
                    'location_dest_id': location_dest_id,
                    'state': 'draft',
                }
                move = self.env['stock.move'].create(move_vals)
                move._action_confirm()
                move._action_assign()
                if move.state == 'assigned':
                    move._action_done()

    def write(self, vals):
        if 'uom_qty' in vals:
            for line in self:
                if line.booking_id.state in ['check_in', 'done'] and line.food_id.product_id:
                    diff = vals['uom_qty'] - line.uom_qty
                    if diff > 0:
                        line._action_stock_move(diff, 'outgoing')
                    elif diff < 0:
                        line._action_stock_move(diff, 'incoming')
        res = super(FoodBookingLine, self).write(vals)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        lines = super(FoodBookingLine, self).create(vals_list)
        for line in lines:
            if line.booking_id.state in ['check_in', 'done'] and line.food_id.product_id:
                line._action_stock_move(line.uom_qty, 'outgoing')
        return lines

    def unlink(self):
        """When deleting a line, return the stock if it was already deducted."""
        for line in self:
            if line.booking_id.state in ['check_in', 'done'] and line.food_id.product_id:
                line._action_stock_move(line.uom_qty, 'incoming')
        return super(FoodBookingLine, self).unlink()

    def search_food_orders(self):
        """Returns list of food orders"""
        return (self.search([]).filtered(lambda r: r.booking_id.state not in [
            'check_out', 'cancel', 'done']).ids)

