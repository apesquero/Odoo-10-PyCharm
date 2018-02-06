# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    price_total = fields.Monetary(string='Amount with taxs', store=True,
                                  readonly=True, compute='_compute_price')

    # @api.one
    # @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
    #              'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
    #              'invoice_id.date_invoice', 'invoice_id.date')
    # def _compute_price(self):
    #     super(AccountInvoiceLine, self)._compute_price()
    #     self.price_total = self.price_subtotal + taxes


# class AccountInvoice(models.Model):
#     _inherit = 'account.invoice'
#
#     @api.multi
#     def order_lines_layouted(self):
#         """
#         Returns this sale order lines ordered by sale_layout_category sequence. Used to render the report.
#         """
#         self.ensure_one()
#         report_pages = [[]]
#         for category, lines in groupby(self.invoice_line_ids, lambda l: l.layout_category_id):
#             # If last added category induced a pagebreak, this one will be on a new page
#             if report_pages[-1] and report_pages[-1][-1]['pagebreak']:
#                 report_pages.append([])
#             # Append category to current report page
#             report_pages[-1].append({
#                 'name': category and category.name,
#                 'subtotal': category and category.subtotal,
#                 'pagebreak': category and category.pagebreak,
#                 'lines': list(lines)
#             })
#
#         return report_pages
