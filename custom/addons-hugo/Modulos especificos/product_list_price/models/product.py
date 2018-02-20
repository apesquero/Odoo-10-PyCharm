# -*- coding: utf-8 -*-
import numbers

from openerp import models, fields, exceptions, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError

from openerp.addons.product_price_cost_base.models.simpleeval import simple_eval, InvalidExpression


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    @api.depends('table_price_items')
    def _compute_table_price_items_len(self):
        for product in self:
            product.table_price_items_len = len(product.table_price_items)
    
    @api.depends('attribute_line_ids')
    def _compute_possible_range_num_price_attribute(self):
        for product in self:
            product.possible_range_num_price_attribute = product.attribute_line_ids.mapped('attribute_id'). \
                                                            filtered(lambda a: a.attr_type in ['range','numeric']).ids
    
    price_mode = fields.Selection(
        selection=[
            ('standard', 'Standard'),
            ('table1d', 'Table1D'),
            ('table2d', 'Table2D'),
            ('area', 'Area'),
            ('formula', 'Formula')],
        string='Price Mode', required=True,
        default='standard')
    list_price_alias = fields.Float(
        string='Base List Price', digits_compute=dp.get_precision('Product Price'),
        default=0.0, groups="base.group_user",
        help="Base price of the product (also known as list price), used if the variant does not exists.")
    price_formula_eval = fields.Char(
        string='Price Formula', default='')
    possible_range_num_price_attribute = fields.Many2many(
        comodel_name='product.attribute', compute=_compute_possible_range_num_price_attribute)
    table_price_attribute_x = fields.Many2one(
        comodel_name='product.attribute', string='Attribute X')
    table_price_attribute_y = fields.Many2one(
        comodel_name='product.attribute', string='Attribute Y')
    table_price_items = fields.One2many(
        comodel_name='template.table.list.price.item', inverse_name='template_id')
    table_price_items_len = fields.Integer(
        compute=_compute_table_price_items_len, string="Items loaded")
    area_price_attribute_x = fields.Many2one(
        comodel_name='product.attribute', string='First attribute')
    area_price_x_factor = fields.Float(
        digits_compute=dp.get_precision('Product Price'), default=1.0)
    area_price_x_sum = fields.Float(
        digits_compute=dp.get_precision('Product Price'), default=0.0)
    area_price_attribute_y = fields.Many2one(
        comodel_name='product.attribute', string='Second attribute')
    area_price_y_factor = fields.Float(
        digits_compute=dp.get_precision('Product Price'), default=1.0)
    area_price_y_sum = fields.Float(
        digits_compute=dp.get_precision('Product Price'), default=0.0)
    area_price_factor = fields.Float(
        string="Factor", digits_compute=dp.get_precision('Product Price'),
        default=1.0)
    area_min_price = fields.Float(
        string="Minimum price", digits_compute=dp.get_precision('Product Price'),
        default=0.0)
    
    @api.multi
    def write(self, vals):
        old_price_modes = {}
        if 'price_mode' in vals:
            for template in self:
                old_price_modes[template.id] = template.price_mode
        
        res = super(ProductTemplate, self).write(vals)
        
        if 'list_price_alias' in vals:
            for template in self:
                for product in template.product_variant_ids:
                    product.list_price_alias = template.list_price_alias
        
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
                                        'area_price_x_factor': 1.0,
                                        'area_price_x_sum': 0.0,
                                        'area_price_attribute_y': False,
                                        'area_price_y_factor': 1.0,
                                        'area_price_y_sum': 0.0,
                                        'area_price_factor': 1.0,
                                        'area_min_price': 0.0,})
        
        return res
    
    @api.model
    def _price_get(self, products, ptype='list_price'):
        res = {}
        #if 'product_attribute_values' in self._context and ptype == 'standard_price':
        if products[0]._name == "product.template" and ptype == 'list_price':
            attr_values = self._context.get('product_attribute_values')
            
            for product in products:
                if not attr_values:
                    attr_values = product.get_minimum_attribute_values_dicts()
                
                list_price = product.get_list_price_from_attribute_values(attr_values)
                
                res.update({ product.id: list_price })
                
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
        
        return res
    
    #Price mode router
    @api.multi
    def get_list_price_from_attribute_values(self, attribute_values):
        self.ensure_one()
        
        if self.price_mode == 'standard':
            product = self.env['product.product']._product_find(self, attribute_values)
            if not product:
                return self.list_price_alias
            return product.list_price_alias
        
        elif self.price_mode == 'table1d':
            return self._get_table1d_price(attribute_values)
        
        elif self.price_mode == 'table2d':
            return self._get_table2d_price(attribute_values)
        
        elif self.price_mode == 'area':
            return self._get_area_price(attribute_values)
        
        elif self.price_mode == 'formula':
            if isinstance(attribute_values, list):
                return self._get_formula_price_from_dicts(attribute_values)
            return self._get_formula_price_from_proclines(attribute_values)
        
        else:
            raise exceptions.Warning(_("Unknown price mode"))
    
    #Formula price methods
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
            
        return simple_eval(self.price_formula_eval, names=names, functions=functions)
    
    @api.onchange('price_formula_eval')
    def onchange_price_formula_eval(self):
        if not self.price_formula_eval or len(self.price_formula_eval) <= 0:
            return
        
        names, functions = self._get_init_names_and_function()
        for attr_line in self.attribute_line_ids:
            if attr_line.attribute_id.attr_type in ('range', 'numeric'):
                names[self.spaceto_(attr_line.attribute_id.name)] = 1
        
        try:
            simple_eval(self.price_formula_eval, names=names, functions=functions)
        except SyntaxError, reason:
            raise UserError(_('Error in the expression of the quantity formula\nReason: %s') % (reason,))
        except InvalidExpression, reason:
            raise UserError(_('Error in the quantity formula\nReason: %s') % (reason,))
    
    #Table2d price methods
    @api.multi
    def _get_table2d_price(self, attribute_values):
        self.ensure_one()
        
        x_value = self._obtain_numeric_value(attribute_values, self.table_price_attribute_x)
        y_value = self._obtain_numeric_value(attribute_values, self.table_price_attribute_y)
        
        table_item = self.table_price_items.search([('template_id', '=', self.id),
                                                   ('x_upper', '>=', x_value),
                                                   ('x_lower', '<', x_value),
                                                   ('y_upper', '>=', y_value),
                                                   ('y_lower', '<', y_value)])
        if not table_item:
            table_item = self.table_price_items.search([('template_id', '=', self.id),
                                                       ('x_upper', '>=', x_value),
                                                       ('x_lower', '<=', x_value),
                                                       ('y_upper', '>=', y_value),
                                                       ('y_lower', '<=', y_value)])
        if not table_item:
            raise exceptions.Warning(_("Could not find price for those values (out of range)"))
        
        if table_item.d_mode != '2d': #should never happen
            raise exceptions.Warning(_("There was a problem loading the 2d table data. Please report the problem."))
        
        return table_item[0].price
    
    #Table1d price methods
    @api.multi
    def _get_table1d_price(self, attribute_values):
        self.ensure_one()
        
        x_value = self._obtain_numeric_value(attribute_values, self.table_price_attribute_x)
        
        table_item = self.table_price_items.search([('template_id', '=', self.id),
                                                     ('x_upper', '>=', x_value),
                                                     ('x_lower', '<', x_value),])
        if not table_item:
            table_item = self.table_price_items.search([('template_id', '=', self.id),
                                                         ('x_upper', '>=', x_value),
                                                         ('x_lower', '<=', x_value),])
        if not table_item:
            raise exceptions.Warning(_("Could not find price for those values (out of range)"))
        
        if table_item.d_mode != '1d': #should never happen
            raise exceptions.Warning(_("There was a problem loading the 1d table data. Please report the problem."))
        
        return table_item[0].price
    
    #Area price methods
    @api.multi
    def _get_area_price(self, attribute_values):
        self.ensure_one()
        
        x_value = self._obtain_numeric_value(attribute_values, self.area_price_attribute_x)
        y_value = self._obtain_numeric_value(attribute_values, self.area_price_attribute_y)
        
        res_price = ((x_value * self.area_price_x_factor) + self.area_price_x_sum) * \
            ((y_value * self.area_price_y_factor) + self.area_price_y_sum) * self.area_price_factor
        return max(self.area_min_price, res_price)


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    #we need list_price_alias becouse list_price can not be changed under certain circumstances
    list_price_alias = fields.Float(
        related='list_price', #store=True,
        string='Price', #digits_compute=dp.get_precision('Product Price'),
        #default=0.0, groups="base.group_user",
        help="Price of the product (also known as list price), in the default unit of measure of the product..")
    
    @api.model
    def create(self, values):
        product = super(ProductProduct, self).create(values)
        
        product.list_price_alias = product.product_tmpl_id.list_price_alias
        
        return product

