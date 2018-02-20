# -*- coding: utf-8 -*-
from openerp import models, fields, exceptions, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    price_mode = fields.Selection(
        selection_add=[('bom', 'BoM'),])
    
    #Price mode router
    @api.multi
    def get_list_price_from_attribute_values(self, attribute_values):
        self.ensure_one()
        
        if self.price_mode == 'bom':
            unlink_attr = False
            if isinstance(attribute_values, list):
                proc_attributes = self._get_procurement_values_from_dict(attribute_values)
                unlink_attr = True
            else:
                proc_attributes = attribute_values
            
            price = self.sudo()._get_bom_list_price_from_proclines(proc_attributes)
            
            if unlink_attr:
                proc_attributes.unlink()
            
            return price
        
        return super(ProductTemplate, self).get_list_price_from_attribute_values(attribute_values)
    
    #BoM Price Methods
    @api.multi
    def _get_bom_list_price_from_proclines(self, proc_lines):
        self.ensure_one()
        
        bom_obj = self.env['mrp.bom']
        bom_id = bom_obj._bom_find(product_tmpl_id=self.id)
        bom = bom_obj.browse(bom_id)
        factor = 1 #TODO maybe but corrected self.env['product.uom']._compute_qty(product_uom.id, product_qty, bom.product_uom.id) / bom.product_qty
        result1, result2 = self.env['mrp.bom'].with_context(
                                   production_product_attributes = proc_lines,
                                   bom_explode_no_create_new_product = True,
                               )._bom_explode(bom, False, factor)
        
        price = 0
        for child_item in result1:
            template = self.browse(child_item['product_tmpl_id'])
            
            child_value_dicts = []
            for values_dict in child_item['product_attributes']:
                child_value_dicts.append(values_dict[2])
            
            price += child_item['product_qty'] * \
                    template.with_context( {},
                        product_attribute_values=child_value_dicts
                    )._price_get([template], ptype='list_price')[template.id]
        
        return price

