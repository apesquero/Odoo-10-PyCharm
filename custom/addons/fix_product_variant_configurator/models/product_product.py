# -*- coding: utf-8 -*-
# Copyright 2018 Amaro Pesquero Rodríguez <apesquero@gmail.com>
from odoo import _, api, exceptions, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _build_attributes_domain(self, product_template, product_attributes):
        domain = []
        cont = 0
        if product_template:
            domain.append(('product_tmpl_id', '=', product_template.id))
            for attr_line in product_attributes:
                # We need this hack to trigger the compute function,
                # otherwise attr_line.price_extra always returns 0.0
                # here (possible Odoo bug, it seems Odoo does not behave
                # well with a computed variable on NewID 'child' of another
                # NewID)
                attr_line.value_id = attr_line.value_id
                if isinstance(attr_line, dict):
                    value_id = attr_line.get('value_id')
                else:
                    value_id = attr_line.value_id.id
                if value_id:
                    domain.append(('attribute_value_ids', '=', value_id))
                    cont += 1
        return domain, cont
