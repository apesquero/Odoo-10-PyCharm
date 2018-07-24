# -*- coding: utf-8 -*-
# Copyright 2017 Amaro Pesquero Rodríguez <apesquero@gmail.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Fix Sale - Product variants",
    "summary": "Fixed product variants in sale management",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "data": [
             'views/sale_view.xml',
             ],
    "depends": [
        "sale_variant_configurator",
    ],
    "author": "Amaro Pesquero Rodríguez",
    "category": "Sales Management",
    "installable": True,
    "auto_install": True,
}
