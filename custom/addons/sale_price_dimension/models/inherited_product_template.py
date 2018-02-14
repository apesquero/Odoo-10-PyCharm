# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp


class product_template(models.Model):
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