# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def origin_check_sale_dim_values(self, width, height):
        if self.sale_price_type in ['table_1d', 'table_2d']:
            product_prices_table_obj = self.env['product.prices_table']
            norm_width = self.origin_normalize_sale_width_value(width)
            if self.sale_price_type == 'table_2d':
                norm_height = self.origin_normalize_sale_height_value(height)
                return product_prices_table_obj.search_count([
                    ('sale_product_tmpl_id', '=', self.product_tmpl_id.id),
                    ('pos_x', '=', norm_width),
                    ('pos_y', '=', norm_height),
                    ('value', '!=', 0)]) > 0
            return product_prices_table_obj.search_count([
                ('sale_product_tmpl_id', '=', self.product_tmpl_id.id),
                ('pos_x', '=', norm_width),
                ('value', '!=', 0)]) > 0
        elif self.sale_price_type == 'area':
            return width >= self.min_width_area and \
                   width <= self.max_width_area and \
                   height >= self.min_height_area and \
                   height <= self.max_height_area
        return True

    @api.model
    def origin_normalize_sale_width_value(self, width):
        headers = self.get_sale_price_table_headers()
        norm_val = width
        for index in range(len(headers['x']) - 1):
            if headers['x'][0] == 0 and index == 0:
                if width >= headers['x'][index + 1] and \
                                width <= headers['x'][index + 1]:
                    norm_val = headers['x'][index + 2]
            else:
                if width > headers['x'][index] and \
                                width <= headers['x'][index + 1]:
                    norm_val = headers['x'][index + 1]
        return norm_val

    @api.model
    def origin_normalize_sale_height_value(self, height):
        headers = self.get_sale_price_table_headers()
        norm_val = height
        for index in range(len(headers['y']) - 1):
            if headers['y'][0] == 0 and index == 0:
                if height >= headers['y'][index + 1] and \
                                height <= headers['y'][index + 1]:
                    norm_val = headers['y'][index + 2]
            else:
                if height > headers['y'][index] and \
                            height <= headers['y'][index + 1]:
                    norm_val = headers['y'][index + 1]
        return norm_val

    @api.model
    def get_sale_price_table_headers(self):
        result = {'x': [0], 'y': [0]}
        for rec in self.sale_prices_table:
            result['x'].append(rec.pos_x)
            result['y'].append(rec.pos_y)
        result.update({
            'x': sorted(list(set(result['x']))),
            'y': sorted(list(set(result['y'])))
        })
        return result

    @api.model
    def get_sale_price(self):
        origin_width = self._context.get('width', False)
        origin_height = self._context.get('height', False)

        result = False
        if origin_width:
            product_prices_table_obj = self.env['product.prices_table']
            origin_width = self.origin_normalize_sale_width_value(origin_width)
            if self.sale_price_type == 'table_2d':
                origin_height = self.origin_normalize_sale_height_value(origin_height)
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
                # Unit conversion created
                origin_width = (self.area_uom.factor * origin_width) / self.width_uom.factor
                origin_height = (self.area_uom.factor * origin_height) / self.height_uom.factor

                result = self.list_price * origin_width * origin_height
                result = max(self.min_price_area, result)
        if not result:
            result = self.list_price
        return result

    @api.depends('list_price')
    def _compute_product_lst_price(self):
        super(ProductProduct, self)._compute_product_lst_price()
        to_uom = None
        if 'uom' in self._context:
            to_uom = self.env['product.uom'].browse([self._context['uom']])

        for product in self:
            if to_uom:
                list_price = product.uom_id._compute_price(product.get_sale_price(), to_uom)
                price_extra = product.uom_id._compute_price(product.price_extra, to_uom)
            else:
                list_price = product.list_price
            product.lst_price = list_price + price_extra
            product.list_price = product.lst_price
