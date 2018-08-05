# -*- coding: utf-8 -*-
from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    origin_width = fields.Float(string="Width", required=False)
    origin_height = fields.Float(string="Height", required=False)

    def _prepare_procurement_from_move(self):
        res = super(StockMove, self)._prepare_procurement_from_move()
        res.update({
            'origin_width': self._context.get('width', 0),
            'origin_height': self._context.get('height', 0)
        })
        return res

    def create(self, vals):
        vals.update({
            'origin_width': self._context.get('width',0),
            'origin_height': self._context.get('height',0)
        })
        vals = super(StockMove, self).create(vals)        
        return vals
