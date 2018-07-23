# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    origin_width = fields.Float(string="Width", required=True, default=0.0)
    origin_height = fields.Float(string="Height", required=True, default=0.0)

    width_sale_uom = fields.Many2one('product.uom',
                                     string='Width UOM',
                                     related='product_tmpl_id.width_uom',
                                     readonly=True)
    height_sale_uom = fields.Many2one('product.uom',
                                      string='Height UOM',
                                      related='product_tmpl_id.height_uom',
                                      readonly=True)

    product_price_type = fields.Selection([('standard', 'Standard'),
                                           ('fabric', 'Fabric'),
                                           ('table_1d', '1D Table'),
                                           ('table_2d', '2D Table'),
                                           ('area', 'Area')],
                                          string='Sale Price Type',
                                          related='product_tmpl_id.sale_price_type')

    rapport = fields.Float(related='product_tmpl_id.rapport')
    rapport_uom = fields.Many2one('product.uom',
                                  string='Rapport UOM',
                                  related='product_tmpl_id.rapport_uom',
                                  readonly=True)