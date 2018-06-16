# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import xlrd


class WizardMultiDimensionTable(models.TransientModel):
    _inherit = 'wizard.mdtable'

    @api.multi
    def import_supplier_prices_from_file(self):
        record_id = self.env[self._context.get('active_model')].browse(
            self._context.get('active_id'))

        try:
            book = xlrd.open_workbook(file_contents=base64.b64decode(
                self.prices_table_file))
            opers = self._generate_commands_from_xls_book(
                record_id.purchase_price_type, book)
            record_id.write({'prices_table': [(5, False, False)] + opers})
        except xlrd.XLRDError:
            raise UserError(_('Invalid file format! (Only accept .xls or .xlsx)'))
        return {}
