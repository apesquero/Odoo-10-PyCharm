# -*- coding: utf-8 -*-
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.website_sale.controllers.main import website_sale, QueryURL


class website_sale_hook(website_sale):
    
    """def variant_attrs_condition(self, attr_line, product):
        if len(attr_line.value_ids) > 1:
            return True
        return False
    
    def get_attribute_value_ids(self, product): #TODO test speed old vs new
        #cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        currency_obj = request.env['res.currency'].sudo()
        attribute_value_ids = []
        #variant_attrs = set(l.attribute_id.id
        #                        for l in product.attribute_line_ids
        #                            if self.variant_attr_condition(l, product))
        variant_attrs = product.attribute_line_ids. \
                filtered(lambda l: self.variant_attrs_condition(l, product)). \
                mapped('attribute_id')
        
        if request.website.pricelist_id.id != request.context['pricelist']:
            website_currency_id = request.website.currency_id.id
            currency_id = self.get_pricelist().currency_id.id
            for p in product.product_variant_ids:
                price = currency_obj.compute(website_currency_id, currency_id, p.lst_price)
                #attribute_value_ids.append([p.id, [v.id for v in p.attribute_value_ids.sorted(key=lambda v: v.attribute_id.sequence)
                #        if v.attribute_id.id in variant_attrs], p.price, price])
                attribute_value_ids.append([p.id,
                                            p.attribute_value_ids. \
                                                filtered(lambda v: v.attribute_id in variant_attrs). \
                                                sorted(key=lambda v: v.attribute_id.sequence). \
                                                mapped('id'),
                                            p.price,
                                            price])
        else:
            #attribute_value_ids = [[p.id, [v.id for v in p.attribute_value_ids.sorted(key=lambda v: v.attribute_id.sequence)
            #                                   if v.attribute_id.id in visible_attrs], p.price, p.lst_price]
            #                       for p in product.product_variant_ids]
            attribute_value_ids = [[p.id,
                                    p.attribute_value_ids. \
                                        filtered(lambda v: v.attribute_id in variant_attrs). \
                                        sorted(key=lambda v: v.attribute_id.sequence). \
                                        mapped('id'),
                                    p.price,
                                    p.lst_price]
                                   for p in product.product_variant_ids]
        
        return attribute_value_ids"""

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        category_obj = pool['product.public.category']
        template_obj = pool['product.template']

        context.update(active_id=product.id)

        if category:
            category = category_obj.browse(cr, uid, int(category), context=context)
            category = category if category.exists() else False

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int,v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        keep = QueryURL('/shop', category=category and category.id, search=search, attrib=attrib_list)

        category_ids = category_obj.search(cr, uid, [('parent_id', '=', False)], context=context)
        categs = category_obj.browse(cr, uid, category_ids, context=context)

        pricelist = self.get_pricelist()

        from_currency = pool['res.users'].browse(cr, uid, uid, context=context).company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price, context=context)

        # get the rating attached to a mail.message, and the rating stats of the product
        Rating = pool['rating.rating']
        rating_ids = Rating.search(cr, uid, [('message_id', 'in', product.website_message_ids.ids)], context=context)
        ratings = Rating.browse(cr, uid, rating_ids, context=context)
        rating_message_values = dict([(record.message_id.id, record.rating) for record in ratings])
        rating_product = product.rating_get_stats([('website_published', '=', True)])

        if not context.get('pricelist'):
            context['pricelist'] = int(self.get_pricelist())
            product = template_obj.browse(cr, uid, int(product), context=context)
        
        selected_values_dict = None
        line_order_id = kwargs.get('loid')
        if line_order_id:
            line_order_id = int(line_order_id)
            order = request.website.sale_get_order(context=context)
            if order:
                order_line = order.order_line.filtered(lambda ol: ol.id == line_order_id)
                if order_line:
                    selected_values_dict = order_line[0].get_procurement_lines_as_website_dict()
        if not selected_values_dict:
            selected_values_dict = product.get_default_values_as_website_dict()
        
        values = {
            'search': search,
            'category': category,
            'pricelist': pricelist,
            'attrib_values': attrib_values,
            'compute_currency': compute_currency,
            'attrib_set': attrib_set,
            'keep': keep,
            'categories': categs,
            'main_object': product,
            'product': product,
            'get_attribute_value_ids': self.get_attribute_value_ids,
            'rating_message_values' : rating_message_values,
            'rating_product' : rating_product,
            'selected_values_dict' : selected_values_dict,
        }
        return request.website.render("website_sale_hook.product", values)

