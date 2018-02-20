# -*- coding: utf-8 -*-
import numbers
import math

from openerp import models, fields, exceptions, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError

from simpleeval import simple_eval, DEFAULT_FUNCTIONS, DEFAULT_NAMES, InvalidExpression


class SupplierinfoValueExtra(models.Model):
    _name = 'supplierinfo.value.extra'
    
    supplierinfo = fields.Many2one(
        comodel_name='product.supplierinfo')
    value = fields.Many2one(
        comodel_name='product.attribute.value', string='Value')
    attribute = fields.Many2one(
        comodel_name='product.attribute', related='value.attribute_id',
        string='Attribute')
    price_extra = fields.Float(
        string='Supplier Price Extra', digits_compute=dp.get_precision('Product Price'),
        default=0.0)
    price_percent_extra = fields.Float(
        string='Supplier Price Percent Extra', digits_compute=dp.get_precision('Product Price'),
        default=0.0)

class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'
    
    @api.depends('table_price_items')
    def _compute_table_price_items_len(self):
        for supplierinfo in self:
            supplierinfo.table_price_items_len = len(supplierinfo.table_price_items)
    
    @api.depends('product_tmpl_id.attribute_line_ids')
    def _compute_possible_range_num_price_attribute(self):
        for supplierinfo in self:
            supplierinfo.possible_range_num_price_attribute = supplierinfo.product_tmpl_id.attribute_line_ids.mapped('attribute_id'). \
                                                                  filtered(lambda a: a.attr_type in ['range','numeric']).ids
            #print supplierinfo.possible_range_num_price_attribute
    
    extras = fields.One2many(
        comodel_name='supplierinfo.value.extra', inverse_name='supplierinfo')
    price_mode = fields.Selection(
        selection=[
            ('standard', 'Standard'),
            ('table1d', 'Table1D'),
            ('table2d', 'Table2D'),
            ('area', 'Area'),
            ('formula', 'Formula')],
        string='Price Mode', required=True,
        default='standard')
    price_formula_eval = fields.Char(
        string='Price Formula', default='')
    possible_range_num_price_attribute = fields.Many2many(
        comodel_name='product.attribute', compute=_compute_possible_range_num_price_attribute)
    table_price_attribute_x = fields.Many2one(
        comodel_name='product.attribute', string='Attribute X')
    table_price_attribute_y = fields.Many2one(
        comodel_name='product.attribute', string='Attribute Y')
    table_price_items = fields.One2many(
        comodel_name='suppliers.table.price.item', inverse_name='supplierinfo')
    table_price_items_len = fields.Integer(
        compute=_compute_table_price_items_len, string="Items loaded")
    area_price_attribute_x = fields.Many2one(
        comodel_name='product.attribute', string='First attribute')
    area_x_factor = fields.Float(
        digits_compute=dp.get_precision('Product Price'), default=1.0)
    area_x_sum = fields.Float(
        digits_compute=dp.get_precision('Product Price'), default=0.0)
    area_price_attribute_y = fields.Many2one(
        comodel_name='product.attribute', string='Second attribute')
    area_y_factor = fields.Float(
        digits_compute=dp.get_precision('Product Price'), default=1.0)
    area_y_sum = fields.Float(
        digits_compute=dp.get_precision('Product Price'), default=0.0)
    area_price_factor = fields.Float(
        string="Factor", digits_compute=dp.get_precision('Product Price'),
        default=1.0)
    area_min_price = fields.Float(
        string="Minimum Price", digits_compute=dp.get_precision('Product Price'),
        default=0.0)
    
    @api.multi
    def write(self, vals):
        old_price_modes = {}
        if 'price_mode' in vals:
            for template in self:
                old_price_modes[template.id] = template.price_mode
        
        res = super(ProductSupplierinfo, self).write(vals)
        
        if 'price_mode' in vals:
            for template in self:
                old_price_mode = old_price_modes[template.id]
                if old_price_mode != template.price_mode:
                    if old_price_mode == 'table2d':
                        if template.price_mode == 'table1d':
                            if template.table_price_items_len > 0 \
                                    and template.table_price_items[0].d_mode == '2d':
                                template.table_price_items.unlink()
                            template.table_price_attribute_y = False
                        
                        else:
                            template.table_price_items.unlink()
                            template.write({'table_price_attribute_x': False,
                                            'table_price_attribute_y': False,})
                    
                    elif old_price_mode == 'table1d':
                        if template.price_mode == 'table2d':
                            if template.table_price_items_len > 0 \
                                    and template.table_price_items[0].d_mode == '1d':
                                template.table_price_items.unlink()
                        else:
                            template.table_price_attribute_x = False
                            template.table_price_items.unlink()
                    
                    elif old_price_mode == 'formula':
                        template.price_formula_eval = ''
                    
                    #elif old_price_mode == 'standard':
                    #    template.standard_price_alias = 0.0
                    
                    elif old_price_mode == 'area':
                        template.write({'area_price_attribute_x': False,
                                        'area_x_factor': 1.0,
                                        'area_x_sum': 0.0,
                                        'area_price_attribute_y': False,
                                        'area_y_factor': 1.0,
                                        'area_y_sum': 0.0,
                                        'area_price_factor': 1.0,
                                        'area_min_price': 0.0,})
        
        return res
    
    def get_price(self, proc_lines=[]):
        self.ensure_one()
        
        new_price = self.get_price_from_proclines(proc_lines)
        
        #extra
        if self.product_id:
            for value in self.product_id.attribute_value_ids:
                extra = self.extras.filtered(lambda e: e.value == value)
                if extra:
                    new_price += extra.price_extra
                    new_price += new_price * extra.price_percent_extra / 100
        
        else:
            for line in proc_lines:
                if isinstance(line, dict):
                    extra = self.extras.filtered(lambda e: e.value.id == line['value'])
                else:
                    extra = self.extras.filtered(lambda e: e.value == line.value)
                if extra:
                    new_price += extra.price_extra
                    new_price += new_price * extra.price_percent_extra / 100
        
        return new_price
    
    #Price mode router
    @api.multi
    def get_price_from_proclines(self, procurement_value_lines):
        self.ensure_one()
        
        if self.price_mode == 'standard':
            return self.price
        
        elif self.price_mode == 'table1d':
            return self._get_table1d_price(procurement_value_lines)
        
        elif self.price_mode == 'table2d':
            return self._get_table2d_price(procurement_value_lines)
        
        elif self.price_mode == 'area':
            return self._get_area_price(procurement_value_lines)
        
        elif self.price_mode == 'formula':
            if isinstance(procurement_value_lines, list):
                return self._get_formula_price_from_dicts(procurement_value_lines)
            return self._get_formula_price_from_proclines(procurement_value_lines)
        
        else:
            raise exceptions.Warning(_("Unknown supplier price mode"))
    
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
    
    #Formula price methods
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
    def _get_formula_price_from_proclines(self, attribute_values):
        self.ensure_one()
        
        names, functions = self._get_init_names_and_function()
        for attr_line in attribute_values:
            if attr_line.attr_type == 'range':
                names[self.spaceto_(attr_line.attribute.name)] = attr_line.custom_value
            elif attr_line.attr_type == 'numeric':
                names[self.spaceto_(attr_line.attribute.name)] = attr_line.value.numeric_value
        return simple_eval(self.price_formula_eval, names=names, functions=functions)
    
    @api.multi
    def _get_formula_price_from_dicts(self, attribute_dict_values):
        self.ensure_one()
        
        names, functions = self._get_init_names_and_function()
        for attr_dict in attribute_dict_values:
            attr_line_ds = self.product_tmpl_id.attribute_line_ids.filtered(lambda l: l.attribute_id.id == attr_dict.get('attribute'))
            if not attr_line_ds:
                raise exceptions.Warning(_("Could not find attribute in product."))
            
            if attr_line_ds[0].attr_type == 'range':
                numeric_value = attr_dict.get('r', False) or attr_dict.get('custom_value')
            elif attr_line_ds[0].attr_type == 'numeric':
                value_ds = attr_line_ds[0].attribute_id.value_ids.filtered(lambda v: v.id == attr_dict.get('value'))
                if not value_ds:
                    raise exceptions.Warning(_("Could not find value in attribute."))
                numeric_value = value_ds[0].numeric_value
            else:
                continue
            
            if numeric_value is None:
                raise exceptions.Warning(_("Numeric value is None."))
            if not isinstance(numeric_value, numbers.Number):
                raise exceptions.Warning(_("Numeric value is not a number"))
            
            names[self.spaceto_(attr_line_ds[0].attribute_id.name)] = numeric_value
            
        return simple_eval(self.price_formula_eval, names=names, functions=functions)
    
    @api.onchange('price_formula_eval')
    def onchange_price_formula_eval(self):
        if not self.price_formula_eval or len(self.price_formula_eval) <= 0:
            return
        
        names, functions = self._get_init_names_and_function()
        for attr_line in self.product_tmpl_id.attribute_line_ids:
            if attr_line.attribute_id.attr_type in ('range', 'numeric'):
                names[self.spaceto_(attr_line.attribute_id.name)] = 1
        
        try:
            simple_eval(self.price_formula_eval, names=names, functions=functions)
        except SyntaxError, reason:
            raise UserError(_('Error in the expression of the quantity formula\nReason: %s') % (reason,))
        except InvalidExpression, reason:
            raise UserError(_('Error in the quantity formula\nReason: %s') % (reason,))
    
    #Table2d Price methods
    @api.multi
    def _get_table2d_price(self, attribute_values):
        self.ensure_one()
        
        x_value = self._obtain_numeric_value(attribute_values, self.table_price_attribute_x)
        y_value = self._obtain_numeric_value(attribute_values, self.table_price_attribute_y)
        
        table_item = self.table_price_items.search([('supplierinfo', '=', self.id),
                                                   ('x_upper', '>=', x_value),
                                                   ('x_lower', '<', x_value),
                                                   ('y_upper', '>=', y_value),
                                                   ('y_lower', '<', y_value)])
        if not table_item:
            table_item = self.table_price_items.search([('supplierinfo', '=', self.id),
                                                       ('x_upper', '>=', x_value),
                                                       ('x_lower', '<=', x_value),
                                                       ('y_upper', '>=', y_value),
                                                       ('y_lower', '<=', y_value)])
        if not table_item:
            raise exceptions.Warning(_("Could not find supplier price for those values (out of range)"))
        
        if table_item.d_mode != '2d': #should never happen
            raise exceptions.Warning(_("There was a problem loading the 2d table data. Please report the problem."))
        
        return table_item[0].price
    
    #Table1d price methods
    @api.multi
    def _get_table1d_price(self, attribute_values):
        self.ensure_one()
        
        x_value = self._obtain_numeric_value(attribute_values, self.table_price_attribute_x)
        
        table_item = self.table_price_items.search([('supplierinfo', '=', self.id),
                                                     ('x_upper', '>=', x_value),
                                                     ('x_lower', '<', x_value),])
        if not table_item:
            table_item = self.table_price_items.search([('supplierinfo', '=', self.id),
                                                         ('x_upper', '>=', x_value),
                                                         ('x_lower', '<=', x_value),])
        if not table_item:
            raise exceptions.Warning(_("Could not find supplier price for those values (out of range)"))
        
        if table_item.d_mode != '1d': #should never happen
            raise exceptions.Warning(_("There was a problem loading the 1d table data. Please report the problem."))
        
        return table_item[0].price
    
    #Area price methods
    @api.multi
    def _get_area_price(self, attribute_values):
        self.ensure_one()
        
        x_value = self._obtain_numeric_value(attribute_values, self.area_price_attribute_x)
        y_value = self._obtain_numeric_value(attribute_values, self.area_price_attribute_y)
        
        res_price = ((x_value * self.area_x_factor) + self.area_x_sum) * \
            ((y_value * self.area_y_factor) + self.area_y_sum) * self.area_price_factor
        return max(self.area_min_price, res_price)
    
    #Extras button
    @api.multi
    def action_open_value_extras(self):
        self.ensure_one()
        
        extra_ds = self.env['supplierinfo.value.extra']
        for line in self.product_tmpl_id.attribute_line_ids:
            for value in line.value_ids:
                extra = extra_ds.search([('supplierinfo', '=', self.id),
                                           ('value', '=', value.id)])
                if not extra:
                    extra = extra_ds.create({
                        'supplierinfo': self.id,
                        'value': value.id,
                    })
                
                extra_ds |= extra
        
        all_supplierinfo_extra = self.env['supplierinfo.value.extra']. \
            search([('supplierinfo', '=', self.id)])
        remove_extra = all_supplierinfo_extra- extra_ds
        remove_extra.unlink()
        
        result = self.product_tmpl_id._get_act_window_dict(
            'supplier_price.value_extra_action')
        return result

