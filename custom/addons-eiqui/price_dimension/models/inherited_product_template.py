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

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
from .consts import PRICE_TYPES


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_price_area_min_width = fields.Float(string="Min. Width",
                                             default=0.0,
                                             digits=dp.get_precision('Product Price'))
    sale_price_area_max_width = fields.Float(string="Max. Width",
                                             default=0.0,
                                             digits=dp.get_precision('Product Price'))
    sale_price_area_min_height = fields.Float(string="Min. Height",
                                              default=0.0,
                                              digits=dp.get_precision('Product Price'))
    sale_price_area_max_height = fields.Float(string="Max. Height",
                                              default=0.0,
                                              digits=dp.get_precision('Product Price'))
    sale_min_price_area = fields.Monetary("Min. Price")
    height_uom = fields.Many2one('product.uom',string='Height UOM')
    width_uom = fields.Many2one('product.uom',string='Width UOM')


    sale_price_type = fields.Selection(
            PRICE_TYPES,
            string='Sale Price Type',
            required=True,
            default='standard',
        )
    sale_prices_table = fields.One2many('product.prices_table',
                                        'sale_product_tmpl_id',
                                        string="Sale Prices Table")

    def get_sale_price(self):
        origin_width = self._context and self._context.get('width') or False
        origin_height = self.context and self._context.get('height') or False

        result = False
        if origin_width:
            product_prices_table_obj = self.env['product.prices_table']
            origin_width = self.origin_normalize_sale_width_value(self.id, origin_width)
            if self.sale_price_type == 'table_2d':
                origin_height = self.origin_normalize_sale_height_value(self.id, origin_height)
                res = product_prices_table_obj.search([
                    ('sale_product_tmpl_id', '=', self.product_tmpl_id.id),
                    ('pos_x', '=', origin_width),
                    ('pos_y', '=', origin_height)
                ], limit=1)
                result = res and res.value or False
            elif self.sale_price_type == 'table_1d':
                res = product_prices_table_obj.search([
                    ('sale_product_tmpl_id', '=', self.product_tmpl_id.id),
                    ('pos_x', '=', origin_width)
                ], limit=1)
                result = res and res.value or False
            elif self.sale_price_type == 'area':
                result = self.list_price * origin_width * origin_height
                result = max(self.sale_min_price_area, result)
        if not result:
            result = self.list_price
        return result

    @api.model
    def _price_get(self, products, ptype='list_price'):
        if context is None:
            context = {}

        res = super(ProductTemplate, self)._price_get(products,
                                                       ptype=ptype)
        product_uom_obj = self.env['product.uom']
        for product in products:
            # standard_price field can only be seen by users in base.group_user
            # Thus, in order to compute the sale price from the cost for users not in this group
            # We fetch the standard price as the superuser
            if ptype != 'standard_price':
                res[product.id] = product.get_sale_price()
            else:
                company_id = self._context.get('force_company') or \
                    product.env.user.company_id.id
                product = product.with_context(force_company=company_id)
                res[product.id] = product.sudo()[ptype]
#TODO - Revisar para la refactorizacion
            #~ if ptype == 'list_price' and product._name == "product.product":
                #~ res[product.id] += (res[product.id] * product.price_extra_perc) / 100.0
                #~ res[product.id] += product.price_extra
            if 'uom' in context:
                uom = product.uom_id
                res[product.id] = product_uom_obj._compute_price(
                        uom.id, res[product.id], context['uom'])
            # Convert from current user company currency to asked one
            if self._context.get('currency_id'):
                # Take current user company currency.
                # This is right cause a field cannot be in more than one currency
                res[product.id] = self.env['res.currency'].compute(
                    product.currency_id.id,
                    self._context.get('currency_id'),
                    res[product.id])
        return res

    def origin_check_sale_dim_values(self, width, height):
        if self.sale_price_type in ['table_1d', 'table_2d']:
            product_prices_table_obj = self.env['product.prices_table']
            norm_width = self.origin_normalize_sale_width_value(width)
            if self.sale_price_type == 'table_2d':
                norm_height = self.origin_normalize_sale_height_value(height)
                return product_prices_table_obj.search_count([
                    ('sale_product_tmpl_id', '=', self.id),
                    ('pos_x', '=', norm_width),
                    ('pos_y', '=', norm_height),
                    ('value', '!=', 0)]) > 0
            return product_prices_table_obj.search_count([
                ('sale_product_tmpl_id', '=', self.id),
                ('pos_x', '=', norm_width),
                ('value', '!=', 0)]) > 0
        elif self.sale_price_type == 'area':
            return width >= self.sale_price_area_min_width and \
                width <= self.sale_price_area_max_width and \
                height >= self.sale_price_area_min_height and \
                height <= self.sale_price_area_max_height
        return True

    def origin_normalize_sale_width_value(self, width):
        headers = self.get_sale_price_table_headers()
        norm_val = width
        for index in range(len(headers[self.id]['x'])-1):
            if width > headers[self.id]['x'][index] and \
                width <= headers[self.id]['x'][index+1]:
                norm_val = headers[self.id]['x'][index+1]
        return norm_val

    def origin_normalize_sale_height_value(self, height):
        headers = self.get_sale_price_table_headers()
        norm_val = height
        for index in range(len(headers[self.id]['y'])-1):
            if height > headers[self.id]['y'][index] and \
                    height <= headers[self.id]['y'][index+1]:
                norm_val = headers[self.id]['y'][index+1]
        return norm_val

    def get_sale_price_table_headers(self):
        result = {self.id: {'x': [0], 'y': [0]}}
        for rec in self.sale_prices_table:
            result[self.id]['x'].append(rec.pos_x)
            result[self.id]['y'].append(rec.pos_y)
        result[self.id].update({
            'x': sorted(list(set(result[self.id]['x']))),
            'y': sorted(list(set(result[self.id]['y'])))
        })
        return result
