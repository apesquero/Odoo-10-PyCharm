# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TodoTask(models.Model):
    _inherit = 'todo.task'

    name = fields.Char(help="What needs to be done?")

    user_id = fields.Many2one('res.users', 'Responsible')
    date_deadline = fields.Date('Deadline')

    @api.multi
    def do_clear_done(self):
        domain = [('is_done', '=', True),
                  '|', ('user_id', '=', self.env.uid),
                       ('user_id', '=', False)]
        dones = self.search(domain)
        dones.write({'active': False})
        return True

    @api.multi
    def do_toggle_done(self):
        for task in self:
            if task.user_id != self.env.user:
                raise ValidationError('Only the responsible can to this!')
        return super(TodoTask, self).do_toggle_done()
