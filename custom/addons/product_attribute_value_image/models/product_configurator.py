# -*- coding: utf-8 -*-

from odoo import _, api, exceptions, fields, models
from odoo.addons import decimal_precision as dp

class ProductConfigurator(models.AbstractModel):
    _inherit = 'product.configurator'

    image = fields.Binary(
        string='Image')