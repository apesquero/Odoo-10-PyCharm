# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProcurementOrder(models.Model):
    """ Procurement Orders """
    _inherit = 'procurement.order'

    # Redefine again the product template field as a regular one
    product_tmpl_id = fields.Many2one(
        string='Product Template',
        comodel_name='product.template',
        store=True,
        related=False,
        auto_join=True,
    )


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
            'product_tmpl_id': supplier.product_tmpl_id.id,
        })
        return res
