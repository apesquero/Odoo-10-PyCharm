# -*- encoding: utf-8 -*-
from openerp import models, fields, exceptions, api, _
from openerp.exceptions import Warning as UserError
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.float_utils import float_is_zero


#This is all a big hack and will make maintenance and compatibility with other modules difficult but there is no other way

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.onchange('product_qty', 'product_uom')
    def _onchange_quantity(self):
        if not self.product_id:
            return

        seller = self.product_id._select_seller(
            self.product_id,
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order[:10],
            uom_id=self.product_uom)

        if seller or not self.date_planned:
            self.date_planned = self._get_date_planned(seller).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        if not seller:
            return
        
        seller_price = seller.get_price(proc_lines=self.product_attributes)
        price_unit = self.env['account.tax']._fix_tax_included_price(seller_price, self.product_id.supplier_taxes_id, self.taxes_id) if seller else 0.0
        if price_unit and seller and self.order_id.currency_id and seller.currency_id != self.order_id.currency_id:
            price_unit = seller.currency_id.compute(price_unit, self.order_id.currency_id)

        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = self.env['product.uom']._compute_price(seller.product_uom.id, price_unit, to_uom_id=self.product_uom.id)

        self.price_unit = price_unit


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def propagate_cancels(self):
        #from stock
        move_cancel = self.env['stock.move']
        for procurement in self:
            if procurement.rule_id.action == 'move' and procurement.move_ids:
                move_cancel |= procurement.move_ids
            
            #from mrp
            elif procurement.rule_id.action == 'manufacture' and procurement.production_id:
                procurement.production_id.action_cancel()
            
            #from purchase
            if procurement.rule_id.action == 'buy' and procurement.purchase_line_id:
                if procurement.purchase_line_id.order_id.state not in ('draft', 'cancel', 'sent', 'to validate'):
                    raise UserError(
                        _('Can not cancel a procurement related to a purchase order. Please cancel the purchase order first.'))
            if procurement.purchase_line_id:
                price_unit = 0.0
                product_qty = 0.0
                others_procs = procurement.purchase_line_id.procurement_ids.filtered(lambda r: r != procurement)
                for other_proc in others_procs:
                    if other_proc.state not in ['cancel', 'draft']:
                        product_qty += other_proc.product_uom._compute_qty_obj(other_proc.product_uom, other_proc.product_qty, procurement.purchase_line_id.product_uom)

                precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
                if not float_is_zero(product_qty, precision_digits=precision):
                    seller = procurement.product_id._select_seller(
                        procurement.product_id,
                        partner_id=procurement.purchase_line_id.partner_id,
                        quantity=product_qty,
                        date=procurement.purchase_line_id.order_id.date_order and procurement.purchase_line_id.order_id.date_order[:10],
                        uom_id=procurement.product_uom)
                    
                    seller_price = seller.get_price(proc_lines=procurement.attribute_line_ids)
                    price_unit = self.env['account.tax']._fix_tax_included_price(seller.price, procurement.purchase_line_id.product_id.supplier_taxes_id, procurement.purchase_line_id.taxes_id) if seller else 0.0
                    if price_unit and seller and procurement.purchase_line_id.order_id.currency_id and seller.currency_id != procurement.purchase_line_id.order_id.currency_id:
                        price_unit = seller.currency_id.compute(price_unit, procurement.purchase_line_id.order_id.currency_id)

                    if seller and seller.product_uom != procurement.product_uom:
                        price_unit = self.env['product.uom']._compute_price(seller.product_uom.id, price_unit, to_uom_id=procurement.product_uom.id)

                procurement.purchase_line_id.product_qty = product_qty
                procurement.purchase_line_id.price_unit = price_unit
        
        #from stock(again)
        if move_cancel:
            move_cancel.action_cancel()
        return True
    
    @api.multi
    def _prepare_purchase_order_line(self, po, supplier):
        self.ensure_one()
        
        seller = self.product_id._select_seller(
            self.product_id,
            partner_id=supplier.name,
            quantity=self.product_qty,
            date=po.date_order and po.date_order[:10],
            uom_id=self.product_uom)
        
        taxes = self.product_id.supplier_taxes_id
        fpos = po.fiscal_position_id
        taxes_id = fpos.map_tax(taxes) if fpos else taxes
        if taxes_id:
            taxes_id = taxes_id.filtered(lambda x: x.company_id.id == self.company_id.id)
        
        seller_price = seller.get_price(proc_lines=self.attribute_line_ids)
        price_unit = self.env['account.tax']._fix_tax_included_price(seller_price, self.product_id.supplier_taxes_id, taxes_id) if seller else 0.0
        if price_unit and seller and po.currency_id and seller.currency_id != po.currency_id:
            price_unit = seller.currency_id.compute(price_unit, po.currency_id)
        
        if seller and self.product_uom and seller.product_uom != self.product_uom:
            price_unit = self.env['product.uom']._compute_price(seller.product_uom.id, price_unit, to_uom_id=self.product_uom.id)
        
        product_lang = self.product_id.with_context({
            'lang': supplier.name.lang,
            'partner_id': supplier.name.id,
        })
        name = product_lang.display_name
        if product_lang.description_purchase:
            name += '\n' + product_lang.description_purchase
        
        date_planned = self.env['purchase.order.line']._get_date_planned(seller, po=po).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        
        return {
            'name': name,
            'product_qty': self.product_qty,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'price_unit': price_unit,
            'date_planned': date_planned,
            'taxes_id': [(6, 0, taxes_id.ids)],
            'procurement_ids': [(4, self.id)],
            'order_id': po.id,
            'product_template': self.product_id.product_tmpl_id.id,
            'product_attributes': [(4, x.id) for x in self.attribute_line_ids],
        }
    
    @api.multi
    def make_po(self):
        cache = {}
        res = []
        for procurement in self:
            suppliers = procurement.product_id.seller_ids.filtered(lambda r: not r.product_id or r.product_id == procurement.product_id)
            if not suppliers:
                procurement.message_post(body=_('No vendor associated to product %s. Please set one to fix this procurement.') % (procurement.product_id.name))
                continue
            supplier = suppliers[0]
            partner = supplier.name

            gpo = procurement.rule_id.group_propagation_option
            group = (gpo == 'fixed' and procurement.rule_id.group_id) or \
                    (gpo == 'propagate' and procurement.group_id) or False

            domain = (
                ('partner_id', '=', partner.id),
                ('state', '=', 'draft'),
                ('picking_type_id', '=', procurement.rule_id.picking_type_id.id),
                ('company_id', '=', procurement.company_id.id),
                ('dest_address_id', '=', procurement.partner_dest_id.id))
            if group:
                domain += (('group_id', '=', group.id),)

            if domain in cache:
                po = cache[domain]
            else:
                po = self.env['purchase.order'].search([dom for dom in domain])
                po = po[0] if po else False
                cache[domain] = po
            if not po:
                vals = procurement._prepare_purchase_order(partner)
                po = self.env['purchase.order'].create(vals)
                cache[domain] = po
            elif not po.origin or procurement.origin not in po.origin.split(', '):
                # Keep track of all procurements
                if po.origin:
                    po.write({'origin': po.origin + ', ' + procurement.origin})
                else:
                    po.write({'origin': procurement.origin})
            res += po.ids

            # Create Line
            po_line = False
            if procurement.allow_line_grouping():
                for line in po.order_line:
                    if procurement.line_is_compatible(line):
                        seller = self.product_id._select_seller(
                            self.product_id,
                            partner_id=partner,
                            quantity=line.product_qty + procurement.product_qty,
                            date=po.date_order and po.date_order[:10],
                            uom_id=self.product_uom)
                        
                        seller_price = seller.get_price(proc_lines=procurement.attribute_line_ids)
                        price_unit = self.env['account.tax']._fix_tax_included_price(seller_price, line.product_id.supplier_taxes_id, line.taxes_id) if seller else 0.0
                        if price_unit and seller and po.currency_id and seller.currency_id != po.currency_id:
                            price_unit = seller.currency_id.compute(price_unit, po.currency_id)
                        
                        if seller and self.product_uom and seller.product_uom != self.product_uom:
                            price_unit = self.env['product.uom']._compute_price(seller.product_uom.id, price_unit, to_uom_id=self.product_uom.id)
                        
                        po_line = line.write({
                            'product_qty': line.product_qty + procurement.product_qty,
                            'price_unit': price_unit,
                            'procurement_ids': [(4, procurement.id)]
                        })
                        break
            
            if not po_line:
                vals = procurement._prepare_purchase_order_line(po, supplier)
                self.env['purchase.order.line'].create(vals)
        return res

