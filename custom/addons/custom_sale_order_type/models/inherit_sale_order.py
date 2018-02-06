from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_order_type(self):
        if self.partner_id.sale_type.id:
            self.type_id = self.partner_id.sale_type.id
        if self.user_id.sale_type.id:
            self.type_id = self.user_id.sale_type.id
        else:
            self.type_id = self.env['sale.order.type'].search([], limit=1)
        return self.type_id

    @api.multi
    @api.onchange('user_id')
    def onchange_user_id(self):
        if self.user_id:
            self.type_id = self.user_id.sale_type.id or self._get_order_type().id
            self.onchange_type_id()


    @api.multi
    @api.onchange('type_id', 'partner_id')
    def onchange_type_id(self):
        return super(SaleOrder, self).onchange_type_id()
