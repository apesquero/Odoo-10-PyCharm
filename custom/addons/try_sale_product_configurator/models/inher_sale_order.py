# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = ["sale.order.line", "product.configurator"]
    _name = "sale.order.line"

    @api.multi
    @api.depends('product_attribute_ids', 'product_attribute_ids.value_id')
    def _compute_price_extra(self):
        self.ensure_one()
        for record in self:
            record.price_extra = sum(
                record.product_attribute_ids.value_id.price_ids.filtered(
                    lambda x: (
                        x.product_tmpl_id == record.product_tmpl_id)
                ).mapped('price_extra'))
