# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ProductConfiguratorAttribute(models.Model):
    _inherit = 'product.configurator.attribute'

    image = fields.Binary(compute='_compute_image',
                          readonly=True, string='Image')

    @api.depends('value_id')
    def _compute_image(self):
        for record in self:
            record.image = record.value_id.image
