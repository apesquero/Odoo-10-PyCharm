# -*- coding: utf-8 -*-
{
    'name': 'Custom Sale Order Type',
    'description': 'Module that adds the functionality of change of numbering by commercial',
    'depends': ['sale_order_type'],
    'data': [
        'views/inherit_sale_order_view.xml',
        'views/inherit_res_partner_view.xml',
    ],
    'application': True,
    'auto_install': True,
}