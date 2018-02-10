# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class product_prices_table(models.Model):
    _inherit = 'product.prices_table'

    supplier_product_id = fields.Many2one('product.supplierinfo', 'Product Supplier Info')