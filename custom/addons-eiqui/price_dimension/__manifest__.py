# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017 Solucións Aloxa S.L. <info@aloxa.eu>
#                        Alexandre Díaz <alex@aloxa.eu>
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Price Dimension',
    'version': '1.0',
    'author': "Alexandre Díaz (Aloxa Solucións S.L.) <alex@aloxa.eu>",
    'website': 'https://www.eiqui.com',
    'category': 'eiqui/manzano',
    'summary': "Price Dimension",
    'description': "Price Dimension",
    'depends': [
        'sale',
        'stock',
        'purchase',
        # Si no pones sale_variant_configurator, malo, no te va ha funcionar en la vida
        'sale_variant_configurator',
        # También has de poner este
        'purchase_variant_configurator',
    ],
    'external_dependencies': {
        'python': [
            'xlrd',
        ]
    },
    'data': [
        'views/general.xml',
        'views/inherited_product_template_views.xml',
        'views/inherited_product_product_views.xml',
        'views/inherited_product_supplier_info_views.xml',
        'views/inherited_sale_order_views.xml',
        'views/inherited_purchase_order_views.xml',
        'views/inherited_stock_move_views.xml',
        'views/inherited_stock_picking_views.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3',
}
