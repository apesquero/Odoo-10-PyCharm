# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProcurementOrder(models.Model):
    """ Procurement Orders """
    _inherit = ['procurement.order', 'product.configurator']
    _name = 'procurement.order'


    @api.model
    def _run_move_create(self, procurement):
        res = super(ProcurementOrder, self)._run_move_create(procurement)

        res.update({
            'product_tmpl_id': self.product_tmpl_id.id,
        })
        return res

    @api.multi
    def _prepare_purchase_order_line(self, po, supplier):
        self.ensure_one()
        res = super(ProcurementOrder, self)._prepare_purchase_order_line(po=po, supplier=supplier)

        res.update({
            'product_tmpl_id': self.product_id.product_tmpl_id.id,
            # 'product_attribute_ids': [(4, x.id) for x in self.product_id.product_variant_id.attribute_line_ids],
        })
        return res
