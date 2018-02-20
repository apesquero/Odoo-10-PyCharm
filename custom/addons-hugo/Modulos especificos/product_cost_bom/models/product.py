# -*- coding: utf-8 -*-
from openerp import models, fields, exceptions, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    cost_mode = fields.Selection(
        selection_add=[('bom', 'BoM'),])
    
    @api.multi
    def _apply_extra_cost_by_mode(self):
        self.ensure_one()
        
        if self.cost_mode == 'bom':
            return True
        
        return super(ProductTemplate, self)._apply_extra_cost_by_mode()
    
    #Cost mode router
    @api.multi
    def get_cost_from_attribute_values(self, attribute_values):
        self.ensure_one()
        
        if self.cost_mode == 'bom':
            unlink_attr = False
            if isinstance(attribute_values, list):
                proc_attributes = self._get_procurement_values_from_dict(attribute_values)
                unlink_attr = True
            else:
                proc_attributes = attribute_values
            
            cost = self.sudo()._get_bom_cost_from_proclines(proc_attributes)
            
            if unlink_attr:
                proc_attributes.unlink()
            
            return cost
        
        return super(ProductTemplate, self).get_cost_from_attribute_values(attribute_values)
    
    #BoM Cost Methods
    @api.multi
    def _get_bom_cost_from_proclines(self, proc_lines):
        self.ensure_one()
        
        bom_obj = self.env['mrp.bom']
        bom_id = bom_obj._bom_find(product_tmpl_id=self.id)
        bom = bom_obj.browse(bom_id)
        factor = 1 #TODO maybe but corrected self.env['product.uom']._compute_qty(product_uom.id, product_qty, bom.product_uom.id) / bom.product_qty
        result1, result2 = self.env['mrp.bom'].with_context(
                                   production_product_attributes = proc_lines,
                                   bom_explode_no_create_new_product = True,
                               )._bom_explode(bom, False, factor)
        
        cost = 0
        for child_item in result1:
            template = self.browse(child_item['product_tmpl_id'])
            
            #child_proc_lines = self.env['procurement.attribute.line']
            #for values_dict in child_item['product_attributes']: #TODO no need to create the procurement.attribute.line anymore, can pass the dicts as list, but need to change 'custom_value' to 'r'
            #    child_proc_lines |= child_proc_lines.create(values_dict[2])
            
            child_value_dicts = []
            for values_dict in child_item['product_attributes']:
                child_value_dicts.append(values_dict[2])
            
            cost += child_item['product_qty'] * \
                    template.with_context( {},
                        product_attribute_values=child_value_dicts#child_proc_lines
                    )._price_get([template], ptype='standard_price')[template.id]
            
            #child_proc_lines.unlink()
        
        return cost

