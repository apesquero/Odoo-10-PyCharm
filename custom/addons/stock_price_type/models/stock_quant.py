# -*- coding: utf-8 -*-
from odoo import models, fields


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    origin_width = fields.Float(string="Width", required=False)
    origin_height = fields.Float(string="Height", required=False)
