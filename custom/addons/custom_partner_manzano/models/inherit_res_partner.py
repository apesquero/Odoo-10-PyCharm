# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    doorway = fields.Char(string='Doorway Interior')
    floor = fields.Char(string='Floor')
    letter = fields.Char(string='Letter')
    number_door = fields.Char(string='Door Number')
    mobile2 = fields.Char(string='Mobile 2')
