# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp


class ProductPricesFabric(models.Model):
    _name = 'product.prices_fabric'

    fabric_uom = fields.Many2one('product.uom',
                                  string='Fabric UOM')
    rapport = fields.Float(string="Rapport",
                           default=0.0,
                           digits=dp.get_precision('Product Unit of Measure'))
    rapport_uom = fields.Many2one('product.uom',
                                  string='Rapport UOM')
    height_roll = fields.Float(string="Height Roll",
                               default=0.0,
                               digits=dp.get_precision('Product Unit of Measure'))
    roll_uom = fields.Many2one('product.uom',
                               string='Roll UOM')

    rapport_orientation = fields.Selection([
        ('normal', 'Normal'),
        ('turned', 'Turned')],
        string='Orientation',
        default='normal')

    """
    TODO: Debería ser Monetary, pero hay que asignarle un valor previo, no sirve default
    """
    min_price_fabric = fields.Float(string="Min. Sale Price",
                                    default=1.0,
                                    digits=dp.get_precision('Product Price'))
    cost_transport_fabric = fields.Float(string="Sale Price Transport",
                                         default=1.0,
                                         digits=dp.get_precision('Product Price'))
    min_transport_fabric = fields.Float(string="Min Free Transport",
                                         default=1.0,
                                         digits=dp.get_precision('Product Price'))

    sale_fabric_tmpl_id = fields.Many2one('product.template', 'Product Template')


class CompositionFabric(models.Model):
    _name = 'product.composition_fabric'

    composition_fabric_id = fields.Many2one('product.template', 'Fabric Composition')

    percent_composition = fields.Float('% Composition', (3, 2))

    type_composition = fields.Many2one('product.type_composition_fabric', 'Type Composition')


class TypeCompositionFabric(models.Model):
    _name = 'product.type_composition_fabric'
    _rec_name = 'name_type'

    name_type = fields.Char('Name Type Composition', size=40, translate=True)


class TagFabricCare(models.Model):
    _name = 'product.tag_fabric_care'

    name = fields.Char('Name', size=40, translate=True)
    image_care = fields.Binary('Imagen Care')
