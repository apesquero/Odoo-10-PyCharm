# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp


class ProductPricesArea(models.Model):
    _name = 'product.prices_area'

    min_width_area = fields.Float(string="Min. Width", default=0.0,
                             digits=dp.get_precision('Product Price'))
    max_width_area = fields.Float(string="Max. Width", default=0.0,
                             digits=dp.get_precision('Product Price'))
    min_height_area = fields.Float(string="Min. Height", default=0.0,
                              digits=dp.get_precision('Product Price'))
    max_height_area = fields.Float(string="Max. Height", default=0.0,
                              digits=dp.get_precision('Product Price'))

    """
    TODO: Debería ser Monetary, pero hay que asignarle un valor previo, no sirve default
    """
    min_price_area = fields.Float(string="Min. Price", default=1.0,
                             digits=dp.get_precision('Product Price'))

    sale_area_tmpl_id = fields.Many2one('product.template', 'Product Template')
