# -*- coding: utf-8 -*-
# © 2015 Oihane Crucelaegui - AvanzOSC
# © 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import fields, models, api


class ProductConfiguratorAttribute(models.Model):
    _inherit = 'product.configurator.attribute'

    price_extra_type = fields.Char(compute='_compute_price_extra_type',
                                   readonly=True, string='Extra Price Type')

    @api.depends('value_id')
    def _compute_price_extra_type(self):
        for record in self:
            record.price_extra_type = record.value_id.price_extra_type
