# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def origin_check_sale_dim_values(self, width, height):
        if self.sale_price_type in ['table_1d', 'table_2d']:
            product_prices_table_obj = self.env['product.prices_table']
            norm_width = self.origin_normalize_sale_width_value(width)
            if self.sale_price_type == 'table_2d':
                norm_height = self.origin_normalize_sale_height_value(height)
                return product_prices_table_obj.search_count([
                    ('sale_product_tmpl_id', '=', self.product_tmpl_id.id),
                    ('pos_x', '=', norm_width),
                    ('pos_y', '=', norm_height),
                    ('value', '!=', 0)]) > 0
            return product_prices_table_obj.search_count([
                ('sale_product_tmpl_id', '=', self.product_tmpl_id.id),
                ('pos_x', '=', norm_width),
                ('value', '!=', 0)]) > 0
        elif self.sale_price_type == 'area':
            return width >= self.min_width_area and \
                   width <= self.max_width_area and \
                   height >= self.min_height_area and \
                   height <= self.max_height_area
        return True

    @api.model
    def origin_normalize_sale_width_value(self, width):
        headers = self.get_sale_price_table_headers()
        norm_val = width
        for index in range(len(headers['x']) - 1):
            if headers['x'][0] == 0 and index == 0:
                if width >= headers['x'][index + 1] and \
                                width <= headers['x'][index + 1]:
                    norm_val = headers['x'][index + 2]
            else:
                if width > headers['x'][index] and \
                                width <= headers['x'][index + 1]:
                    norm_val = headers['x'][index + 1]
        return norm_val

    @api.model
    def origin_normalize_sale_height_value(self, height):
        headers = self.get_sale_price_table_headers()
        norm_val = height
        for index in range(len(headers['y']) - 1):
            if headers['y'][0] == 0 and index == 0:
                if height >= headers['y'][index + 1] and \
                                height <= headers['y'][index + 1]:
                    norm_val = headers['y'][index + 2]
            else:
                if height > headers['y'][index] and \
                            height <= headers['y'][index + 1]:
                    norm_val = headers['y'][index + 1]
        return norm_val

    @api.model
    def get_sale_price_table_headers(self):
        result = {'x': [0], 'y': [0]}
        for rec in self.sale_prices_table:
            result['x'].append(rec.pos_x)
            result['y'].append(rec.pos_y)
        result.update({
            'x': sorted(list(set(result['x']))),
            'y': sorted(list(set(result['y'])))
        })
        return result

    @api.model
    def get_sale_price(self):
        origin_width = self._context.get('width', False)
        origin_height = self._context.get('height', False)

        result = False
        if origin_width:
            product_prices_table_obj = self.env['product.prices_table']
            origin_width = self.origin_normalize_sale_width_value(origin_width)
            if self.sale_price_type == 'table_2d':
                origin_height = self.origin_normalize_sale_height_value(origin_height)
                res = product_prices_table_obj.search([
                    ('sale_product_tmpl_id', '=', self.product_tmpl_id.id),
                    ('pos_x', '=', origin_width),
                    ('pos_y', '=', origin_height)
                ], limit=1)
                result = res and res.value or False
            elif self.sale_price_type == 'table_1d':
                res = product_prices_table_obj.search([
                    ('sale_product_tmpl_id', '=', self.product_tmpl_id.id),
                    ('pos_x', '=', origin_width)
                ], limit=1)
                result = res and res.value or False
            elif self.sale_price_type == 'area':
                # Unit conversion created
                origin_width = (self.area_uom.factor * origin_width) / self.width_uom.factor
                origin_height = (self.area_uom.factor * origin_height) / self.height_uom.factor

                result = self.list_price * origin_width * origin_height
                result = max(self.min_price_area, result)
            elif self.sale_price_type == 'fabric':
                """
                TODO: Falta todo el proceso de cálculo del rapport, pero es posible que haya que 
                ponerlo en las unidades en vez de en el precio. Pendiente de revisar
                """
                # Unit conversion created
                origin_width = (self.fabric_uom.factor * origin_width) / self.width_uom.factor

                result = self.list_price * origin_width
                if result < self.min_transport_fabric:
                    result = result + self.cost_transport_fabric
                result = max(self.min_price_fabric + self.cost_transport_fabric, result)
        if not result:
            result = self.list_price
        return result

    @api.depends('list_price', 'price_extra')
    def _compute_product_lst_price(self):
        # super(ProductProduct, self)._compute_product_lst_price()
        to_uom = None
        if 'uom' in self._context:
            to_uom = self.env['product.uom'].browse([self._context['uom']])

        price_extra = 0.0
        for product in self:
            if to_uom:
                list_price = product.uom_id._compute_price(product.get_sale_price(), to_uom)
                price_extra = product.uom_id._compute_price(product.price_extra, to_uom)
            else:
                list_price = product.list_price
            product.lst_price = list_price + price_extra
            product.list_price = product.lst_price
            product.price = product.lst_price

    @api.multi
    def price_compute(self, price_type, uom=False, currency=False, company=False):
        # TDE FIXME: delegate to template or not ? fields are reencoded here ...
        # compatibility about context keys used a bit everywhere in the code
        if not uom and self._context.get('uom'):
            uom = self.env['product.uom'].browse(self._context['uom'])
        if not currency and self._context.get('currency'):
            currency = self.env['res.currency'].browse(self._context['currency'])

        products = self
        if price_type == 'standard_price':
            # standard_price field can only be seen by users in base.group_user
            # Thus, in order to compute the sale price from the cost for users not in this group
            # We fetch the standard price as the superuser
            products = self.with_context(force_company=company and company.id or self._context.get('force_company',
                                                                                                   self.env.user.company_id.id)).sudo()

        prices = dict.fromkeys(self.ids, 0.0)
        for product in products:
            prices[product.id] = product[price_type] or 0.0
            if price_type == 'list_price':
                prices[product.id] += product.price_extra

            """Eliminado el condicional, ya que se convierten las unidades en _compute_product_lst_price"""
            # if uom:
            #     prices[product.id] = product.uom_id._compute_price(prices[product.id], uom)

            # Convert from current user company currency to asked one
            # This is right cause a field cannot be in more than one currency
            if currency:
                prices[product.id] = product.currency_id.compute(prices[product.id], currency)

        return prices
