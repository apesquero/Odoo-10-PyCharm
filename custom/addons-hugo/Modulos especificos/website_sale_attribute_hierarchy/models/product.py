# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class ProductTemplate (models.Model):
    _inherit = 'product.template'
    
    website_sale_variant_type = fields.Selection(
        selection_add=[('hierarchy', 'Hierarchy')], default='hierarchy')
    
    def get_default_values_as_website_dict(self):
        self.ensure_one()
        
        res = {}
        for attr_line in self.attribute_line_ids:
            value = attr_line.default if attr_line.default else attr_line.value_ids[0]
            if attr_line.attr_type == 'range':
                res[attr_line.attribute_id.id] = {'value': value.id, 'custom_value': value.min_range}
            else:
                res[attr_line.attribute_id.id] = {'value': value.id}
        
        return res

