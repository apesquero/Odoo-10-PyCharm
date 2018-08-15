# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT


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
        #AP: Includes the method of calculating the extra price with the pricelist
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
            #AP: Update price for having into account possible extra prices
            self._onchange_product_attribute_ids_configurator()
            self._update_price_configurator()
        return res

    # @api.multi
    # def _get_display_price(self, product):
    #     # TO DO: move me in master/saas-16 on sale.order
    #     #AP: Agrego una condición más, pero no se por qué.
    #     if self.order_id.pricelist_id.discount_policy == 'with_discount' \
    #             or product._name != 'product.product':
    #         return product.with_context(
    #             pricelist=self.order_id.pricelist_id.id).price
    #
    #     final_price, rule_id = self.order_id.pricelist_id. \
    #         get_product_price_rule(self.product_id,
    #                                self.product_uom_qty or 1.0,
    #                                self.order_id.partner_id)
    #
    #     context_partner = dict(self.env.context,
    #                            partner_id=self.order_id.partner_id.id,
    #                            date=self.order_id.date_order)
    #
    #     base_price, currency_id = self.with_context(context_partner). \
    #         _get_real_price_currency(self.product_id, rule_id,
    #                                  self.product_uom_qty,
    #                                  self.product_uom,
    #                                  self.order_id.pricelist_id.id)
    #
    #     if currency_id != self.order_id.pricelist_id.currency_id.id:
    #         base_price = self.env['res.currency'].browse(currency_id). \
    #             with_context(context_partner).\
    #             compute(base_price,
    #                     self.order_id.pricelist_id.currency_id)
    #
    #     # negative discounts (= surcharge) are included in the display price
    #     return max(base_price, final_price)

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update({
            'product_tmpl_id': self.product_tmpl_id.id or False,
        })
        return res

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        vals = super(SaleOrderLine, self)._prepare_order_line_procurement(group_id=group_id)
        vals.update({
            'product_tmpl_id': self.product_tmpl_id.id or False,
            # 'product_attribute_ids': [(4, x.id) for x in self.product_attribute_ids],
        })
        return vals

    @api.multi
    def _action_procurement_create(self):
        """
        Create procurements based on quantity ordered. If the quantity is increased, new
        procurements are created. If the quantity is decreased, no automated action is taken.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        new_procs = self.env['procurement.order']  # Empty recordset
        for line in self:
            if line.state != 'sale' or not line.product_id._need_procurement():
                continue
            qty = 0.0
            for proc in line.procurement_ids:
                qty += proc.product_qty
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            if not line.order_id.procurement_group_id:
                vals = line.order_id._prepare_procurement_group()
                line.order_id.procurement_group_id = self.env["procurement.group"].create(vals)

            vals = line._prepare_order_line_procurement(
                group_id=line.order_id.procurement_group_id.id)
            vals['product_qty'] = line.product_uom_qty - qty
            new_proc = self.env["procurement.order"].with_context(
                procurement_autorun_defer=True,
            ).create(vals)
            # Do one by one because need pass specific context values
            new_proc.with_context(
                product_tmpl_id=line.product_tmpl_id.id,
                # product_attribute_ids=line.product_attribute_ids,
            ).run()
            new_procs += new_proc
        return new_procs
