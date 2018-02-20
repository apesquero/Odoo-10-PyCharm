# -*- coding: utf-8 -*-

from openerp import fields, models


class product_attribute(models.Model):
    _inherit = "product.attribute"
    
    type = fields.Selection(selection_add=[('radiohide', 'RadioHide'),
                                           ('selecthide', 'SelectHide'),
                                           ('colorhide', 'ColorHide'),
                                           ('imagehide', 'ImageHide')])

