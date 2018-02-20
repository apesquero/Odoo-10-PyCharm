# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


#http://stackoverflow.com/questions/6780952/how-to-change-behavior-of-dict-for-an-instance
class RecursiveDict(dict):
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

#https://gist.github.com/hrldcpr/2012250
#def tree():
#    return defaultdict(tree)


class ProductAttributeHierarchy (models.Model):
    _name = 'product.attribute.hierarchy'
    
    name = fields.Char(
        string="Name", required=True)
    #parent_attribute_line_ids = fields.One2many(
    #    comodel_name='hierarchy.parent.attribute.line', inverse_name='hierarchy_id',
    #    string="Rules")
    #nodes = fields.One2many(
    #    comodel_name='product.attribute.hierarchy.node', inverse_name='hierarchy_id',
    #    string="Rules")
    rule_line_ids = fields.One2many(
        comodel_name='product.attribute.hierarchy.rule', inverse_name='hierarchy_id',
        string="Rules")
    
    #@api.multi
    #def allowed_combination(self, attribute_values):
    #    self.ensure_one()
    #    
    #    if isinstance(attribute_values, list):
    #        return self.allowed_combination_from_dict(attribute_values)
    #    return self.allowed_combination_from_values(attribute_values)
    
    @api.multi
    def allowed_combination(self, attribute_values): #TODO this algo could be greatly improved for speed (probably could be done all in SQL)
        self.ensure_one()
        
        #_logger.info("allowed_combination, start, attribute_values: {av}".format(av=attribute_values))
        for value in attribute_values:
            rules_as_parent_attr = self.rule_line_ids.filtered(lambda x: x.parent_attribute_id == value.attribute_id)
            if len(rules_as_parent_attr) > 0:
                rules_as_parent_value = rules_as_parent_attr.filtered(lambda x: value in x.parent_value_ids)
                valid = {}
                for rule in rules_as_parent_value:
                    second_value = attribute_values.filtered(lambda x: x.attribute_id == rule.child_attribute_id)
                    if second_value:
                        if second_value in rule.child_value_ids:
                            valid[rule.child_attribute_id] = True
                        elif not valid.get(rule.child_attribute_id):
                            valid[rule.child_attribute_id] = False
                if not all(valid.values()):
                    return False
        return True
    
    @api.multi
    def allowed_combination_from_dict(self, attribute_values_dicts): #TODO this algo could be greatly improved for speed (probably could be done all in SQL)
        self.ensure_one()
        
        #_logger.info("allowed_combination_from_dicts, start, attribute_values: {av}".format(av=attribute_values_dicts))
        for value in attribute_values_dicts:
            rules_as_parent_attr = self.rule_line_ids.filtered(lambda x: x.parent_attribute_id.id == value['attribute'])
            if len(rules_as_parent_attr) > 0:
                rules_as_parent_value = rules_as_parent_attr.filtered(lambda x: value['value'] in x.parent_value_ids.ids) #TODO check
                valid = {}
                for rule in rules_as_parent_value:
                    #second_value = attribute_values.filtered(lambda x: x.attribute_id == rule.child_attribute_id)
                    second_value_id = next((x['value'] for x in attribute_values_dicts if x['attribute'] == rule.child_attribute_id.id), None)
                    if second_value_id:
                        if second_value_id in rule.child_value_ids.ids: #TODO check
                            valid[rule.child_attribute_id] = True
                        elif not valid.get(rule.child_attribute_id):
                            valid[rule.child_attribute_id] = False
                if not all(valid.values()):
                    return False
        return True
    
    @api.one
    def get_hierarchy_as_dict(self):
        res = RecursiveDict()
        for rule in self.rule_line_ids:
            for parent_value in rule.parent_value_ids:
                res[parent_value.id][rule.child_attribute_id.id] = \
                    res[parent_value.id].get(rule.child_attribute_id.id, []) + \
                    [x.id for x in rule.child_value_ids]
        return res


class ProductAttributeHierarchyRule(models.Model):
    _name = 'product.attribute.hierarchy.rule'
    
    @api.onchange('hierarchy_id', 'sequence')
    def _compute_allowed_parent_attribute_ids(self):
        for rule in self:
            domain = []
            if not rule.hierarchy_id: #Should never happend but the v9 x2many view is fucked up
                rule.allowed_parent_attribute_ids = self.env['product.attribute'].search([])
                return
            
            up_rules = self.env['product.attribute.hierarchy.rule'].search([
                        ('hierarchy_id', '=', rule.hierarchy_id.id),
                        ('sequence', '>', rule.sequence),
                    ]).sorted(key=lambda x: x.sequence, reverse=True)
            if up_rules:
                domain.append(('sequence', '>', up_rules[0].parent_attribute_id.sequence))
            
            res = self.env['product.attribute'].search(domain).sorted(key=lambda x: x.sequence)
            rule.allowed_parent_attribute_ids = res
    
    #def _search_allowed_parent_attribute_ids(self, operator, operand):
    #    _logger.info("search_allowed_parent_attribute_ids, operator:{operator}, operand:{operand}".format(opeartor=operator, operand=operand))
    #    return []
    
    @api.onchange('parent_attribute_id')
    def _compute_allowed_parent_value_ids(self):
        for rule in self:
            rule.allowed_parent_value_ids = rule.parent_attribute_id.value_ids
    
    @api.onchange('parent_attribute_id')
    def _compute_allowed_child_attribute_ids(self):
        for rule in self:
            if not rule.parent_attribute_id:
                rule.allowed_parent_attribute_ids = self.env['product.attribute'].search([]) #TODO should be empty, but empty does not work right now in views x2many
                return
        
            res = self.env['product.attribute'].search([
                        ('sequence', '>', rule.parent_attribute_id.sequence),
                    ]).sorted(key=lambda x: x.sequence)
            rule.allowed_child_attribute_ids = res
    
    @api.onchange('child_attribute_id')
    def _compute_allowed_child_value_ids(self):
        for rule in self:
            rule.allowed_child_value_ids = rule.child_attribute_id.value_ids
    
    hierarchy_id = fields.Many2one(
        comodel_name='product.attribute.hierarchy', string='Hierarchy')
    sequence = fields.Integer(
        string='Sequence')
    allowed_parent_attribute_ids = fields.Many2many(
        comodel_name='product.attribute', compute=_compute_allowed_parent_attribute_ids)
    parent_attribute_id = fields.Many2one(
        comodel_name='product.attribute', string='Parent Attribute',
        required=True)
    allowed_parent_value_ids = fields.Many2many(
        comodel_name='product.attribute.value', compute=_compute_allowed_parent_value_ids)
    parent_value_ids = fields.Many2many(
        comodel_name='product.attribute.value', string='Parent Values',
        relation='attribute_hierarchy_rule_parent_values') #TODO required?
    allowed_child_attribute_ids = fields.Many2many(
        comodel_name='product.attribute', compute=_compute_allowed_child_attribute_ids)
    child_attribute_id = fields.Many2one(
        comodel_name='product.attribute', string='Child Attribute',
        required=True)
    allowed_child_value_ids = fields.Many2many(
        comodel_name='product.attribute.value', compute=_compute_allowed_child_value_ids)
    child_value_ids = fields.Many2many(
        comodel_name='product.attribute.value', string='Child Values',
        relation='attribute_hierarchy_rule_child_values') #TODO required?


"""class ProductAttributeHierarchyNode (models.Model):
    _name = 'product.attribute.hierarchy.node'

    @api.multi
    @api.depends('parent_id', 'parent_id.level')
    def _get_level(self):
        '''Returns a dictionary with key=the ID of a record and value = the level of this  
           record in the tree structure.'''
        for node in self:
            level = 0
            if node.parent_id:
                level = node.parent_id.level + 1
            node.level = level
    
    hierarchy_id = fields.Many2one(
        comodel_name='product.attribute.hierarchy', string='Hierarchy')
    parent_id = fields.Many2one(
        comodel_name='product.attribute.hierarchy.node')
    child_ids = fields.One2many(
        comodel_name='product.attribute.hierarchy.node', inverse_name='parent_id')
    level = fields.Integer(compute='_get_level', string='Level', store=True)
    sequence = fields.Integer('Sequence')
    #type = fields.Selection([
    #    ('parent_attr', 'Parent Attribute Node'),
    #    ('parent_value', 'Parent Value Node'),
    #    ('child', 'Child Node'),
    #    ('account_report', 'Report Value'),
    #    ], 'Type', default='sum')
    parent_attribute_id = fields.Many2one(
        comodel_name='product.attribute', string='Parent Attribute',
        required=True)
    parent_value_ids = fields.Many2many(
        comodel_name='product.attribute.value', string='Parent Values')
    child_attribute_id = fields.Many2one(
        comodel_name='product.attribute', string='Child Attribute',
        required=True)
    child_value_ids = fields.Many2many(
        comodel_name='product.attribute.value', string='Child Values')"""

"""class HierarchyParentAttributeLine (models.Model):
    _name = 'hierarchy.parent.attribute.line'
    
    hierarchy_id = fields.Many2one(
        comodel_name='product.attribute.hierarchy', string='Hierarchy')
    parent_attribute_id = fields.Many2one(
        comodel_name='product.attribute', string='Parent Attribute',
        required=True)
    parent_values_line_ids = fields.One2many(
        comodel_name='hierarchy.parent.value.line', inverse_name='parent_attribute_line',
        string="Parent Value Lines")
    #TODO reference for the order

class HierarchyParentValueLine (models.Model):
    _name = 'hierarchy.parent.value.line'
    
    parent_attribute_line = fields.Many2one(
        comodel_name='hierarchy.parent.attribute.line', string='Parent Attribute')
    parent_attribute_id = fields.Many2one(
        related='parent_attribute_line.parent_attribute_id', store=True)
    parent_value_ids = fields.Many2many(
        comodel_name='product.attribute.value', string='Parent Values')
    child_line_ids = fields.One2many(
        comodel_name='hierarchy.child.line', inverse_name='parent_value_line',
        string="Child Lines", oldname='child_attribute_line_ids')

class HierarchyChildLine (models.Model):
    _name = 'hierarchy.child.line'
    
    parent_value_line = fields.Many2one(
        comodel_name='hierarchy.parent.value.line', string='Parent Value')
    child_attribute_id = fields.Many2one(
        comodel_name='product.attribute', string='Child Attribute',
        required=True)
    child_value_ids = fields.Many2many(
        comodel_name='product.attribute.value', string='Child Values')"""

