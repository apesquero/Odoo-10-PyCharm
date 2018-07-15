# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class CompositionFabric(models.Model):
    _name = 'product.composition_fabric'

    composition_fabric_id = fields.Many2one('product.template', 'Fabric Composition')

    percent_composition = fields.Float('% Composition', (3, 2))

    type_composition = fields.Many2one('type.composition_fabric', 'Type Composition')

class TypeCompositionFabric(models.Model):
    _name = 'type.composition_fabric'
    _rec_name = 'name_type'

    name_type = fields.Char('Name Type Composition', size=40, translate=True)


