# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp


class ProductPricesTable(models.Model):
    _name = 'product.prices_table'

    pos_x = fields.Float(string="X", required=True)
    pos_y = fields.Float(string="Y", required=True)
    value = fields.Float(string="Value", digits=dp.get_precision('Product Price'))

    sale_product_tmpl_id = fields.Many2one('product.template', 'Product Template')

    supplier_product_id = fields.Many2one('product.supplierinfo', 'Product Supplier Info')

