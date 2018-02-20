# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class SuppliersTablePriceItem(models.Model):
    _name = 'suppliers.table.price.item'
    
    supplierinfo = fields.Many2one(
        comodel_name='product.supplierinfo')
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

