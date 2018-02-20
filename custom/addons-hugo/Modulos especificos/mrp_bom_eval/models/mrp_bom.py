# -*- coding: utf-8 -*-

import math

from openerp import models, fields, api, exceptions, _
import openerp.addons.decimal_precision as dp

from simpleeval import simple_eval, DEFAULT_FUNCTIONS, DEFAULT_NAMES, InvalidExpression


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'
    
    qty_eval = fields.Char(
        string='Product Quantity', required=True)
    
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
    
    @api.multi
    def get_product_qty(self, production_product_attributes):
        self.ensure_one()
        
        names, functions = self._get_init_names_and_function()
        for attr_line in production_product_attributes:
            if attr_line.attr_type == 'range':
                names[self.spaceto_(attr_line.attribute.name)] = attr_line.custom_value
            elif attr_line.attr_type == 'numeric':
                names[self.spaceto_(attr_line.attribute.name)] = attr_line.value.numeric_value
        return simple_eval(self.qty_eval, names=names, functions=functions)
    
    @api.onchange('qty_eval')
    def onchange_qty_eval(self):
        for line in self:
            if not line.qty_eval or len(line.qty_eval) <= 0:
                return
            
            if line.bom_id and line.bom_id.product_tmpl_id:
                names, functions = self._get_init_names_and_function()
                if line.bom_id.product_id:
                    for attr_value in line.bom_id.product_id.attribute_value_ids:
                        if attr_value.attr_type in ('range', 'numeric'):
                            names[self.spaceto_(attr_value.attribute_id.name)] = 1
                else:
                    for attr_line in line.bom_id.product_tmpl_id.attribute_line_ids:
                        if attr_line.attribute_id.attr_type in ('range', 'numeric'):
                            names[self.spaceto_(attr_line.attribute_id.name)] = 1
                
                try:
                    simple_eval(line.qty_eval, names=names, functions=functions)
                except SyntaxError, reason:
                    raise exceptions.UserError(_('Error in the expression of the quantity formula\nReason: %s') % (reason,))
                except InvalidExpression, reason:
                    raise exceptions.UserError(_('Error in the quantity formula\nReason: %s') % (reason,))


class MrpBom(models.Model):
    _inherit='mrp.bom'
    
    def _get_possible_eval_attributes(self):
        self.possible_eval_attributes = self.env['product.attribute']. \
            search([('attr_type', '=', 'range')])
    
    attribute_eval_line_ids = fields.One2many(
        comodel_name='mrp.bom.attribute.eval.line', inverse_name='bom_id')
    possible_eval_attributes = fields.Many2many(
        comodel_name='product.attribute', compute=_get_possible_eval_attributes)
    
    @api.multi
    def _get_new_line_dict_from_proc_line(self, template, proc_line, production_proc_lines):
        self.ensure_one()
        
        res = super(MrpBom, self)._get_new_line_dict_from_proc_line(template, proc_line, production_proc_lines)
        
        if proc_line.attr_type == 'range':
            eval_line = self.attribute_eval_line_ids. \
                    filtered(lambda el: el.attribute_id == proc_line.attribute). \
                    filter_by_condition_values(production_proc_lines)
            
            if eval_line:
                new_custom_value = eval_line[0].get_line_custom_value(production_proc_lines)
                
                #new_value = proc_line.attribute.get_value_from_custom_value(new_custom_value)
                attr_line = template.attribute_line_ids.filtered(lambda l: l.attribute_id == proc_line.attribute)
                if not attr_line: #should never happen
                    raise exceptions.Warning(_('Could not find attribute line in template for specified attribute.')) #TODO use exceptions.MissingError?
                new_value = attr_line[0].get_value_from_custom_value(new_custom_value)
                if not new_value:
                     raise exceptions.Warning(_('Calculated new custom value outside the range of any attribute value.'))
                
                res['value'] = new_value.id
                res['custom_value'] = new_custom_value
        
        return res
    
    """@api.multi
    def _get_new_line_dict_from_extra_conditions(self, template, attribute, production_proc_lines):
        self.ensure_one()
        
        res = super(MrpBom, self)._get_new_line_dict_from_extra_conditions(template, attribute, production_proc_lines)
        
        if attribute.attr_type == 'range':
            eval_line = self.attribute_eval_line_ids. \
                    filtered(lambda el: el.attribute_id == attribute). \
                    filter_by_condition_values(production_proc_lines)
            
            if eval_line:
                new_custom_value = eval_line[0].get_line_custom_value(production_proc_lines)
                
                attr_line = template.attribute_line_ids.filtered(lambda l: l.attribute_id == attribute)
                if not attr_line: #should never happen
                    raise exceptions.Warning(_('Could not find attribute line in template for specified attribute.')) #TODO use exceptions.MissingError?
                new_value = attr_line[0].get_value_from_custom_value(new_custom_value)
                if not new_value:
                     raise exceptions.Warning(_('Calculated new custom value outside the range of any attribute value.'))
                
                res = self.env['procurement.attribute.line'].create_data_dict_from_value(new_value)
                res['custom_value'] = new_custom_value
        
        return res"""
    
    def _bom_eval_skip_hook(self, attr_line):
        if attr_line.attr_type == 'range':
            return True
        
        return super(MrpBom, self)._bom_eval_skip_hook(attr_line)


class MrpBomAttributeEvalLine(models.Model):
    _name = 'mrp.bom.attribute.eval.line'
    
    bom_id = fields.Many2one(
        comodel_name='mrp.bom')
    attribute_id = fields.Many2one(
        comodel_name='product.attribute', string='Attribute to modify')
    possible_eval_attributes = fields.Many2many(
        comodel_name='product.attribute')
    formula_eval = fields.Char(
        string='Formula', required=True)
    condition_value_ids = fields.Many2many(
        comodel_name='product.attribute.value', domain="[('id', 'in', possible_condition_values[0][2])]",
        string='Values condition', help="BOM Product Values needed to apply this formula.")
    possible_condition_values = fields.Many2many(
        comodel_name='product.attribute.value', compute='_get_possible_condition_values')

    @api.one
    @api.depends('bom_id.product_tmpl_id',
                 'bom_id.product_tmpl_id.attribute_line_ids')
    def _get_possible_condition_values(self):
        attr_values = self.env['product.attribute.value']
        for attr_line in self.bom_id.product_tmpl_id.attribute_line_ids:
            attr_values |= attr_line.value_ids
        self.possible_condition_values = attr_values.sorted()
    
    @api.multi
    def filter_by_condition_values(self, production_proc_lines):
        production_values = production_proc_lines.mapped('value')
        for eval_line in self:
            if all(limiting_value in production_values for limiting_value in eval_line.condition_value_ids):
                return eval_line
        return None
    
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
    
    @api.multi
    def get_line_custom_value(self, production_product_attributes):
        self.ensure_one()
        
        names, functions = self._get_init_names_and_function()
        for attr_line in production_product_attributes:
            if attr_line.attr_type == 'range':
                names[self.spaceto_(attr_line.attribute.name)] = attr_line.custom_value
            elif attr_line.attr_type == 'numeric':
                names[self.spaceto_(attr_line.attribute.name)] = attr_line.value.numeric_value
        return simple_eval(self.formula_eval, names=names, functions=functions)
    
    @api.onchange('formula_eval')
    def onchange_formula_eval(self):
        for line in self:
            if not line.formula_eval or len(line.formula_eval) <= 0:
                return
            
            if line.bom_id and line.bom_id.product_tmpl_id:
                names, functions = self._get_init_names_and_function()
                if line.bom_id.product_id:
                    for attr_value in line.bom_id.product_id.attribute_value_ids:
                        if attr_value.attr_type in ('range', 'numeric'):
                            names[self.spaceto_(attr_value.attribute_id.name)] = 1
                else:
                    for attr_line in line.bom_id.product_tmpl_id.attribute_line_ids:
                        if attr_line.attribute_id.attr_type in ('range', 'numeric'):
                            names[self.spaceto_(attr_line.attribute_id.name)] = 1
                
                try:
                    simple_eval(line.formula_eval, names=names, functions=functions)
                except SyntaxError, reason:
                    raise exceptions.UserError(_('Error in the expression of the quantity formula\nReason: %s') % (reason,))
                except InvalidExpression, reason:
                    raise exceptions.UserError(_('Error in the quantity formula\nReason: %s') % (reason,))


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def _get_inherit_value_hook(self, attr_line, proc_lines, bom):
        self.ensure_one()
        
        value = None
        attribute = attr_line.attribute_id
        
        if attribute.attr_type == 'range':
            eval_line = bom.attribute_eval_line_ids. \
                    filtered(lambda el: el.attribute_id == attribute). \
                    filter_by_condition_values(proc_lines)
            
            if eval_line:
                new_custom_value = eval_line[0].get_line_custom_value(proc_lines)
                
                value = attr_line.get_value_from_custom_value(new_custom_value)
                if not value:
                     raise exceptions.Warning(_('Calculated new custom value outside the range of any attribute value.'))
        
        return value

