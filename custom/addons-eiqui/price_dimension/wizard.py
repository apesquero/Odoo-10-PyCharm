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

from openerp import models, fields, api
from openerp.exceptions import UserError
from openerp.tools.translate import _
import base64
import xlrd
import logging
_logger = logging.getLogger(__name__)


class Wizard_Multi_Dimension_Table(models.TransientModel):
    _name = 'wizard.mdtable'

    @api.multi
    def import_sale_prices_from_file(self):
        record_id = self.env[self._context.get('active_model')].browse(self._context.get('active_id'))

        try:
            book = xlrd.open_workbook(file_contents=base64.b64decode(self.prices_table_file))
            opers = self._generate_commands_from_xls_book(record_id.sale_price_type, book)
            record_id.write({'sale_prices_table': [(5, False, False)] + opers})
        except xlrd.XLRDError as err:
            raise UserError(_('Invalid file format! (Only accept .xls or .xlsx)'))
        return {}
    
#     @api.multi
#     def import_cost_prices_from_file(self):
#         record_id = self.env[self._context.get('active_model')].browse(self._context.get('active_id'))
# 
#         try:
#             book = xlrd.open_workbook(file_contents=base64.b64decode(self.prices_table_file))
#             opers = self._generate_commands_from_xls_book(record_id.cost_price_type, book)
#             record_id.write({'cost_prices_table': [(5, False, False)] + opers})
#         except xlrd.XLRDError as err:
#             raise UserError(_('Invalid file format! (Only accept .xls or .xlsx)'))
#         return {}

    @api.multi
    def import_supplier_prices_from_file(self):
        record_id = self.env[self._context.get('active_model')].browse(self._context.get('active_id'))

        try:
            book = xlrd.open_workbook(file_contents=base64.b64decode(self.prices_table_file))
            opers = self._generate_commands_from_xls_book(record_id.price_type, book)
            record_id.write({'prices_table': [(5, False, False)] + opers})
        except xlrd.XLRDError as err:
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

    prices_table_file = fields.Binary(string='Prices Table File')
