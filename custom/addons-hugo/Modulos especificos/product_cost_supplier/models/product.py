# -*- coding: utf-8 -*-
from openerp import models, fields, exceptions, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    cost_mode = fields.Selection(
        selection_add=[('supplier', 'Supplier'),])
    
    @api.multi
    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        
        if 'cost_mode' in vals:
            for template in self:
                if template.cost_mode == 'supplier':
                    first_seller = template.seller_ids.filtered(lambda s: s.sequence == 1)
                    if not first_seller:
                        raise exceptions.Warning('No supplier configured while cost mode is supplier.')
    
        return res
    
    @api.multi
    def _apply_extra_cost_by_mode(self):
        self.ensure_one()
        
        if self.cost_mode == 'supplier':
            return False
        
        return super(ProductTemplate, self)._apply_extra_cost_by_mode()
    
    #Cost mode router
    @api.multi
    def get_cost_from_attribute_values(self, attribute_values):
        self.ensure_one()
        
        if self.cost_mode == 'supplier':
            first_seller = self.seller_ids.filtered(lambda s: s.sequence == 1)
            if not first_seller:
                raise excepetions.Warning('No supplier configured while trying to obtain its price.')
            return first_seller.get_price(proc_lines=attribute_values)
        
        return super(ProductTemplate, self).get_cost_from_attribute_values(attribute_values)

