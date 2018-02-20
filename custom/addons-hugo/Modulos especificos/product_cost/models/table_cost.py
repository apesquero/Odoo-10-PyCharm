# -*- coding: utf-8 -*-
from openerp import models, fields, api, _


class TableCostItem(models.Model):
    _name = 'template.table.cost.item'
    
    template_id = fields.Many2one(
        comodel_name='product.template')
    x_upper = fields.Float()
    x_lower = fields.Float()
    y_upper = fields.Float()
    y_lower = fields.Float()
    cost = fields.Float()


class TableCostItemOne(models.Model):
    _name = 'template.table.cost.item.one'
    
    template_id = fields.Many2one(
        comodel_name='product.template')
    x_upper = fields.Float()
    x_lower = fields.Float()
    cost = fields.Float()

