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
from .consts import EXTRA_PRICE_TYPES


class supplier_attribute_value(models.Model):
    _name = 'supplier.attribute.value'

    supplierinfo_id = fields.Many2one(comodel_name='product.supplierinfo')
    value = fields.Many2one(
        comodel_name='product.attribute.value',
        string='Value')
    attribute = fields.Many2one(
        comodel_name='product.attribute', related='value.attribute_id',
        string='Attribute')
    price_extra = fields.Float(
        string='Supplier Price Extra',
        digits=dp.get_precision('Product Price'),
        default=0.0)

    price_extra_type = fields.Selection(EXTRA_PRICE_TYPES,
                                        string='Price Extra Type',
                                        equired=True,
                                        default='standard')
