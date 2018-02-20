# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _

import logging
_logger = logging.getLogger(__name__)


class SaleOrder (models.Model):
    _inherit = 'sale.order'
    
    @api.multi
    def _cart_find_product_line_from_attributes(self, product_template_id, attribute_dicts, line_id=None, **kwargs):
        for so in self:
            domain = [('order_id', '=', so.id), ('product_template_id', '=', product_template_id)]
            if line_id:
                domain.append(('id', '=', line_id))
            
            res = self.env['sale.order.line'].sudo().search(domain)
            
            if res and attribute_dicts:
                res = res.filter_by_attribute_dicts(attribute_dicts)
            
            return res
    
    #To make the normal way play nice with sale_product_variants
    @api.multi
    def _website_product_id_change(self, order_id, product_id, qty=0):
        res = super(SaleOrder, self)._website_product_id_change(order_id, product_id, qty=qty)
        
        order = self.env['sale.order'].sudo().browse(order_id) #TODO losing context, matters?
        product = self.env['product.product'].with_context(
                lang = order.partner_id.lang,
                partner = order.partner_id.id,
                quantity = qty,
                date = order.date_order,
                pricelist = order.pricelist_id.id
            ).browse(product_id)
        if product:
            res.update({'product_template_id': product.product_tmpl_id.id, })
        
        return res
    
    @api.multi
    def _website_product_template_id_change_values(self, product_template_id, attribute_dicts, qty=0):
        self.ensure_one()
        
        product_template = self.env['product.template'].with_context( #TODO is the context needed? it was intended for product.product
                lang = self.partner_id.lang,
                partner = self.partner_id.id,
                quantity = qty,
                date = self.date_order,
                pricelist = self.pricelist_id.id
            ).browse(product_template_id)
        
        #Checking there are no extra attribute_dicts and the values fits the product
        for attr_dict in attribute_dicts:
            attr_line =  product_template.attribute_line_ids.filtered(lambda l: l.attribute_id.id == attr_dict['attribute'])
            if not attr_line:
                raise exceptions.Warning(_('Received an attribute that do not belong to the product selected.'))
            if attr_dict['value'] not in attr_line[0].value_ids.ids:
                raise exceptions.Warning(_('Received a value that do not belong to the product selected.'))
        
        #Find or create product_product if it does not exists
        product = self.env['product.product']._product_find(
                          product_template, attribute_dicts)
        if not product:
            product_values = {
                'product_tmpl_id': product_template_id,
                'attribute_value_ids': [(6, 0, [d['value'] for d in attribute_dicts])],
            }
            product = self.env['product.product'].create(product_values)
        
        values = {
            'product_template_id': product_template_id,
            'product_id': product.id,
            'name': product.display_name,
            'product_uom_qty': qty,
            'order_id': self.id,
            'product_uom': product_template.uom_id.id,
            'price_unit': product_template.with_context(product_attribute_values=attribute_dicts).price,
        }
        if attribute_dicts:
            values['product_attributes'] = [ (0,0, {
                            'product_template_id': product_template_id,
                            'attribute': value_dict['attribute'],
                            'value': value_dict['value'],
                            'custom_value': value_dict.get('r', 0.0),
                        }) for value_dict in attribute_dicts
                    ]
        
        if product_template.description_sale:
            values['name'] += '\n' + product_template.description_sale
        
        return values
    
    @api.multi
    def _cart_update(self, product_template_id=None, product_id=None, attribute_dicts=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        """ Add or set product quantity, add_qty can be negative """
        
        line_with_attributes = False #this is a hack and the whole function needs to be restructured
        if line_id:
            pre_sale_line = self.env['sale.order.line'].sudo().browse(line_id)
            if pre_sale_line and len(pre_sale_line.product_attributes) > 0:
                line_with_attributes = pre_sale_line
        
        if not line_with_attributes:
            if product_id or not (product_template_id and attribute_dicts):
                return super(SaleOrder, self)._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty, **kwargs)
        
        sol = self.env['sale.order.line'].sudo() #maybe as sale_manager is enough?

        quantity = 0
        for so in self:
            if so.state != 'draft':
                request.session['sale_order_id'] = None
                raise exceptions.UserError(_('It is forbidden to modify a sale order which is not in draft status'))
            
            if not line_with_attributes:
                sale_line = False
                if line_id is not False:
                    line_ds = so._cart_find_product_line_from_attributes(product_template_id, attribute_dicts, line_id=line_id, **kwargs)
                    if line_ds:
                        sale_line = line_ds[0]
                
                # Create sale_line if no line with product_template_id and attribute_dicts can be located
                if not sale_line:
                    values = so._website_product_template_id_change_values(product_template_id, attribute_dicts, qty=1)
                    sale_line = sol.create(values)
                    #TODO update sale name
                    sale_line._compute_tax_id()
                    if add_qty:
                        add_qty -= 1
            else:
                sale_line = line_with_attributes
            
            # compute new quantity
            if set_qty:
                quantity = set_qty
            elif add_qty is not None:
                quantity = sale_line.product_uom_qty + (add_qty or 0)
            
            # Remove zero of negative lines
            if quantity <= 0:
                sale_line.unlink()
            else:
                # update sale_line qty
                #values = so._website_product_template_id_change_values(product_template_id, attribute_dicts, qty=quantity)
                sale_line.write({'product_uom_qty': quantity,})
        
        return {'line_id': sale_line.id, 'quantity': quantity}


class SaleOrderLine (models.Model):
    _inherit = 'sale.order.line'
    
    @api.multi
    def filter_by_attribute_dicts(self, attribute_dicts):
        res = self.env['sale.order.line']
        
        for line in self:
            if not line.product_attributes:
                continue
            
            valid_line = True
            for value_dict in attribute_dicts:
                #this way range type with same custom_value but different value will not match, maybe make exception for this case?
                proc_line = line.product_attributes.filtered(lambda l: l.value.id == value_dict.get('value'))
                if not proc_line:
                    valid_line = False
                    break
                if proc_line.attr_type == 'range' and proc_line.custom_value != value_dict.get('r'):
                    valid_line = False
                    break
            
            if valid_line:
                res |= line
        
        return res

