# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class TableListPriceItem(models.Model):
    _name = 'template.table.list.price.item'
    
    template_id = fields.Many2one(
        comodel_name='product.template')
    d_mode = fields.Selection(
        selection=[
            ('1d', '1D'),
            ('2d', '2D'),],
        string='Dimension', required=True)
    x_upper = fields.Float()
    x_lower = fields.Float()
    y_upper = fields.Float()
    y_lower = fields.Float()
    price = fields.Float()

