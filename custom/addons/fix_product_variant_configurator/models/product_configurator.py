# -*- coding: utf-8 -*-
# Copyright 2018 Amaro Pesquero Rodríguez <apesquero@gmail.com>
from odoo import _, api, exceptions, fields, models
from odoo.exceptions import ValidationError


class ProductConfigurator(models.AbstractModel):
    _inherit = 'product.configurator'

    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
        required=True)

    @api.onchange('product_tmpl_id')
    def _onchange_product_tmpl_id_configurator(self):
        self.ensure_one()
        if not self.product_tmpl_id:
            self.product_id = False
            self._empty_attributes()
            # no product template: allow any product
            return {'domain': {'product_id': []}}

        if not self.product_tmpl_id.attribute_line_ids:
            # template without attribute, use the unique variant
            if self.product_tmpl_id.product_variant_ids[0].id:
                self.product_id = \
                    self.product_tmpl_id.product_variant_ids[0].id
            else:
                raise ValidationError(_("The product has not been "
                                        "previously stored."))
        else:
            # verify the product correspond to the template
            # otherwise reset it
            if (self.product_id and
                    self.product_id.product_tmpl_id != self.product_tmpl_id):
                if not self.env.context.get('not_reset_product'):
                    self.product_id = False

        # populate attributes
        if self.product_id:
            self._set_product_attributes()
        elif self.product_tmpl_id:
            self._set_product_tmpl_attributes()
        else:
            self._empty_attributes()

        # Restrict product possible values to current selection
        domain = [('product_tmpl_id', '=', self.product_tmpl_id.id)]
        return {'domain': {'product_id': domain}}
