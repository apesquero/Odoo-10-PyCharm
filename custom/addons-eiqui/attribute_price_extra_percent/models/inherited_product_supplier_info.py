# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017 Solucións Aloxa S.L. <info@aloxa.eu>
#                        Alexandre Díaz <alex@aloxa.eu>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class ProductSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    @api.depends('attribute_value_ids')
    def _compute_price_extra_percentage(self):
        product_id = self.env.context and self.env.context.get('product_id') or False
        for supplier in self:
            price_extra = 0.0
            for variant_id in supplier.attribute_value_ids:
                if product_id and variant_id.value not in product_id.attribute_value_ids:
                    continue
                if variant_id.price_extra_type != 'percentage' or \
                        supplier.id != variant_id.supplierinfo_id.id:
                    continue
                price_extra += variant_id.price_extra
            supplier.price_extra_perc = price_extra

    @api.depends('attribute_value_ids')
    def _compute_price_extra(self):
        product_id = self.env.context and self.env.context.get('product_id') or False
        for supplier in self:
            price_extra = 0.0
            for variant_id in supplier.attribute_value_ids:
                if product_id and variant_id.value not in product_id.attribute_value_ids:
                    continue
                if variant_id.price_extra_type != 'standard' or \
                        supplier.id != variant_id.supplierinfo_id.id:
                    continue
                price_extra += variant_id.price_extra
            supplier.price_extra = price_extra
            
    attribute_value_ids = fields.One2many(
        comodel_name='supplier.attribute.value',
        inverse_name='supplierinfo_id'
    )

    price_extra = fields.Float(compute='_compute_price_extra',
                               string='Variant Extra Price',
                               help="This is the sum of the extra price of all attributes",
                               digits=dp.get_precision('Product Price'))
    price_extra_perc = fields.Float(compute='_compute_price_extra_percentage',
                                    string='Variant Extra Price Percentage',
                                    help="This is the percentage of the extra price of all attributes",
                                    digits=dp.get_precision('Product Price'))

    @api.depends('price')
    def get_supplier_price(self):
        product_id = self.env.context and self.env.context.get('product_id') or False
        result = self.price
        result += (result * self.with_context(product_id=product_id).price_extra_perc) /100
        result += self.with_context(product_id=product_id).price_extra
        return result

        
    @api.multi
    def _prepare_purchase_order_line(self, po, supplier):
        self.ensure_one()
        order_line = super(ProductSupplierInfo, self)._prepare_purchase_order_line( po, supplier)
        if order_line:
            product_id = self.product_id.id
            price_unit = order_line.get('price_unit')
            price_unit += (price_unit * self.with_context(product_id=product_id).price_extra_perc) /100
            price_unit += self.with_context(product_id=product_id).price_extra
            order_line.update({'price_unit': price_unit,})

    @api.multi
    def action_open_value_extras(self):
        self.ensure_one()
        extra_ds = self.env['supplier.attribute.value']
        for line in self.product_tmpl_id.attribute_line_ids:
            for value in line.value_ids:
                extra = extra_ds.search([('supplierinfo_id', '=', self.id),
                                         ('value', '=', value.id)])
                if not extra:
                    extra = extra_ds.create({
                        'supplierinfo_id': self.id,
                        'value': value.id,
                    })
                extra_ds |= extra
        all_supplierinfo_extra = extra_ds.search([
            ('supplierinfo_id', '=', self.id)
        ])
        remove_extra = all_supplierinfo_extra - extra_ds
        remove_extra.unlink()
        action = self.env.ref('attribute_price_extra_percent.supplier_attribute_value_action').read()[0]
        return action
