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
    'name': 'Attribute Price Extra Percent',
    'version': '1.0',
    'author': "Alexandre Díaz (Aloxa Solucións S.L.) <alex@aloxa.eu>",
    'website': 'https://www.eiqui.com',
    'category': 'eiqui/manzano',
    'summary': "Add Percent Option in Sale and Pruchase variant Price",
    'description': "Add Percent Option in Sale and Pruchase variant Price",
    'depends': [
        'sale',
        'purchase',
        'product_variant_configurator',
        'sale_variant_configurator',
        'purchase_variant_configurator',
    ],
    'data': [
        'views/supplier_attribute_value_views.xml',
        'views/inherited_product_supplier_info_views.xml',
        'views/inherited_product_attribute_value_views.xml',
        'views/inherited_product_attribute_price_views.xml',
        'views/inherited_sale_order_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'AGPL-3',
}
