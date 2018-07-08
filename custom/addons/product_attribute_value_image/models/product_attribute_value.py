# -*- coding: utf-8 -*-from openerp import models, fields
from odoo import api, fields, models

class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    image = fields.Binary(
        string='Image')
