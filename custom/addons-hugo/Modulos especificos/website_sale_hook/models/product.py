# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class ProductTemplate (models.Model):
    _inherit = 'product.template'
    
    website_sale_variant_type = fields.Selection(
        selection=[('standard', 'Standard')], required=True,
        string='Variants selection', default='standard')
    
    def get_default_values_as_website_dict(self):
        self.ensure_one()
        
        res = {}
        for attr_line in self.attribute_line_ids:
            value = attr_line.value_ids[0]
            res[attr_line.attribute_id.id] = {'value': value.id}
        
        return res

