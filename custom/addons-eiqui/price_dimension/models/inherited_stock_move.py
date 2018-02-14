# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017 Solucións Aloxa S.L. <info@aloxa.eu>
#                        Alexandre Díaz <alex@aloxa.eu>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields

class stock_move(models.Model):
    _inherit = 'stock.move'

    origin_width = fields.Float(string="Width", required=False)
    origin_height = fields.Float(string="Height", required=False)

    def _prepare_procurement_from_move(self):
        res = super(stock_move, self)._prepare_procurement_from_move()
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
        vals = super(stock_move, self).create(vals)        
        return vals
