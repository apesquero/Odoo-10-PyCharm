# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    width_uom = fields.Many2one('product.uom',
                                domain="[('category_id', '=', 4)]",
                                default=lambda self: self.env['product.uom'].search([('name', '=', u'cm')]).id,
                                string='Width UOM')
    height_uom = fields.Many2one('product.uom',
                                 domain="[('category_id', '=', 4)]",
                                 default=lambda self: self.env['product.uom'].search([('name', '=', u'cm')]).id,
                                 string='Height UOM')

    product_price_type = fields.Selection([
        ('standard', 'Standard'),
        ('fabric', 'Fabric'),
        ('table_1d', '1D Table'),
        ('table_2d', '2D Table'),
        ('area', 'Area')],
        string='Sale Price Type',
        required=True,
        default='standard',
    )
    """FABRIC"""
    fabric_uom = fields.Many2one('product.uom',
                                  domain="[('category_id', '=', 4)]",
                                  default=lambda self: self.env['product.uom'].search([('name', '=', u'm')]).id,
                                  string='Fabric UOM',
                                  related='sale_prices_fabric.fabric_uom')

    rapport = fields.Float(related='sale_prices_fabric.rapport')
    rapport_uom = fields.Many2one('product.uom',
                                  domain="[('category_id', '=', 4)]",
                                  default=lambda self: self.env['product.uom'].search([('name', '=', u'cm')]).id,
                                  string='Rapport UOM',
                                  related='sale_prices_fabric.rapport_uom')

    height_roll = fields.Float(related='sale_prices_fabric.height_roll')
    roll_uom = fields.Many2one('product.uom',
                               domain="[('category_id', '=', 4)]",
                               default=lambda self: self.env['product.uom'].search([('name', '=', u'cm')]).id,
                               string='Roll UOM',
                               related='sale_prices_fabric.roll_uom')

    rapport_orientation = fields.Selection([
        ('normal', 'Normal'),
        ('turned', 'Turned')],
        string='Orientation',
        default='normal',
        related='sale_prices_fabric.rapport_orientation')

    min_price_fabric = fields.Float(related='sale_prices_fabric.min_price_fabric')
    cost_transport_fabric = fields.Float(related='sale_prices_fabric.cost_transport_fabric')
    min_transport_fabric = fields.Float(related='sale_prices_fabric.min_transport_fabric')

    sale_prices_fabric = fields.One2many('product.prices_fabric',
                                         'sale_fabric_tmpl_id',
                                         string="Sale Prices Fabric")

    composition_fabric = fields.One2many('product.composition_fabric',
                                         'composition_fabric_id',
                                         string="Fabric Composition")

    fabric_care = fields.Many2many('product.tag_fabric_care',
                                   strig='Fabric Care')

    """TABLE"""
    sale_prices_table = fields.One2many('product.prices_table',
                                        'sale_product_tmpl_id',
                                        string="Sale Prices Table")

    """AREA"""
    sale_prices_area = fields.One2many('product.prices_area',
                                       'sale_area_tmpl_id',
                                       string="Sale Prices Area")

    area_uom = fields.Many2one('product.uom',
                               domain="[('category_id', '=', 4)]",
                               default=lambda self: self.env['product.uom'].search([('name', '=', u'm')]).id,
                               string='Area UOM',
                               related='sale_prices_area.area_uom')

    min_width_area = fields.Float(related='sale_prices_area.min_width_area')
    max_width_area = fields.Float(related='sale_prices_area.max_width_area')
    min_height_area = fields.Float(related='sale_prices_area.min_height_area')
    max_height_area = fields.Float(related='sale_prices_area.max_height_area')

    min_price_area = fields.Float(related='sale_prices_area.min_price_area')

    @api.one
    @api.constrains('product_price_type')
    def _create_relation(self):
        self.ensure_one()
        if self.product_price_type == 'fabric':
            column = {'rapport': self.rapport,
                      'height_roll': self.height_roll,
                      'min_price_fabric': self.min_price_fabric,
                      'cost_transport_fabric': self.cost_transport_fabric,
                      'min_transport_fabric': self.min_transport_fabric
                      }
            # We check that the relationship is not already created
            if not self.sale_prices_fabric:
                self.write({'sale_prices_fabric': [(0, None, column)]})
            return {}
        if self.product_price_type != 'fabric' and self.sale_prices_fabric.id is not False:
            self.write({'sale_prices_fabric': [(2, self.sale_prices_fabric.id, False)]})
            return {}
        if self.product_price_type == 'area':
            column = {'min_width_area': self.min_width_area,
                      'max_width_area': self.max_width_area,
                      'min_height_area': self.min_height_area,
                      'max_height_area': self.max_height_area,
                      'min_price_area': self.min_price_area
                      }
            # We check that the relationship is not already created
            if not self.sale_prices_area:
                self.write({'sale_prices_area': [(0, None, column)]})
            return {}
        if self.product_price_type != 'area' and self.sale_prices_area.id is not False:
            self.write({'sale_prices_area': [(2, self.sale_prices_area.id, False)]})
            return {}


    @api.constrains('min_width_area',
                    'max_width_area',
                    'min_height_area',
                    'max_height_area',
                    'min_price_area')
    def _check_area_values(self):
        if self.product_price_type == 'area':
            if self.min_width_area <= 0 or \
                self.min_height_area <= 0 or \
                self.max_width_area <= 0 or \
                self.max_height_area <= 0 or \
                self.min_price_area <= 0:
                raise ValidationError(_("Error! The values can`t "
                                        "be negative or cero"))
            elif self.min_width_area > self.max_width_area:
                raise ValidationError(_("Error! Min. Width can`t "
                                        "be greater than Max. Width"))
            elif self.min_height_area > self.max_height_area:
                raise ValidationError(_("Error! Min. Height can`t "
                                        "be greater than Max. Height"))
        return True
