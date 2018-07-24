# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from math import ceil

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    origin_width = fields.Float(string="Width", required=True, default=0.0)
    origin_height = fields.Float(string="Height", required=True, default=0.0)

    width_sale_uom = fields.Many2one('product.uom',
                                     string='Width UOM',
                                     related='product_tmpl_id.width_uom',
                                     readonly=True)
    height_sale_uom = fields.Many2one('product.uom',
                                      string='Height UOM',
                                      related='product_tmpl_id.height_uom',
                                      readonly=True)

    product_price_type = fields.Selection([('standard', 'Standard'),
                                           ('fabric', 'Fabric'),
                                           ('table_1d', '1D Table'),
                                           ('table_2d', '2D Table'),
                                           ('area', 'Area')],
                                          string='Sale Price Type',
                                          related='product_tmpl_id.sale_price_type')

    rapport = fields.Float(related='product_tmpl_id.rapport')
    rapport_uom = fields.Many2one('product.uom',
                                  string='Rapport UOM',
                                  related='product_tmpl_id.rapport_uom',
                                  readonly=True)

    @api.constrains('origin_width', 'origin_height')
    def _check_origin_dimensions_constrains(self):
        if self.origin is False:
            for record in self:
                if not record.product_id.origin_check_sale_dim_values(
                        record.origin_width, record.origin_height):
                    raise ValidationError(_("Invalid dimension in:\n%s!") % self.product_id.name_get()[0][1])

    @api.onchange('origin_width',
                  'origin_height')
    def _check_origin_dimensions(self):

        width_uom = self.product_id.width_uom.name
        height_uom = self.product_id.height_uom.name

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
                raise ValidationError(_("Invalid Dimensions Product! "
                                        "max width = %.0f %s") % (max_width, width_uom))
            if self.origin_width < min_width:
                raise ValidationError(_("Invalid Dimensions Product! "
                                        "min width = %.0f %s") % (min_width, width_uom))
            if self.origin_height > max_height:
                raise ValidationError(_("Invalid Dimensions Product! "
                                        "max height = %.0f %s") % (max_height, height_uom))
            if self.origin_height < min_height:
                raise ValidationError(_("Invalid Dimensions Product! "
                                        "min height = %.0f %s") % (min_height, height_uom))
            else:
                raise ValidationError(_("Invalid Combination of Dimensions\n "
                                        "See the table dimensions"))


        elif self.product_id.sale_price_type == 'table_1d' and self.origin_width != 0 and \
                not self.product_id.origin_check_sale_dim_values(self.origin_width, 0):
            if self.origin_width > max_width:
                raise ValidationError(_("Invalid Dimensions Product! "
                                        "max width = %.0f %s") % (max_width, width_uom))
            if self.origin_width < min_width:
                raise ValidationError(_("Invalid Dimensions Product! "
                                        "min width = %.0f %s") % (min_width, width_uom))
            else:
                raise ValidationError(_("Invalid Combination of Dimensions\n "
                                        "See the table dimensions"))

    @api.onchange('product_id',
                  'origin_width',
                  'origin_height',
                  'product_attribute_ids')
    def product_id_change(self):
        product_tmp = False
        if not self.product_tmpl_id or (self.product_id and \
                                        self.product_id.product_tmpl_id.id != \
                                        self.product_id.product_tmpl_id.id):
            return {'domain': {'product_uom': []}}

        # Create a product if it doesn't exist
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
        domain = {'uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)],
                  'width_sale_uom': [('category_id', '=', self.product_id.width_uom.category_id.id)],
                  'height_sale_uom': [('category_id', '=', self.product_id.height_uom.category_id.id)]}
        if not self.uom_id or (self.product_id.uom_id.id != self.uom_id.id):
            vals['uom_id'] = self.product_id.uom_id
            vals['quantity'] = 1.0

        product = self.product_id.with_context(
            lang=self.invoice_id.partner_id.lang,
            partner=self.invoice_id.partner_id.id,
            quantity=self.quantity,
            date=self.invoice_id.date_invoice,
            uom=self.uom_id.id,

            width=self.origin_width,
            height=self.origin_height
        )

        result = {'domain': domain}

        title = False
        message = False
        warning = {}

        if self.product_tmpl_id.sale_price_type not in ['fabric', 'table_1d', 'table_2d', 'area']:
            self.origin_height = self.origin_width = 0

        # rapport calculation
        if self.product_tmpl_id.sale_price_type in ['fabric']:
            rapport = (self.width_sale_uom.factor * self.rapport) / self.rapport_uom.factor
            width_uom = self.width_sale_uom.name
            if rapport > 0:

                result_width = (int(ceil(round((self.origin_width / rapport), 2)))) * rapport
                remainder = result_width - self.origin_width
                if remainder > 0:
                    self.origin_width = result_width
                    product = product.with_context(width=self.origin_width)

                    message = _("The measure is less than the necessary rapport:\n"
                                "The measure has been increased %.2f %s!") % (remainder, width_uom)
                    mess = {'title': _("Warning measure"),
                            'message': message}
                    result = {'warning': mess}

        name = ''
        if self.product_id:
            name = product.name_get()[0][1]
        if product.sale_price_type in ['fabric']:
            width_uom = product.width_uom.name
            name += _(' [Length:%.2f %s]') % (self.origin_width, width_uom)
        elif product.sale_price_type in ['table_1d']:
            width_uom = product.width_uom.name
            name += _(' [Width:%.2f %s]') % (self.origin_width, width_uom)
        elif product.sale_price_type in ['table_2d', 'area']:
            height_uom = product.height_uom.name
            width_uom = product.width_uom.name
            name += _(' [Width:%.2f %s x Height:%.2f %s]') % \
                    (self.origin_width, width_uom, self.origin_height, height_uom)
        if product.description_sale:
            name += '\n' + product.description_sale
        vals['name'] = name

        """TODO: simplificado, pendiente de aplicar pricelist, y la conversión de unidades. Para que 
        funcione correctamente sin el sale instalado, hay que poder activar los grupos de visualización
        para poder ver los precios de las variantes de los productos, y los atributos en las variantes."""

        """TODO: simplified, pending to apply pricelist, and the conversion of units. To work properly 
        without the sale installed, you must be able to activate the display groups to see the prices 
        of the variants of the products, and the attributes in the variants."""

        self.price_unit = product.lst_price
        self._compute_price()

        self.update(vals)

        return result
