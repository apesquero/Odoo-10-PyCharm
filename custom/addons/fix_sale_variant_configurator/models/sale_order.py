# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _update_price_configurator(self):
        """If there are enough data (template, pricelist & partner), check new
        price and update line if different.
        """
        self.ensure_one()
        if (not self.product_tmpl_id or not self.order_id.pricelist_id or
                not self.order_id.partner_id):
            return
        product_tmpl = self.product_tmpl_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=self.product_uom_qty,
            date_order=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
            fiscal_position=self.env.context.get('fiscal_position')
        )
        price = self.env['account.tax']._fix_tax_included_price_company(
            product_tmpl.uom_id._compute_price(
                self.price_extra,
                self.env['product.uom'].browse(
                    product_tmpl._context['uom'])) +
            self._get_display_price(product_tmpl),
            product_tmpl.taxes_id,
            self.tax_id, self.company_id)
        if self.price_unit != price:
            self.price_unit = price

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        """Update price for having into account changes due to qty"""
        res = super(SaleOrderLine, self).product_uom_change()
        if not self.product_id:
            self._onchange_product_attribute_ids_configurator()
            self._update_price_configurator()
        return res

    @api.multi
    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        if self.order_id.pricelist_id.discount_policy == 'with_discount' or product._name != 'product.product':
            return product.with_context(pricelist=self.order_id.pricelist_id.id).price
        final_price, rule_id = self.order_id.pricelist_id.get_product_price_rule(self.product_id,
                                                                                 self.product_uom_qty or 1.0,
                                                                                 self.order_id.partner_id)
        context_partner = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order)
        base_price, currency_id = self.with_context(context_partner)._get_real_price_currency(self.product_id, rule_id,
                                                                                              self.product_uom_qty,
                                                                                              self.product_uom,
                                                                                              self.order_id.pricelist_id.id)
        if currency_id != self.order_id.pricelist_id.currency_id.id:
            base_price = self.env['res.currency'].browse(currency_id).with_context(context_partner).compute(base_price,
                                                                                                            self.order_id.pricelist_id.currency_id)
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)
