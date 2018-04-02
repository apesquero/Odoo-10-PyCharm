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
from odoo import models, fields, api, SUPERUSER_ID, exceptions
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        super(PurchaseOrderLine, self)._onchange_quantity()
        if not self.product_id:
            return
            
        if self.can_create_product:
            try:
                with self.env.cr.savepoint():
                    product_tmp = self.product_id = self.create_variant_if_needed()
            except exceptions.ValidationError as e:
                _logger.exception('Product not created!')
                return {'warning': {
                    'title': _('Product not created!'),
                    'message': e.name,
                }}

        product = self.product_id

        seller = product._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order[:10],
            uom_id=self.product_uom)

        if not seller:
            return
            
        seller = seller.with_context(
            product_id=product
            )
        price_unit = self.env['account.tax']._fix_tax_included_price(
            seller.get_supplier_price(), product.supplier_taxes_id,
            self.taxes_id) if seller else 0.0
        if price_unit and seller and self.order_id.currency_id and \
                seller.currency_id != self.order_id.currency_id:
            price_unit = seller.currency_id.compute(price_unit, self.order_id.currency_id)
        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = self.env['product.uom']._compute_price(
                seller.product_uom.id,
                price_unit,
                to_uom_id=self.product_uom.id)
        self.price_unit = price_unit
