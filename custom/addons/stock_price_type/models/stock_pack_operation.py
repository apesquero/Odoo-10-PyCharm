# -*- coding: utf-8 -*-
from odoo import models, fields


class stock_pack_operation(models.Model):
    _inherit = 'stock.pack.operation'

    origin_width = fields.Float(string="Width")
    origin_height = fields.Float(string="Height")
