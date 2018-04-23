# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_price_area_min_width = fields.Float(string="Min. Width", default=0.0,
                                             digits=dp.get_precision('Product Price'))
    sale_price_area_max_width = fields.Float(string="Max. Width", default=0.0,
                                             digits=dp.get_precision('Product Price'))
    sale_price_area_min_height = fields.Float(string="Min. Height", default=0.0,
                                              digits=dp.get_precision('Product Price'))
    sale_price_area_max_height = fields.Float(string="Max. Height", default=0.0,
                                              digits=dp.get_precision('Product Price'))
    sale_min_price_area = fields.Monetary("Min. Price")

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
