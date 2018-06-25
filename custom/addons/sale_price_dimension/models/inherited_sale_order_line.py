# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    origin_width = fields.Float(string="Width", required=True, default=0.0)
    origin_height = fields.Float(string="Height", required=True, default=0.0)

    product_price_type = fields.Selection([('standard', 'Standard'),
                                           ('table_1d', '1D Table'),
                                           ('table_2d', '2D Table'),
                                           ('area', 'Area')],
                                          string='Sale Price Type',
                                          related='product_tmpl_id.sale_price_type')

    @api.constrains('origin_width', 'origin_height')
    def _check_origin_dimensions_constrains(self):
        for record in self:
            if not record.product_id.origin_check_sale_dim_values(
                    record.origin_width, record.origin_height):
                raise ValidationError(_("Invalid dimension in:\n%s!") % self.product_id.name_get()[0][1])

    @api.onchange('product_id',
                  'origin_width',
                  'origin_height',
                  'product_attribute_ids')
    def product_id_change(self):
        super(SaleOrderLine, self).product_id_change()
        product_tmp = False
        if not self.product_tmpl_id or (self.product_id and \
                                        self.product_id.product_tmpl_id.id != \
                                        self.product_id.product_tmpl_id.id):
            return
        if self.can_create_product:
            try:
                with self.env.cr.savepoint():
                    product_tmp = self.product_id = self.create_variant_if_needed()
            except ValidationError as e:
                return {'warning': {
                    'title': _('Product not created!'),
                    'message': e.name,
                }}
        vals = {}
        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,

            width=self.origin_width,
            height=self.origin_height
        )

        if self.product_tmpl_id.sale_price_type not in ['table_1d', 'table_2d', 'area']:
            self.origin_height = self.origin_width = 0


        name = ''
        if self.product_id:
            name = product.name_get()[0][1]
        if product.sale_price_type in ['table_2d', 'area']:
            height_uom = product.height_uom.name
            width_uom = product.width_uom.name
            name += _(' [Width:%.2f %s x Height:%.2f %s]') % \
                    (self.origin_width, width_uom, self.origin_height, height_uom)
        elif product.sale_price_type == 'table_1d':
            width_uom = product.width_uom.name
            name += _(' [ Width:%.2f %s]') % (self.origin_width, width_uom)
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax'].\
                _fix_tax_included_price_company(self._get_display_price(product),
                                                product.taxes_id,
                                                self.tax_id,
                                                self.company_id)

        self.update(vals)

    @api.onchange('origin_width',
                  'origin_height')
    def _check_origin_dimensions(self):
        if self.product_id and self.product_id.sale_price_type in ['table_1d', 'table_2d']:
            max_width = self.product_id.get_sale_price_table_headers()['x'][-1]
            if self.product_id.get_sale_price_table_headers()['x'][0] == 0:
                min_width = self.product_id.get_sale_price_table_headers()['x'][1]
            else:
                min_width = self.product_id.get_sale_price_table_headers()['x'][0]

        if self.product_id and self.product_id.sale_price_type in ['table_2d']:
            max_height = self.product_id.get_sale_price_table_headers()['y'][-1]
            if self.product_id.get_sale_price_table_headers()['y'][0] == 0:
                min_height = self.product_id.get_sale_price_table_headers()['y'][1]
            else:
                min_height = self.product_id.get_sale_price_table_headers()['y'][0]

        if self.product_id and self.product_id.sale_price_type in ['area']:
            max_width = self.product_id.max_width_area
            min_width = self.product_id.min_width_area
            max_height = self.product_id.max_height_area
            min_height = self.product_id.min_height_area

        if self.product_id.sale_price_type in ['table_2d', 'area'] and \
                        self.origin_height != 0 and self.origin_width != 0 and \
                not self.product_id.origin_check_sale_dim_values(
                    self.origin_width, self.origin_height):
            if self.origin_width > max_width:
                raise ValidationError(_("Invalid Dimensions Product! max width = %.2f") % max_width)
            if self.origin_width < min_width:
                raise ValidationError(_("Invalid Dimensions Product! min width = %.2f") % min_width)
            if self.origin_height > max_height:
                raise ValidationError(_("Invalid Dimensions Product! max height = %.2f") % max_height)
            if self.origin_height < min_height:
                raise ValidationError(_("Invalid Dimensions Product! min height = %.2f") % min_height)
            else:
                raise ValidationError(_("Invalid Combination of Dimensions"))


        elif self.product_id.sale_price_type == 'table_1d' and self.origin_width != 0 and \
                not self.product_id.origin_check_sale_dim_values(self.origin_width, 0):
            if self.origin_width > max_width:
                raise ValidationError(_("Invalid Dimensions Product! max width = %.2f") % max_width)
            if self.origin_width < min_width:
                raise ValidationError(_("Invalid Dimensions Product! min width = %.2f") % min_width)
            else:
                raise ValidationError(_("Invalid Combination of Dimensions"))

    @api.multi
    def _get_display_price(self, product):
        super(SaleOrderLine, self)._get_display_price(product)

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,

            width=self.origin_width,
            height=self.origin_height
        )

        # TO DO: move me in master/saas-16 on sale.order
        if self.order_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.order_id.pricelist_id.id).lst_price

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        super(SaleOrderLine, self).product_uom_change()

        if not self.product_uom:
            self.price_unit = 0.0
            return

        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id.id,
                quantity=self.product_uom_qty,
                date_order=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position'),

                width=self.origin_width,
                height=self.origin_height
            )

        if self.order_id.pricelist_id and self.order_id.partner_id:
            self.price_unit = self.env['account.tax'].\
                _fix_tax_included_price_company(self._get_display_price(product),
                                                product.taxes_id,
                                                self.tax_id,
                                                self.company_id)

    def _update_price_configurator(self):
        """If there are enough data (template, pricelist & partner), check new
        price and update line if different.
        """
        self.ensure_one()
        if (not self.product_tmpl_id or not self.order_id.pricelist_id or
                not self.order_id.partner_id):
            return
        product_tmpl = self.product_tmpl_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=self.product_uom_qty,
            date_order=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
            fiscal_position=self.env.context.get('fiscal_position'),

            width=self.origin_width,
            height=self.origin_height
        )
        price = self.env['account.tax']._fix_tax_included_price_company(
            product_tmpl.uom_id._compute_price(
                self.price_extra,
                self.env['product.uom'].browse(
                    product_tmpl._context['uom'])) +
            self._get_display_price(product_tmpl),
            product_tmpl.taxes_id,
            self.tax_id, self.company_id)
        if self.price_unit != price:
            self.price_unit = price