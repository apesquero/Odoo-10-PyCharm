# -*- coding: utf-8 -*-
import numbers

from openerp import models, fields, exceptions, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError

from openerp.addons.product_price_cost_base.models.simpleeval import simple_eval, InvalidExpression


class ProductCostExtra(models.Model):
    _name = 'product.cost.extra'
    
    product_template = fields.Many2one(
        comodel_name='product.template')
    value = fields.Many2one(
        comodel_name='product.attribute.value', string='Value')
    attribute = fields.Many2one(
        comodel_name='product.attribute', related='value.attribute_id',
        string='Attribute')
    cost_extra = fields.Float(
        string='Cost Extra', digits_compute=dp.get_precision('Product Price'),
        default=0.0)
    cost_percent_extra = fields.Float(
        string='Cost Percent Extra', digits_compute=dp.get_precision('Product Price'),
        default=0.0)


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    @api.depends('table_cost_items')
    def _compute_table_cost_items_len(self):
        for product in self:
            product.table_cost_items_len = len(product.table_cost_items)
    
    @api.depends('table_cost_items1d')
    def _compute_table_cost_items1d_len(self):
        for product in self:
            product.table_cost_items1d_len = len(product.table_cost_items1d)
    
    @api.depends('attribute_line_ids')
    def _compute_possible_range_num_cost_attribute(self):
        for product in self:
            product.possible_range_num_cost_attribute = product.attribute_line_ids.mapped('attribute_id'). \
                                                            filtered(lambda a: a.attr_type in ['range','numeric']).ids
    
    cost_extras = fields.One2many(
        comodel_name='product.cost.extra', inverse_name='product_template')
    #we need standard_price_alias becose standard_price can not be changed under certain circumstances
    standard_price_alias = fields.Float(
        string='Base Cost', digits_compute=dp.get_precision('Product Price'),
        default=0.0, groups="base.group_user",
        help="Base cost of the product, used if the variant does not exists.")
    cost_mode = fields.Selection(
        selection=[
            ('standard', 'Standard'),
            ('table1d', 'Table1D'),
            ('table2d', 'Table2D'),
            ('area', 'Area'),
            ('formula', 'Formula')],
        string='Cost Mode', required=True,
        default='standard')
    cost_formula_eval = fields.Char(
        string='Cost Formula', default='')
    possible_range_num_cost_attribute = fields.Many2many(
        comodel_name='product.attribute', compute=_compute_possible_range_num_cost_attribute)
    table_cost_attribute_x = fields.Many2one(
        comodel_name='product.attribute', string='Attribute X')
    table_cost_attribute_y = fields.Many2one(
        comodel_name='product.attribute', string='Attribute Y')
    table_cost_items = fields.One2many(
        comodel_name='template.table.cost.item', inverse_name='template_id')
    table_cost_items_len = fields.Integer(
        compute=_compute_table_cost_items_len, string="Items loaded")
    table_cost_items1d = fields.One2many(
        comodel_name='template.table.cost.item.one', inverse_name='template_id') #TODO get rid of this like in product_list_price
    table_cost_items1d_len = fields.Integer(
        compute=_compute_table_cost_items1d_len, string="Items loaded")
    area_cost_attribute_x = fields.Many2one(
        comodel_name='product.attribute', string='First attribute')
    area_x_factor = fields.Float(
        digits_compute=dp.get_precision('Product Price'), default=1.0)
    area_x_sum = fields.Float(
        digits_compute=dp.get_precision('Product Price'), default=0.0)
    area_cost_attribute_y = fields.Many2one(
        comodel_name='product.attribute', string='Second attribute')
    area_y_factor = fields.Float(
        digits_compute=dp.get_precision('Product Price'), default=1.0)
    area_y_sum = fields.Float(
        digits_compute=dp.get_precision('Product Price'), default=0.0)
    area_cost_factor = fields.Float(
        string="Factor", digits_compute=dp.get_precision('Product Price'),
        default=1.0)
    area_min_cost = fields.Float(
        string="Minimum cost", digits_compute=dp.get_precision('Product Price'),
        default=0.0)
    
    #Extras button
    @api.multi
    def action_open_cost_extras(self):
        self.ensure_one()
        
        extra_ds = self.env['product.cost.extra']
        for line in self.attribute_line_ids:
            for value in line.value_ids:
                extra = extra_ds.search([('product_template', '=', self.id),
                                           ('value', '=', value.id)])
                if not extra:
                    extra = extra_ds.create({
                        'product_template': self.id,
                        'value': value.id,
                    })
                
                extra_ds |= extra
        
        all_cost_extra = self.env['product.cost.extra']. \
            search([('product_template', '=', self.id)])
        remove_extra = all_cost_extra- extra_ds
        remove_extra.unlink()
        
        result = self._get_act_window_dict(
            'product_cost.product_cost_extra_action')
        return result
    
    @api.multi
    def _apply_extra_cost_by_mode(self):
        self.ensure_one()
        
        return True
    
    @api.model
    def _price_get(self, products, ptype='list_price'):
        res = {}
        #if 'product_attribute_values' in self._context and ptype == 'standard_price':
        if products[0]._name == "product.template" and ptype == 'standard_price':
            attr_values = self._context.get('product_attribute_values')
            
            for product in products:
                if not attr_values:
                    attr_values = product.get_minimum_attribute_values_dicts()
                
                cost = product.get_cost_from_attribute_values(attr_values)
                
                if product._apply_extra_cost_by_mode():
                    cost_extra, cost_percent_extra = product.get_all_cost_extra_from_values(attr_values)
                    cost += cost * cost_percent_extra / 100
                    cost += cost_extra
                
                res.update({ product.id: cost })
                
                if 'uom' in self._context:
                    res[product.id] = self.env['product.uom']._compute_price(self.env.cr, self.env.uid,
                            product.uom_id.id, res[product.id], self._context['uom'])
                # Convert from current user company currency to asked one
                if 'currency_id' in self._context:
                    currency_id = self.env['res.users'].browse(self.env.uid).company_id.currency_id.id
                    # Take current user company currency.
                    # This is right cause a field cannot be in more than one currency
                    res[product.id] = self.env['res.currency'].compute(self.env.cr, self.env.uid, currency_id,
                            self._context['currency_id'], res[product.id], context=self._context)
        
        else:
            res = super(ProductTemplate, self)._price_get(products, ptype)
            if ptype == 'standard_price' and products[0]._name == "product.product":
                for product in products:
                    res[product.id] += res[product.id] * product.cost_percent_extra / 100
                    res[product.id] += product.cost_extra
        return res
    
    @api.multi
    def write(self, vals):
        old_cost_modes = {}
        if 'cost_mode' in vals:
            for template in self:
                old_cost_modes[template.id] = template.cost_mode
        
        res = super(ProductTemplate, self).write(vals)
        
        if 'standard_price_alias' in vals:
            for template in self:
                for product in template.product_variant_ids:
                    product.standard_price_alias = template.standard_price_alias
        
        if 'cost_mode' in vals: #TODO check res for failure?
            for template in self:
                old_cost_mode = old_cost_modes[template.id]
                if old_cost_mode != template.cost_mode:
                    if old_cost_mode == 'table2d':
                        template.table_cost_items.unlink()
                        if template.cost_mode != 'table1d':
                            template.write({'table_cost_attribute_x': False,
                                            'table_cost_attribute_y': False,})
                        else:
                            template.table_cost_attribute_y = False
                    elif old_cost_mode == 'table1d':
                        template.table_cost_items1d.unlink()
                        if template.cost_mode != 'table2d':
                            template.table_cost_attribute_x = False
                    elif old_cost_mode == 'formula':
                        template.cost_formula_eval = ''
                    #elif old_cost_mode == 'standard':
                    #    template.standard_price_alias = 0.0
                    elif old_cost_mode == 'area':
                        template.write({'area_cost_attribute_x': False,
                                        'area_x_factor': 1.0,
                                        'area_x_sum': 0.0,
                                        'area_cost_attribute_y': False,
                                        'area_y_factor': 1.0,
                                        'area_y_sum': 0.0,
                                        'area_cost_factor': 1.0,
                                        'area_min_cost': 0.0,})
        
        return res
    
    @api.multi
    def get_all_cost_extra_from_values(self, attr_values):
        self.ensure_one()
        
        total_cost_extra = 0.0
        total_cost_percent_extra = 0.0
        if isinstance(attr_values, list):
            for value_dict in attr_values:
                cost_extra_ds = self.cost_extras.filtered(lambda ce: ce.value.id == value_dict.get('value'))
                if cost_extra_ds:
                    total_cost_extra += cost_extra_ds[0].cost_extra
                    total_cost_percent_extra += cost_extra_ds[0].cost_percent_extra
        
        else:
            for line in attr_values:
                cost_extra_ds = self.cost_extras.filtered(lambda ce: ce.value == line.value)
                if cost_extra_ds:
                    total_cost_extra += cost_extra_ds[0].cost_extra
                    total_cost_percent_extra += cost_extra_ds[0].cost_percent_extra
        
        return total_cost_extra, total_cost_percent_extra
    
    #Cost mode router
    @api.multi
    def get_cost_from_attribute_values(self, attribute_values):
        self.ensure_one()
        
        if self.cost_mode == 'standard':
            product = self.env['product.product']._product_find(self, attribute_values)
            if not product:
                return self.sudo().standard_price_alias #need sudo because unsigned users do not have read permissions to product_template
            return product.standard_price_alias
        
        elif self.cost_mode == 'table1d':
            return self._get_table1d_cost(attribute_values)
        
        elif self.cost_mode == 'table2d':
            return self._get_table2d_cost(attribute_values)
        
        elif self.cost_mode == 'area':
            return self._get_area_cost(attribute_values)
        
        elif self.cost_mode == 'formula':
            if isinstance(attribute_values, list):
                return self._get_formula_cost_from_dicts(attribute_values)
            return self._get_formula_cost_from_proclines(attribute_values)
        
        else:
            raise exceptions.Warning(_("Unknown cost mode"))
    
    #Formula Cost methods
    @api.multi
    def _get_formula_cost_from_proclines(self, attribute_values):
        self.ensure_one()
        
        names, functions = self._get_init_names_and_function()
        for attr_line in attribute_values:
            if attr_line.attr_type == 'range':
                names[self.spaceto_(attr_line.attribute.name)] = attr_line.custom_value
            elif attr_line.attr_type == 'numeric':
                names[self.spaceto_(attr_line.attribute.name)] = attr_line.value.numeric_value
        return simple_eval(self.cost_formula_eval, names=names, functions=functions)
    
    @api.multi
    def _get_formula_cost_from_dicts(self, attribute_dict_values):
        self.ensure_one()
        
        names, functions = self._get_init_names_and_function()
        for attr_dict in attribute_dict_values:
            attr_line_ds = self.attribute_line_ids.filtered(lambda l: l.attribute_id.id == attr_dict.get('attribute'))
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
            
        return simple_eval(self.cost_formula_eval, names=names, functions=functions)
    
    @api.onchange('cost_formula_eval')
    def onchange_cost_formula_eval(self):
        if not self.cost_formula_eval or len(self.cost_formula_eval) <= 0:
            return
        
        names, functions = self._get_init_names_and_function()
        for attr_line in self.attribute_line_ids:
            if attr_line.attribute_id.attr_type in ('range', 'numeric'):
                names[self.spaceto_(attr_line.attribute_id.name)] = 1
        
        try:
            simple_eval(self.cost_formula_eval, names=names, functions=functions)
        except SyntaxError, reason:
            raise UserError(_('Error in the expression of the quantity formula\nReason: %s') % (reason,))
        except InvalidExpression, reason:
            raise UserError(_('Error in the quantity formula\nReason: %s') % (reason,))
    
    #Table2d Cost methods
    @api.multi
    def _get_table2d_cost(self, attribute_values):
        self.ensure_one()
        
        x_value = self._obtain_numeric_value(attribute_values, self.table_cost_attribute_x)
        y_value = self._obtain_numeric_value(attribute_values, self.table_cost_attribute_y)
        
        table_item = self.table_cost_items.search([('template_id', '=', self.id),
                                                   ('x_upper', '>=', x_value),
                                                   ('x_lower', '<', x_value),
                                                   ('y_upper', '>=', y_value),
                                                   ('y_lower', '<', y_value)])
        if not table_item:
            table_item = self.table_cost_items.search([('template_id', '=', self.id),
                                                       ('x_upper', '>=', x_value),
                                                       ('x_lower', '<=', x_value),
                                                       ('y_upper', '>=', y_value),
                                                       ('y_lower', '<=', y_value)])
        if not table_item:
            raise exceptions.Warning(_("Could not find cost for those values (out of range)"))
        
        return table_item[0].cost
    
    #Table1d Cost methods
    @api.multi
    def _get_table1d_cost(self, attribute_values):
        self.ensure_one()
        
        x_value = self._obtain_numeric_value(attribute_values, self.table_cost_attribute_x)
        
        table_item = self.table_cost_items1d.search([('template_id', '=', self.id),
                                                     ('x_upper', '>=', x_value),
                                                     ('x_lower', '<', x_value),])
        if not table_item:
            table_item = self.table_cost_items1d.search([('template_id', '=', self.id),
                                                         ('x_upper', '>=', x_value),
                                                         ('x_lower', '<=', x_value),])
        if not table_item:
            raise exceptions.Warning(_("Could not find cost for those values (out of range)"))
        
        return table_item[0].cost
    
    #Area cost methods
    @api.multi
    def _get_area_cost(self, attribute_values):
        self.ensure_one()
        
        x_value = self._obtain_numeric_value(attribute_values, self.area_cost_attribute_x)
        y_value = self._obtain_numeric_value(attribute_values, self.area_cost_attribute_y)
        
        res_cost = ((x_value * self.area_x_factor) + self.area_x_sum) * \
            ((y_value * self.area_y_factor) + self.area_y_sum) * self.area_cost_factor
        return max(self.area_min_cost, res_cost)


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    def _compute_all_cost_extra(self): #TODO cost extra not in price_ids anymore
        cost_extra_env = self.env['product.cost.extra']
        
        for product in self:
            cost_extra = 0.0
            cost_percent_extra = 0.0
            for value in product.attribute_value_ids:
                cost_extra_ds = cost_extra_env.search([('product_template', '=', product.product_tmpl_id.id),
                                      ('value', '=', value.id)])
                if cost_extra_ds:
                    cost_extra += cost_extra_ds[0].cost_extra
                    cost_percent_extra += cost_extra_ds[0].cost_percent_extra
            
            product.cost_extra = cost_extra
            product.cost_percent_extra = cost_percent_extra
    
    cost_extra = fields.Float(
        compute=_compute_all_cost_extra, digits_compute=dp.get_precision('Product Price'))
    cost_percent_extra = fields.Float(
        compute=_compute_all_cost_extra, digits_compute=dp.get_precision('Product Price'))
    #we need standard_price_alias becose standard_price can not be changed under certain circumstances
    standard_price_alias = fields.Float(
        related='standard_price', #store=True,
        string='Cost', #digits_compute=dp.get_precision('Product Price'),
        #default=0.0, groups="base.group_user",
        help="Cost of the product, in the default unit of measure of the product..")
    
    @api.model
    def create(self, values):
        product = super(ProductProduct, self).create(values)
        
        product.standard_price_alias = product.product_tmpl_id.standard_price_alias
        
        return product

