# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Tag(models.Model):
    _name = 'todo.task.tag'
    _description = 'To-do Tag'

    name = fields.Char('Name', size=40, translate=True)

    # Relation fields
    # tag_ids = fields.Many2many('todo.task')

class Stage(models.Model):
    _name = 'todo.task.stage'
    _description = 'To-do Stage'
    _order = 'sequence,name'

    # String fields
    name = fields.Char('Name', size=40, translate=True)
    desc = fields.Text('Description')
    state = fields.Selection([('draft','Draft'),
                              ('open','Open'),
                              ('done','Done')],
                             'State')
    docs = fields.Html('Documentation')

    # Numeric fields
    sequence = fields.Integer('Sequence')
    perc_complete = fields.Float('% Complete', (3,2))

    # Date fields
    date_effective = fields.Date('Effective Date')
    date_changed = fields.Datetime('Last Changed')

    # Other fields
    fold = fields.Boolean('Folded?')
    image = fields.Binary('Image')

    # Relation fields
    # stage_id = fields.One2many()

class TodoTask(models.Model):
    _inherit = 'todo.task'

    stage_id = fields.Many2one('todo.task.stage', 'Stage')

    tag_ids = fields.Many2many('todo.task.tag',     # related model
                               'todo_task_tag_rel', # relation table name
                               'task_id',           # field for "this" record
                               'tag_id',            # field for "other" record
                               strig='Tags')
