from openerp import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    group_purchase_lines = fields.Boolean(
        string='Group Purchase Lines', default=True)

