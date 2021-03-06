# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from . import models


def assign_product_template(cr, registry):
    """
    This post-init-hook will update all existing mrp.bom.line, mrp.production
    and mrp.production.product.line
    """
    cr.execute('UPDATE mrp_bom_line AS line'
               '   SET product_tmpl_id = product_product.product_tmpl_id'
               '  FROM product_product'
               ' WHERE line.product_id = product_product.id')
    cr.execute('UPDATE mrp_production AS line'
               '   SET product_template_id = product_product.product_tmpl_id'
               '  FROM product_product'
               ' WHERE line.product_id = product_product.id')
    cr.execute('UPDATE mrp_production_product_line AS line'
               '   SET product_tmpl_id = product_product.product_tmpl_id'
               '  FROM product_product'
               ' WHERE line.product_id = product_product.id')
