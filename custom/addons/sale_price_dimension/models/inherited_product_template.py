# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    width_uom = fields.Many2one('product.uom', string='Width UOM')
    height_uom = fields.Many2one('product.uom', string='Height UOM')

    area_uom = fields.Many2one('product.uom',
                               string='Area UOM',
                               related='sale_prices_area.area_uom')

    sale_price_type = fields.Selection([
        ('standard', 'Standard'),
        ('table_1d', '1D Table'),
        ('table_2d', '2D Table'),
        ('area', 'Area')],
        string='Sale Price Type',
        required=True,
        default='standard',
    )
    sale_prices_table = fields.One2many('product.prices_table',
                                        'sale_product_tmpl_id',
                                        string="Sale Prices Table")

    sale_prices_area = fields.One2many('product.prices_area',
                                       'sale_area_tmpl_id',
                                       string="Sale Prices Area")

    min_width_area = fields.Float(related='sale_prices_area.min_width_area')
    max_width_area = fields.Float(related='sale_prices_area.max_width_area')
    min_height_area = fields.Float(related='sale_prices_area.min_height_area')
    max_height_area = fields.Float(related='sale_prices_area.max_height_area')

    min_price_area = fields.Float(related='sale_prices_area.min_price_area')

    @api.one
    @api.constrains('sale_price_type')
    def _create_relation(self):
        self.ensure_one()
        if self.sale_price_type == 'area':
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
        elif self.sale_price_type != 'area' and self.sale_prices_area.id is not False:
            self.write({'sale_prices_area': [(2, self.sale_prices_area.id, False)]})
            return {}

    @api.constrains('min_width_area',
                    'max_width_area',
                    'min_height_area',
                    'max_height_area',
                    'min_price_area')
    def _check_area_values(self):
        if self.sale_price_type == 'area':
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
