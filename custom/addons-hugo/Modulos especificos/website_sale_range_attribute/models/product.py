# -*- coding: utf-8 -*-

from openerp import models, fields, exceptions, api, _


class ProductAttributeLine (models.Model):
    _inherit = 'product.attribute.line'
    
    @api.multi
    def get_range_min(self):
        self.ensure_one()
        
        if self.attr_type != 'range':
            exceptions.Warning('Trying to obtain the min range of a non range attribute')
        
        return min(self.value_ids, key=lambda x: x.min_range).min_range
    
    @api.multi
    def get_range_max(self):
        self.ensure_one()
        
        if self.attr_type != 'range':
            exceptions.Warning('Trying to obtain the max range of a non range attribute')
        
        return max(self.value_ids, key=lambda x: x.max_range).max_range
    
    @api.multi
    def get_range_default_value(self):
        self.ensure_one()
        
        return self.get_range_min() #TODO


class ProductAttribute(models.Model):
    _inherit = "product.attribute"
    
    type = fields.Selection(selection_add=[('rangeinput', 'RangeInput')])

