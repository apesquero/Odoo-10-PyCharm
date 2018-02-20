# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class ProductTemplate (models.Model):
    _inherit = 'product.template'
    
    website_sale_variant_type = fields.Selection(
        selection_add=[('topdown', 'TopDown')])

