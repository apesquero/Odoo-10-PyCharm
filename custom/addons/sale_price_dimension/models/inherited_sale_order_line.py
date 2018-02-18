# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT


class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    origin_width = fields.Float(string="Width", required=True)
    origin_height = fields.Float(string="Height", required=True)
    product_price_type = fields.Selection([('standard', 'Standard'),
                                           ('table_1d', '1D Table'),
                                           ('table_2d', '2D Table'),
                                           ('area', 'Area')],
                                          string='Sale Price Type',
                                          related='product_tmpl_id.sale_price_type')


    """
    TODO: demasiadas operaciones juntas de onchange, poco eficiente, repite procesos innecesariamente
    """

    @api.onchange('product_id', 'origin_width', 'origin_height', 'product_attribute_ids',
                  'product_attribute_ids.value_id')
    def product_id_change(self):
        super(sale_order_line, self).product_id_change()

        if not self.product_tmpl_id:
            return

        """
        TODO: crea directamente la variante de producto, 
                lo suyo sería llamar al modelo _onchange_create_product_variant de product_configurator
        """
        if self.can_create_product:
            try:
                with self.env.cr.savepoint():
                    self.product_id = self.create_variant_if_needed()
            except exceptions.ValidationError as e:
                _logger.exception('Product not created!')
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

        if product.sale_price_type in ['table_2d', 'area']\
                and self.origin_height != 0\
                and self.origin_width != 0\
                and not self.product_id.origin_check_sale_dim_values(self.origin_width,
                                                                     self.origin_height):
            raise ValidationError(_("Invalid Dimensions!"))

        elif product.sale_price_type == 'table_1d'\
                and self.origin_width != 0\
                and not self.product_id.origin_check_sale_dim_values(self.origin_width, 0):
            raise ValidationError(_("Invalid Dimensions!"))

        if self.product_tmpl_id.sale_price_type not in ['table_1d', 'table_2d', 'area']:
            self.origin_height = self.origin_width = 0

        name = ''

        if self.product_id:
            name = product.name_get()[0][1]

        if product.sale_price_type in ['table_2d', 'area']:
            height_uom = product.height_uom.name
            width_uom = product.width_uom.name
            name += _(' [Width:%.2f %s x Height:%.2f %s]') % (
            self.origin_width, width_uom, self.origin_height, height_uom)

        elif product.sale_price_type == 'table_1d':
            width_uom = product.width_uom.name
            name += _(' [ Width:%.2f %s]') % (self.origin_width, width_uom)

        if product.description_sale:
            name += '\n' + product.description_sale

        vals['name'] = name

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(product.lst_price, product.taxes_id,
                                                                                 self.tax_id)
        self.update(vals)

    # def product_uom_change(self):
    #     super(sale_order_line, self).product_uom_change()
    #     if not self.product_uom or not self.product_id:
    #         self.price_unit = 0.0
    #         return
    #     if self.order_id.pricelist_id and self.order_id.partner_id:
    #         product = self.product_id.with_context(
    #             lang=self.order_id.partner_id.lang,
    #             partner=self.order_id.partner_id.id,
    #             quantity=self.product_uom_qty,
    #             date_order=self.order_id.date_order,
    #             pricelist=self.order_id.pricelist_id.id,
    #             uom=self.product_uom.id,
    #             fiscal_position=self.env.context.get('fiscal_position'),
    #
    #             width=self.origin_width,
    #             height=self.origin_height
    #         )
    #         # self.price_unit = self.env['account.tax']._fix_tax_included_price(product.price, product.taxes_id,
    #         #                                                                   self.tax_id)
    #         self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product),
    #                                                                                   product.taxes_id, self.tax_id,
    #                                                                                   self.company_id)

    @api.multi
    def _prepare_order_line_procurement(self, group_id=False):
        self.ensure_one()
        vals = super(sale_order_line, self)._prepare_order_line_procurement(group_id=group_id)
        vals.update({
            'origin_width': self.origin_width,
            'origin_height': self.origin_height
        })
        return vals

    @api.multi
    def _action_procurement_create(self):
        """
        Create procurements based on quantity ordered. If the quantity is increased, new
        procurements are created. If the quantity is decreased, no automated action is taken.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        new_procs = self.env['procurement.order']  # Empty recordset
        for line in self:
            if line.state != 'sale' or not line.product_id._need_procurement():
                continue
            qty = 0.0
            for proc in line.procurement_ids:
                qty += proc.product_qty
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            if not line.order_id.procurement_group_id:
                vals = line.order_id._prepare_procurement_group()
                line.order_id.procurement_group_id = self.env["procurement.group"].create(vals)

            vals = line._prepare_order_line_procurement(
                group_id=line.order_id.procurement_group_id.id)
            vals['product_qty'] = line.product_uom_qty - qty
            new_proc = self.env["procurement.order"].with_context(
                procurement_autorun_defer=True,
            ).create(vals)
            """
            # Do one by one because need pass specific context values
            """
            new_proc.with_context(
                width=line.origin_width,
                height=line.origin_height).run()
            new_procs += new_proc
        return new_procs
