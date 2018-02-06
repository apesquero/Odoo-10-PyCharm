# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    date_measure = fields.Date('Date of measure')

    date_signal = fields.Date('Date of signal')

    review_quotation = fields.Boolean('Review quotation?')

    acepted = fields.Boolean('Acepted', default=False)

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('acepted', 'Quotation Acepted'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    @api.multi
    def do_acepted(self):
        self.update({'acepted': True})
        return self.write({'state': 'acepted'})

    @api.multi
    def action_cancel(self):
        self.update({'acepted': False})
        return self.write({'state': 'cancel'})
