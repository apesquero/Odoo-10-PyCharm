# -*- coding: utf-8 -*-
import json
import werkzeug

#from openerp import SUPERUSER_ID
from openerp import exceptions
from openerp.addons.web import http
from openerp.http import request
from openerp.addons.website_sale_hook.controllers.main import website_sale_hook

import logging
_logger = logging.getLogger(__name__)


class website_sale_hierarchy(website_sale_hook):
    
    def get_attribute_hierarchy(self, product):
        hierarchy = product.attribute_hierarchy_id
        if hierarchy:
             res = hierarchy.get_hierarchy_as_dict()[0]
        else:
            res = {}
        return json.dumps(res) #this is needed because otherwise the keys get serialized like '5': instead of "5": and jquery doesn't like it

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        r = super(website_sale_hierarchy, self).product(product, category, search, **kwargs)
        
        r.qcontext['get_attribute_hierarchy'] = self.get_attribute_hierarchy
        
        return r

    @http.route(['/shop/get_unit_price'], type='json', auth="public", methods=['POST'], website=True)
    def get_unit_price(self, product_ids, add_qty, use_order_pricelist=False, product_template_id=False, data_from_template=False, **kw):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        
        if product_template_id:
            product_template = pool['product.template'].browse(cr, uid, product_template_id, context=context) #TODO sudo?
            if not product_template:
                raise werkzeug.exceptions.BadRequest("Product id did not match any product")
            
            #checking if allowed by the hierarchy
            hierarchy = product_template.attribute_hierarchy_id
            if hierarchy and not hierarchy.allowed_combination_from_dict(data_from_template):
                raise werkzeug.exceptions.BadRequest("Variant not allowed with those characteristics") 
            
            partner = pool['res.users'].browse(cr, uid, uid, context=context).partner_id
            if use_order_pricelist:
                pricelist_id = request.website.get_current_pricelist(context=context).id
            else:
                pricelist_id = partner.property_product_pricelist.id
            
            try:
                with_context = context.copy()
                with_context.update({'product_attribute_values': data_from_template})
                prices = pool['product.pricelist'].template_price_get(
                        cr, uid,
                        [pricelist_id], product_template,
                        add_qty, context=with_context)
            except exceptions.Warning, msg:
                _logger.info(msg)
                raise werkzeug.exceptions.BadRequest(msg) 
            
            return prices[pricelist_id]
        
        else:
            return super(website_sale_hierarchy, self).get_unit_price(product_ids, add_qty, use_order_pricelist=use_order_pricelist, **kw)

