# -*- coding: utf-8 -*-
from datetime import date, timedelta

from odoo.tests.common import TransactionCase
from odoo import fields
from odoo.exceptions import Warning


class TestPaymentSignal(TransactionCase):

    def test_create(self):
        "Create a simple payment signal"

        partner = self.env['res.partner'].create({
            'name': 'TEST',
            'customer': True,
        })
        payment_term = self.env.ref('account.account_payment_term_net')
        product = self.env['product.product'].create({
            'name': 'Demo',
            'categ_id': self.env.ref('product.product_category_1').id,
            'standard_price': 35.0,
            'list_price': 40.0,
            'type': 'consu',
            'uom_id': self.env.ref('product.product_uom_unit').id,
            'default_code': 'PROD_DEL02',
        })
        sale_pricelist = self.env['product.pricelist'].create({
            'name': 'Sale pricelist',
            'discount_policy': 'without_discount',
            'item_ids': [(0, 0, {
                'compute_price': 'fixed',
                'fixed_price': 56.0,
                'product_id': product.id,
                'applied_on': '0_product_variant',
            })]
        })
        yesterday = date.today() - timedelta(days=1)
        tomorrow = date.today() + timedelta(days=1)

        order = self.env['sale.order'].create({
            'partner_id': partner.id,
            'validity_date': fields.Date.to_string(yesterday),
            'payment_term_id': payment_term.id,
            'pricelist_id': sale_pricelist.id,
            'lines_ids': [(0, 0, {
                'product_id': product.id,
                'product_uom': product.uom_id.id,
                'original_qty': 20.0,
                'price_unit': 1.0,  # will be updated by pricelist
            })],
        })
        order.onchange_partner_id()
        order.pricelist_id = sale_pricelist

        order._pay_signal()

