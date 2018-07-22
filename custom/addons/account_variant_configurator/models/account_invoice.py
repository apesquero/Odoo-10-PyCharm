# -*- coding: utf-8 -*-
from odoo import models


class AccountInvoiceLine(models.Model):
    _inherit = ['account.invoice.line', 'product.configurator']
    _name = 'account.invoice.line'
