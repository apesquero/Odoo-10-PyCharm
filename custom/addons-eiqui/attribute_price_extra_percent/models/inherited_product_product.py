# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017 Solucións Aloxa S.L. <info@aloxa.eu>
#                        Alexandre Díaz <alex@aloxa.eu>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import odoo
from odoo import models, fields, api, tools, SUPERUSER_ID
import odoo.addons.decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.depends('attribute_value_ids.price_ids.price_extra',
                 'attribute_value_ids.price_ids.product_tmpl_id')
    def _compute_product_price_extra(self):
        super(ProductProduct, self)._compute_product_price_extra()
        for product in self:
            price_extra = 0.0
            for variant_id in product.attribute_value_ids:
                if variant_id.price_extra_type != 'standard':
                    continue
                for price_id in variant_id.price_ids:
                    if price_id.product_tmpl_id.id == product.product_tmpl_id.id:
                        price_extra += price_id.price_extra
            product.price_extra = price_extra

    @api.depends('list_price', 'price_extra')
    def _compute_product_lst_price(self):
        res = super(ProductProduct, self)._compute_product_lst_price()
        product_uom_obj = self.env['product.uom']
        to_uom = False
        if 'uom' in self._context:
            to_uom = self.env['product.uom'].browse([self._context['uom']])
        for product in self:
            if to_uom:
                price = product.uom_id._compute_price(product.list_price, to_uom)
            else:
                price = product.list_price
            price += (price * product.price_extra_perc) / 100.0
            price += product.price_extra
            product.lst_price = price

    def _set_product_lst_price(self):
        super(ProductProduct, self)._set_product_lst_price()
        product_uom_obj = self.pool.get('product.uom')
        for product in self:
            if self._context.get('uom'):
                value = product_uom_obj.browse(
                    self._context['uom'])._compute_price(
                    product.lst_price, product.uom_id)
            else:
                value = product.lst_price
            value -= (product.get_sale_price() * \
                product.price_extra_perc) / 100.0
            value -= product.price_extra
            product.write({'list_price': value})

    def _compute_price_extra_percentage(self):
        for product in self:
            price_extra = 0.0
            for variant_id in product.attribute_value_ids:
                if variant_id.price_extra_type != 'percentage':
                    continue
                for price_id in variant_id.price_ids:
                    if price_id.product_tmpl_id.id == product.product_tmpl_id.id:
                        price_extra += price_id.price_extra
            product.price_extra_perc = price_extra

    price_extra_perc = fields.Float(compute=_compute_price_extra_percentage,
                                    string='Variant Extra Price Percentage',
                                    help="This is the percentage of the extra price of all attributes",
                                    digits=dp.get_precision('Product Price'))
