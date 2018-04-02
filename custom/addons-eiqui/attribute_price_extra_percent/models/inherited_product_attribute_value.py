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

import odoo
from odoo import models, fields, api, tools, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.tools.translate import _


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    @api.multi
    def unlink(self):
        product_ids = self.env['product.supplierinfo'].with_context(
            active_test=False).search([
            ('attribute_value_ids', 'in', self.ids)])
        if product_ids:
            raise UserError(_('The operation cannot be completed:\n \
                You are trying to delete an attribute value with a \
                reference on a product supplier variant.'))
        return super(ProductAttributeValue, self).unlink()

    price_extra_type = fields.Selection([('standard', 'Standard'),
                                         ('percentage', 'Percentage')],
                                         string='Price Extra Type',
                                         required=True,
                                         default='standard')
                                         
    supplier_ids = fields.Many2many('product.supplierinfo',
                                    id1='att_id',
                                    id2='prod_id',
                                    string='Variants',
                                    readonly=True)
