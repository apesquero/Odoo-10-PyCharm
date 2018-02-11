# -*- coding: utf-8 -*-

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


class product_supplier_info(models.Model):
    _inherit = 'product.supplierinfo'

    price_area_min_width = fields.Float(string="Min. Width", default=0.0, digits=dp.get_precision('Product Price'))
    price_area_max_width = fields.Float(string="Max. Width", default=0.0, digits=dp.get_precision('Product Price'))
    price_area_min_height = fields.Float(string="Min. Height", default=0.0, digits=dp.get_precision('Product Price'))
    price_area_max_height = fields.Float(string="Max. Height", default=0.0, digits=dp.get_precision('Product Price'))
    min_price_area = fields.Monetary('Min. Price')

    price_type = fields.Selection([('standard', 'Standard'),
                                   ('table_1d', '1D Table'),
                                   ('table_2d', '2D Table'),
                                   ('area', 'Area')],
                                  string='Supplier Price Type',
                                  required=True,
                                  default='standard',
                                  )
    supplier_prices_table = fields.One2many('product.prices_table',
                                   'supplier_product_id',
                                   string="Supplier Prices Table")

    # @api.depends('attribute_value_ids')
    # def _compute_price_extra_percentage(self):
    #     product_id = self.env.context and self.env.context.get('product_id') or False
    #     for supplier in self:
    #         price_extra = 0.0
    #         for variant_id in supplier.attribute_value_ids:
    #             if product_id and variant_id.value not in product_id.attribute_value_ids:
    #                 continue
    #             if variant_id.price_extra_type != 'percentage' or supplier.id != variant_id.supplierinfo_id.id:
    #                 continue
    #             price_extra += variant_id.price_extra
    #         supplier.price_extra_perc = price_extra
    #
    # @api.depends('attribute_value_ids')
    # def _compute_price_extra(self):
    #     product_id = self.env.context and self.env.context.get('product_id') or False
    #     for supplier in self:
    #         price_extra = 0.0
    #         for variant_id in supplier.attribute_value_ids:
    #             if product_id and variant_id.value not in product_id.attribute_value_ids:
    #                 continue
    #             if variant_id.price_extra_type != 'standard' or supplier.id != variant_id.supplierinfo_id.id:
    #                 continue
    #             price_extra += variant_id.price_extra
    #         supplier.price_extra = price_extra
    #


    # attribute_value_ids = fields.One2many(
    #     comodel_name='supplier.attribute.value',
    #     inverse_name='supplierinfo_id'
    # )
    #
    # price_extra = fields.Float(compute='_compute_price_extra', string='Variant Extra Price', help="This is the sum of the extra price of all attributes", digits=dp.get_precision('Product Price'))
    # price_extra_perc = fields.Float(compute='_compute_price_extra_percentage', string='Variant Extra Price Percentage', help="This is the percentage of the extra price of all attributes", digits=dp.get_precision('Product Price'))
    #
    def get_price_table_headers(self):
        result = {'x': [0], 'y': [0]}
        for rec in self.prices_table:
            result['x'].append(rec.pos_x)
            result['y'].append(rec.pos_y)
        result.update({
            'x': sorted(list(set(result['x']))),
            'y': sorted(list(set(result['y'])))
        })
        return result

    def origin_check_dim_values(self, width, height):
        if self.price_type in ['table_1d', 'table_2d']:
            product_prices_table_obj = self.env['product.prices_table']
            norm_width = self.origin_normalize_width_value(width)
            if self.price_type == 'table_2d':
                norm_height = self.origin_normalize_height_value(height)
                return product_prices_table_obj.search_count([('supplier_product_id', '=', self.id),
                                                              ('pos_x', '=', norm_width),
                                                              ('pos_y', '=', norm_height),
                                                              ('value', '!=', 0)]) > 0
            return product_prices_table_obj.search_count([('supplier_product_id', '=', self.id),
                                                          ('pos_x', '=', norm_width),
                                                          ('value', '!=', 0)]) > 0
        elif self.price_type == 'area':
            return width >= self.price_area_min_width and width <= self.price_area_max_width and height >= self.price_area_min_height and height <= self.price_area_max_height
        return True

    def origin_normalize_width_value(self, width):
        headers = self.get_price_table_headers()
        norm_val = width
        for index in range(len(headers['x'])-1):
            if width > headers['x'][index] and width <= headers['x'][index+1]:
                norm_val = headers['x'][index+1]
        return norm_val

    def origin_normalize_height_value(self, height):
        headers = self.get_price_table_headers()
        norm_val = height
        for index in range(len(headers['y'])-1):
            if height > headers['y'][index] and height <= headers['y'][index+1]:
                norm_val = headers['y'][index+1]
        return norm_val

    @api.depends('price')
    def get_supplier_price(self):
        origin_width = self.env.context and self.env.context.get('width') or False
        origin_height = self.env.context and self.env.context.get('height') or False
        product_id = self.env.context and self.env.context.get('product_id') or False

        result = False
        if origin_width:
            product_prices_table_obj = self.env['product.prices_table']
            origin_width = self.origin_normalize_width_value(origin_width)
            if self.price_type == 'table_2d':
                origin_height = self.origin_normalize_height_value(origin_height)
                res = product_prices_table_obj.search([
                    ('supplier_product_id', '=', self.id),
                    ('pos_x', '=', origin_width),
                    ('pos_y', '=', origin_height)
                ], limit=1)
                result = res and res.value or False
            elif self.price_type == 'table_1d':
                res = product_prices_table_obj.search([
                    ('supplier_product_id', '=', self.id),
                    ('pos_x', '=', origin_width)
                ], limit=1)
                result = res and res.value or False
            elif self.price_type == 'area':
                result = self.price * origin_width * origin_height
                result = max(self.min_price_area, result)
        if not result:
            result = self.price
        # result += (result * self.with_context(product_id=product_id).price_extra_perc) /100
        # result += self.with_context(product_id=product_id).price_extra
        return result

    # @api.multi
    # def action_open_value_extras(self):
    #     self.ensure_one()
    #     extra_ds = self.env['supplier.attribute.value']
    #     for line in self.product_tmpl_id.attribute_line_ids:
    #         for value in line.value_ids:
    #             extra = extra_ds.search([('supplierinfo_id', '=', self.id),
    #                                      ('value', '=', value.id)])
    #             if not extra:
    #                 extra = extra_ds.create({
    #                     'supplierinfo_id': self.id,
    #                     'value': value.id,
    #                 })
    #             extra_ds |= extra
    #     all_supplierinfo_extra = extra_ds.search([
    #         ('supplierinfo_id', '=', self.id)
    #     ])
    #     remove_extra = all_supplierinfo_extra - extra_ds
    #     remove_extra.unlink()
    #     action = self.env.ref('price_dimension.supplier_attribute_value_action').read()[0]
    #     return action
