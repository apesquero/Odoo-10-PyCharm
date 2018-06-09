# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    origin_width = fields.Float(string="Width", required=False)
    origin_height = fields.Float(string="Height", required=False)

    @api.model
    def _run_move_create(self, procurement):
        res = super(ProcurementOrder, self)._run_move_create(procurement)
        width = 0
        height = 0
        if procurement.origin_width:
            width = procurement.origin_width
        if procurement.origin_height:
            height = procurement.origin_height
        res.update({
            'origin_width': width,
            'origin_height': height
        })
        return res

    @api.multi
    def _prepare_purchase_order_line(self, po, supplier):
        self.ensure_one()
        res = super(ProcurementOrder, self)._prepare_purchase_order_line(po=po, supplier=supplier)

        product_id = self.product_id.with_context(
            width=self.origin_width,
            height=self.origin_height
        )

        procurement_uom_po_qty = self.product_uom._compute_quantity(self.product_qty, self.product_id.uom_po_id)
        seller = product_id._select_seller(
            partner_id=supplier.name,
            quantity=procurement_uom_po_qty,
            date=po.date_order and po.date_order[:10],
            uom_id=self.product_id.uom_po_id)

        if seller:
            seller = seller.with_context(
                width=self.origin_width,
                height=self.origin_height,
                product_id=product_id
            )

        taxes = product_id.supplier_taxes_id
        fpos = po.fiscal_position_id
        taxes_id = fpos.map_tax(taxes) if fpos else taxes
        if taxes_id:
            taxes_id = taxes_id.filtered(lambda x: x.company_id.id == self.company_id.id)

        name = res['name']
        if product_id.sale_price_type in ['table_2d', 'area']:
            name += ' [Width:%.2f cms x Height:%.2f cms]' % (self.origin_width, self.origin_height)
        elif product_id.sale_price_type == 'table_1d':
            name += ' [ Width:%.2f cms]' % (self.origin_width)

        price_unit = self.env['account.tax']._fix_tax_included_price(
            seller.get_supplier_price(), product_id.supplier_taxes_id, taxes_id) \
            if seller else 0.0
        if price_unit and seller and po.currency_id and seller.currency_id != po.currency_id:
            price_unit = seller.currency_id.compute(price_unit, po.currency_id)

        res.update({
            'name': name,
            'price_unit': price_unit,
            'origin_width': self.origin_width,
            'origin_height': self.origin_height
        })

        return res

    @api.multi
    def make_po(self):
        cache = {}
        res = []
        for procurement in self:
            suppliers = procurement.product_id.seller_ids.filtered(lambda r: not r.product_id or r.product_id == procurement.product_id)
            if not suppliers:
                procurement.message_post(body=_('No vendor associated to '
                    'product %s. Please set one to fix this procurement.') \
                    % (procurement.product_id.name))
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
                    if procurement.origin:
                        po.write({'origin': po.origin + ', ' + procurement.origin})
                    else:
                        po.write({'origin': po.origin})
                else:
                    po.write({'origin': procurement.origin})
            if po:
                res += [procurement.id]

            # Create Line
            po_line = False
            for line in po.order_line:
                product_id = procurement.product_id.with_context(
                    width=line.origin_width,
                    height=line.origin_height
                )
                if line.product_id == product_id and line.product_uom == procurement.product_id.uom_po_id and line.origin_width == procurement.origin_width and line.origin_height == procurement.origin_height:
                    procurement_uom_po_qty = procurement.product_uom._compute_quantity(procurement.product_qty, procurement.product_id.uom_po_id)
                    seller = self.product_id._select_seller(
                        partner_id=partner,
                        quantity=line.product_qty + procurement_uom_po_qty,
                        date=po.date_order and po.date_order[:10],
                        uom_id=procurement.product_id.uom_po_id)

                    if seller:
                        seller = seller.with_context(
                            width=line.origin_width,
                            height=line.origin_height,
                            product_id=product_id
                        )

                    price_unit = self.env['account.tax']._fix_tax_included_price(seller.get_supplier_price(), line.product_id.supplier_taxes_id, line.taxes_id) if seller else 0.0
                    if price_unit and seller and po.currency_id and seller.currency_id != po.currency_id:
                        price_unit = seller.currency_id.compute(price_unit, po.currency_id)

                    po_line = line.write({
                        'product_qty': line.product_qty + procurement_uom_po_qty,
                        'price_unit': price_unit,
                        'procurement_ids': [(4, procurement.id)]
                    })
                    break
            if not po_line:
                vals = procurement._prepare_purchase_order_line(po, supplier)
                self.env['purchase.order.line'].create(vals)
        return res
