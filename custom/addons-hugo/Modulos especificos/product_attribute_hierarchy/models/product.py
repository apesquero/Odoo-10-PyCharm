# -*- coding: utf-8 -*-

from openerp import models, fields, api, _, exceptions, tools
import psycopg2


class ProductTemplate (models.Model):
    _inherit = 'product.template'
    
    attribute_hierarchy_id = fields.Many2one(
        comodel_name='product.attribute.hierarchy', string='Attribute Hierarchy')
    
    @api.multi
    def write(self, values):
        res = super(ProductTemplate, self).write(values)
        
        if 'attribute_hierarchy_id' in values:
            self.check_defaults_respect_hierarchy()
            self.create_variant_ids()
        
        return res
    
    @api.multi
    def check_defaults_respect_hierarchy(self):
        for template in self:
            value_ds = template.attribute_line_ids.mapped('default')
            if not template.allowed_by_attr_hierarchy(value_ds):
                raise exceptions.UserError(_('The default values you have selected are not allowed by the hierarchy. Set a valid combination.'))
    
    def allowed_by_attr_hierarchy(self, attribute_value_ids):
        if not self.attribute_hierarchy_id:
            return True
        
        return self.attribute_hierarchy_id.allowed_combination(attribute_value_ids)
    
    def allowed_by_attr_hierarchy_from_dicts(self, attribute_value_dicts):
        if not self.attribute_hierarchy_id:
            return True
        
        return self.attribute_hierarchy_id.allowed_combination_from_dict(attribute_value_dicts)
    
    @api.multi
    def create_variant_ids(self):
        product_obj = self.env["product.product"]
        if self.env.context.get("create_product_variant"):
            return None
        
        for tmpl_id in self:
            if ((tmpl_id.no_create_variants == 'empty' and
                    not tmpl_id.categ_id.no_create_variants) or
                    (tmpl_id.no_create_variants == 'no')):
                pass
            else:
                #checking all active models respect the hierarchy
                for product_id in tmpl_id.product_variant_ids:
                    if not self.allowed_by_attr_hierarchy(product_id.attribute_value_ids):
                        try:
                            with self.env.cr.savepoint(), tools.mute_logger('openerp.sql_db'):
                                variant.with_context(
                                        active_test=False,
                                        create_product_variant=True
                                ).unlink()
                        #We catch all kind of exception to be sure that the operation doesn't fail.
                        except (psycopg2.Error, exceptions.except_orm):
                            variant.with_context(
                                    active_test=False,
                                    create_product_variant=True
                                ).write({'active': False})
                            pass
                return True
            
            # list of values combination
            variant_alone = []
            all_variants = [[]]
            for variant_id in tmpl_id.attribute_line_ids:
                if len(variant_id.value_ids) == 1:
                    variant_alone.append(variant_id.value_ids[0])
                temp_variants = []
                for variant in all_variants:
                    for value_id in variant_id.value_ids:
                        temp_variants.append(sorted(variant + [int(value_id)]))
                if temp_variants:
                    all_variants = temp_variants

            # adding an attribute with only one value should not recreate product
            # write this attribute on every product to make sure we don't lose them
            for variant_id in variant_alone:
                product_ids = []
                for product_id in tmpl_id.product_variant_ids:
                    if variant_id.id not in map(int, product_id.attribute_value_ids) and product_id.active == True:
                        product_ids.append(product_id.id)
                products = product_obj.browse(product_ids)
                products.with_context(
                        active_test=False,
                        create_product_variant=True
                    ).write({'attribute_value_ids': [(4, variant_id.id)]})

            # check product
            variant_ids_to_active = []
            variants_active_ids = []
            variants_inactive = []
            for product_id in tmpl_id.product_variant_ids:
                variants = sorted(map(int,product_id.attribute_value_ids))
                if variants in all_variants and self.allowed_by_attr_hierarchy(product_id.attribute_value_ids):
                    variants_active_ids.append(product_id.id)
                    all_variants.pop(all_variants.index(variants))
                    if not product_id.active:
                        variant_ids_to_active.append(product_id.id)
                else:
                    variants_inactive.append(product_id)
            if variant_ids_to_active:
                variants_to_active = product_obj.browse(variant_ids_to_active)
                variants_to_active.with_context(
                        active_test=False,
                        create_product_variant=True
                    ).write({'active': True})

            # create new product
            for variants in all_variants:
                #if self.allowed_by_attr_hierarchy(variants):
                if self.allowed_by_attr_hierarchy(self.env['product.attribute.value'].browse(variants)):
                    values = {
                        'product_tmpl_id': tmpl_id.id,
                        'attribute_value_ids': [(6, 0, variants)]
                    }
                    id = product_obj.with_context(
                            active_test=False,
                            create_product_variant=True
                        ).create(values)
                    variants_active_ids.append(id)

            # unlink or inactive product
            for variant in product_obj.browse(map(int,variants_inactive)):
                try:
                    with self.env.cr.savepoint(), tools.mute_logger('openerp.sql_db'):
                        variant.with_context(
                                active_test=False,
                                create_product_variant=True
                            ).unlink()
                #We catch all kind of exception to be sure that the operation doesn't fail.
                except (psycopg2.Error, exceptions.except_orm):
                    variant.with_context(
                                active_test=False,
                                create_product_variant=True
                            ).write({'active': False})
                    pass
        return True
    
    """@api.multi
    def create_variant_ids(self):
        product_obj = self.env["product.product"]
        if self.env.context.get("create_product_variant"):
            return None

        for tmpl_id in self:
            # list of values combination
            variant_alone = []
            all_variants = [[]]
            for variant_id in tmpl_id.attribute_line_ids:
                if len(variant_id.value_ids) == 1:
                    variant_alone.append(variant_id.value_ids[0])
                temp_variants = []
                for variant in all_variants:
                    for value_id in variant_id.value_ids:
                        temp_variants.append(sorted(variant + [int(value_id)]))
                if temp_variants:
                    all_variants = temp_variants

            # adding an attribute with only one value should not recreate product
            # write this attribute on every product to make sure we don't lose them
            for variant_id in variant_alone:
                product_ids = []
                for product_id in tmpl_id.product_variant_ids:
                    if variant_id.id not in map(int, product_id.attribute_value_ids):
                        product_ids.append(product_id.id)
                products = product_obj.browse(product_ids)
                products.with_context(
                        active_test=False,
                        create_product_variant=True
                    ).write({'attribute_value_ids': [(4, variant_id.id)]})

            # check product
            variant_ids_to_active = []
            variants_active_ids = []
            variants_inactive = []
            for product_id in tmpl_id.product_variant_ids:
                variants = sorted(map(int,product_id.attribute_value_ids))
                if variants in all_variants and self.allowed_by_attr_hierarchy(variants):
                    variants_active_ids.append(product_id.id)
                    all_variants.pop(all_variants.index(variants))
                    if not product_id.active:
                        variant_ids_to_active.append(product_id.id)
                else:
                    variants_inactive.append(product_id)
            if variant_ids_to_active:
                variants_to_active = product_obj.browse(variant_ids_to_active)
                variants_to_active.with_context(
                        active_test=False,
                        create_product_variant=True
                    ).write({'active': True})

            # create new product
            for variants in all_variants:
                if self.allowed_by_attr_hierarchy(variants):
                    values = {
                        'product_tmpl_id': tmpl_id.id,
                        'attribute_value_ids': [(6, 0, variants)]
                    }
                    id = product_obj.with_context(
                            active_test=False,
                            create_product_variant=True
                        ).create(values)
                    variants_active_ids.append(id)

            # unlink or inactive product
            for variant in product_obj.browse(map(int,variants_inactive)):
                try:
                    with self.env.cr.savepoint(), tools.mute_logger('openerp.sql_db'):
                        variant.with_context(
                                active_test=False,
                                create_product_variant=True
                            ).unlink()
                #We catch all kind of exception to be sure that the operation doesn't fail.
                except (psycopg2.Error, exceptions.except_orm):
                    variant.with_context(
                                active_test=False,
                                create_product_variant=True
                            ).write({'active': False})
                    pass
        return True"""


class ProductProduct (models.Model):
    _inherit = 'product.product'
    
    @api.one
    @api.constrains('attribute_value_ids')
    def _check_attribute_hierarchy(self):
        #The hierarchy is already checked in create_variant_ids
        if self.env.context.get('create_product_variant'):
            return True
        return self.product_tmpl_id.allowed_by_attr_hierarchy(self.attribute_value_ids)

class ProductAttributeLine(models.Model):
    _inherit = "product.attribute.line"

    default = fields.Many2one(
        comodel_name='product.attribute.value', string='Default')
    required = fields.Boolean(
        string='Required', default=True)
    
    @api.onchange('attribute_id', 'value_ids')
    def automatic_set_default(self):
        if self.default and self.default.attribute_id == self.attribute_id and self.default in self.value_ids:
            return
        
        if len(self.value_ids) > 0:
            self.default = self.value_ids[0]
        else:
            self.default = False
    
    @api.multi
    def write(self, values):
        res = super(ProductAttributeLine, self).write(values)
        
        if 'default' in values:
            affected_templates = {}
            for line in self:
                affected_templates.setdefault(line.product_tmpl_id.id, line.product_tmpl_id)
            for template_id, template in affected_templates.iteritems():
                template.check_defaults_respect_hierarchy()
        
        return res

