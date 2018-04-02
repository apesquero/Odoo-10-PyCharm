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

from odoo import models, fields
import odoo.addons.decimal_precision as dp


class ProductPricesTable(models.Model):
    _name = 'product.prices_table'

    pos_x = fields.Float(string="X", required=True)
    pos_y = fields.Float(string="Y", required=True)
    value = fields.Float(string="Value", digits=dp.get_precision('Product Price'))

    sale_product_tmpl_id = fields.Many2one('product.template', 'Product Template')
    supplier_product_id = fields.Many2one('product.supplierinfo', 'Product Supplier Info')
