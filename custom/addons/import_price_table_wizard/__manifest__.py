# -*- coding: utf-8 -*-

{
    'name': 'Import Price Table Wizard',
    'description': 'Module that adds a wizard to import price tables',
    'version': '10.0.1.0',
    'author': 'Amaro Pesquero',
    'data': ['views/import_price_table.xml'],
    'application': True,
    'external_dependencies': {'python': ['xlrd']},
    'qweb': ['static/src/xml/*.xml'],
    'category': 'Sale',
    'depends': [],
    'application': True,
    'installable': True,
}
