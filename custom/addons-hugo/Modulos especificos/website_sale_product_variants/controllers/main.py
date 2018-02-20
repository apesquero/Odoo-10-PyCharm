# -*- coding: utf-8 -*-
import json
#import werkzeug

#from openerp import exceptions
from openerp.addons.web import http
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale


class website_sale_product_variants(website_sale):
    
    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True)
    def cart_update(self, product_id=None, product_template_id=None, attribute_lines=None, add_qty=1, set_qty=0, **kw):
        if attribute_lines:
            attribute_lines = json.loads(attribute_lines) #TODO errors
        request.website.sale_get_order(force_create=1)._cart_update(
                                                           product_template_id=int(product_template_id),
                                                           product_id=int(product_id) if product_id else False,
                                                           attribute_dicts=attribute_lines,
                                                           add_qty=float(add_qty),
                                                           set_qty=float(set_qty)
                                                       )
        return request.redirect("/shop/cart")

#TODO update_json?

