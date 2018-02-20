# -*- coding: utf-8 -*-
import numbers
import math

from openerp import models, fields, exceptions, api, _

from simpleeval import DEFAULT_FUNCTIONS, DEFAULT_NAMES


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    @api.multi
    def get_minimum_attribute_values_dicts(self): #TODO done in another module
        self.ensure_one()
        
        res = []
        for attr_line in self.attribute_line_ids:
            value = attr_line.default or attr_line.value_ids[0] or False
            if not value:
                continue
            
            value_dict = self.env['procurement.attribute.line'].create_data_dict_from_value(value)
            res.append(value_dict)
        
        return res
    
    #Shared methods
    @staticmethod
    def _obtain_numeric_value(attribute_values, attribute):
        
        if isinstance(attribute_values, list):
            attr_x_dict = next((v for v in attribute_values if v['attribute'] == attribute.id), None)
            if attr_x_dict is None:
                raise exceptions.Warning(_("Could not find attribute."))
            x_value = None
            if attribute.attr_type == 'range':
                x_value = attr_x_dict.get('r', False) or attr_x_dict.get('custom_value')
            elif attribute.attr_type == 'numeric':
                x_value_ds = attribute.value_ids.filtered(lambda v: v.id == attr_x_dict['value'])
                if not x_value_ds:
                    raise exceptions.Warning(_("Value ds for attribute incorrect."))
                x_value = x_value_ds[0].numeric_value
            if x_value is None:
                raise exceptions.Warning(_("Custom value for attribute not present."))
            if not isinstance(x_value, numbers.Number):
                raise exceptions.Warning(_("Custom value for attribute not a number."))
        
        else:
            x_line_ds = attribute_values.filtered(lambda l: l.attribute == attribute)
            if not x_line_ds:
                raise exceptions.Warning(_("Could not find attribute."))
            if x_line_ds[0].attr_type == 'range':
                x_value = x_line_ds[0].custom_value
            elif x_line_ds[0].attr_type == 'numeric':
                x_value = x_line_ds[0].value.numeric_value
            else:
                raise exceptions.Warning(_('Non range or numeric attribute.')) #should never happen
        
        return x_value
    
    #Formula methods
    @staticmethod
    def _get_init_names_and_function():
        functions = {'ceil': math.ceil, 'max': max, 'min': min}
        functions.update(DEFAULT_FUNCTIONS)
        names = {}
        names.update(DEFAULT_NAMES)
        return (names, functions)
    
    @staticmethod
    def spaceto_(string):
        return "_".join(string.split())
    
    #This is only necessary for the bom modules but fits better here
    @api.multi
    def _get_procurement_values_from_dict(self, attribute_value_dicts):
        self.ensure_one()
        
        proc_attributes_rs = self.env['procurement.attribute.line']
        for value_dict in attribute_value_dicts:
            value_id = value_dict.get('value')
            if value_id is None:
                raise exceptions.Warning(_("Could not find value id"))
            if not isinstance(value_id, int):
                raise exceptions.Warning(_("Value id not an int"))
            
            attribute_id = value_dict.get('attribute')
            if attribute_id is None:
                raise exceptions.Warning(_("Could not find attribute id"))
            if not isinstance(attribute_id, int):
                raise exceptions.Warning(_("Attribute id not an int"))
            
            custom_value = value_dict.get('r', False) or value_dict.get('custom_value', False)
            
            temp_rs = self.env['procurement.attribute.line'].create({'product_template_id' : self.id, #TODO catch error in case custom_value wrong
                                                                     'attribute': attribute_id,
                                                                     'value': value_id,
                                                                     'custom_value': custom_value,
                                                                    })
            
            proc_attributes_rs |= temp_rs
        
        return proc_attributes_rs

