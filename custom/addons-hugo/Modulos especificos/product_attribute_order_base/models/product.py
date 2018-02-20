# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class ProductAttributeLine (models.Model):
    _inherit = 'product.attribute.line'
    
    sequence = fields.Integer(
        string='Sequence', help="Determine the display order")


class ProductTemplate (models.Model):
    _inherit = 'product.template'
    
    attribute_order = fields.Selection(
        selection=[('attribute', 'Attribute'),
                   ('product', 'Product')],
        required=True, default='attribute',
        string='Attributes order')

