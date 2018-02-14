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

from psycopg2 import OperationalError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _
from odoo import models, fields, api, SUPERUSER_ID
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class stock_pack_operation(models.Model):
    _inherit = 'stock.pack.operation'

    origin_width = fields.Float(string="Width")
    origin_height = fields.Float(string="Height")


    #~ @api.depends('linked_move_operation_ids.move_id')
    #~ @api.multi
    #~ def _compute_size(self):
        #~ for r in self:
            #~ _logger.info(r.id)
            #~ _logger.info("-----------------")
            #~ for move in r.linked_move_operation_ids:
                #~ _logger.info(r.id)
                #~ _logger.info(move.display_name)
                #~ _logger.info(move.move_id.id)
                #~ _logger.info(move.move_id.origin_height)
                #~ _logger.info(move.move_id.origin_width)
                #~ r.origin_height = move.move_id.origin_height
                #~ r.origin_width = move.move_id.origin_width
