# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SaleAdvancePaymentInv(models.TransientModel):
    _name = "sale.advance.payment.inv"
    _inherit = "sale.advance.payment.inv"

    @api.model
    def _get_advance_payment_method(self):
        state_obj = self.env['sale.order'].browse(self._context.get('active_ids')).state
        if state_obj in ('draft', 'sent', 'acepted'):
            return 'fixed'
        elif state_obj in ('sale', 'done'):
            return 'all'
        #TODO: Del Módulo original, no entiendo muy bien lo que hace, queda en desuso pero no lo borro
        elif self._count() == 1:
            sale_obj = self.env['sale.order']
            order = sale_obj.browse(self._context.get('active_ids'))[0]
            if all([line.product_id.invoice_policy == 'order' for line in order.order_line]) or order.invoice_count:
                return 'all'
        return 'delivered'

    advance_payment_method = fields.Selection([
        ('fixed', 'Down payment (fixed amount)'),
        ('percentage', 'Down payment (percentage)'),
        ('all', 'Invoiceable lines (deduct down payments)'),
        ('delivered', 'Invoiceable lines')],
        string='What do you want to invoice?',
        default=_get_advance_payment_method,
        required=True)

    @api.multi
    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        sale_obj = self.env['sale.order'].browse(self._context.get('active_ids'))
        if self.advance_payment_method == 'percentage':
            self.amount = sale_obj.user_id.company_id.default_signal
            return {}
        if self.advance_payment_method == 'fixed':
            self.amount = sale_obj.payment_signal
            return {}