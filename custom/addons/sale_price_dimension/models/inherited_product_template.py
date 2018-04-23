# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    height_uom = fields.Many2one('product.uom', string='Height UOM')
    width_uom = fields.Many2one('product.uom', string='Width UOM')

    sale_price_type = fields.Selection([
        ('standard', 'Standard'),
        ('table_1d', '1D Table'),
        ('table_2d', '2D Table'),
        ('area', 'Area')],
        string='Sale Price Type',
        required=True,
        default='standard',
    )
    sale_prices_table = fields.One2many('product.prices_table',
                                        'sale_product_tmpl_id',
                                        string="Sale Prices Table")

    sale_prices_area = fields.One2many('product.prices_area',
                                       'sale_area_tmpl_id',
                                       string="Sale Prices Area")

    min_width_area = fields.Float(related='sale_prices_area.min_width_area')
    max_width_area = fields.Float(related='sale_prices_area.max_width_area')
    min_height_area = fields.Float(related='sale_prices_area.min_height_area')
    max_height_area = fields.Float(related='sale_prices_area.max_height_area')

    min_price_area = fields.Float(related='sale_prices_area.min_price_area')

    @api.one
    @api.constrains('sale_price_type')
    def _create_relation(self):
        self.ensure_one()
        if self.sale_price_type == 'area':
            column = {'min_width_area': self.min_width_area,
                      'max_width_area': self.max_width_area,
                      'min_height_area': self.min_height_area,
                      'max_height_area': self.max_height_area,
                      'min_price_area': self.min_price_area
                      }
            self.write({'sale_prices_area': [(0, None, column)]})
            return {}
        elif self.sale_price_type != 'area':
            self.write({'sale_prices_area': [(2, self.sale_prices_area.id, False)]})
            return {}
