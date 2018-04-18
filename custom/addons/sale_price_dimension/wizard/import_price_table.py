# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import xlrd


class WizardMultiDimensionTable(models.TransientModel):
    _name = 'wizard.mdtable'

    # allow imports to survive for 12h in case user is slow
    _transient_max_hours = 12.0

    prices_table_file = fields.Binary('Prices Table File')
    file_name = fields.Char('File Name')

    @api.multi
    def import_sale_prices_from_file(self):
        record_id = self.env[self._context.get('active_model')].browse(self._context.get('active_id'))
        try:
            book = xlrd.open_workbook(file_contents=base64.b64decode(self.prices_table_file))
            opers = self._generate_commands_from_xls_book(record_id.sale_price_type, book)
            record_id.write({'sale_prices_table': [(5, False, False)] + opers})
        except xlrd.XLRDError:
            raise UserError(_('Invalid file format! (Only accept .xls or .xlsx)'))
        return {}

    def _generate_commands_from_xls_book(self, mode, book):
        fs = book.sheet_by_index(0)
        rows = range(1, fs.nrows)
        cols = range(0 if mode == 'table_1d' else 1, fs.ncols)
        cmds = []
        for x in cols:
            for y in rows:
                cell = fs.cell(y, x)
                cellHL = fs.cell(0, x)
                cellHT = fs.cell(y, 0)
                cmds.append((
                    0,
                    False,
                    {
                        'pos_x': cellHL.value,
                        'pos_y': cellHT.value,
                        'value': cell.value
                    }
                ))
        return cmds
