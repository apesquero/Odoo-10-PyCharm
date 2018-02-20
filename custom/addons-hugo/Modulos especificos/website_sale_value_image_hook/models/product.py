# -*- coding: utf-8 -*-

from openerp import fields, models


class ProductAttribute(models.Model):
    _inherit = "product.attribute"
    
    type = fields.Selection(selection_add=[('image', 'Image')])

