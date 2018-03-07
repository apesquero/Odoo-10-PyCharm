# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Tag(models.Model):
    _name = 'todo.task.tag'
    _description = 'To-do Tag'

    _parent_name = 'parent_id'
    _parent_store = True

    name = fields.Char('Name', size=40, translate=True)

    parent_id = fields.Many2one('todo.task.tag', 'Parent Tag', ondelete='restrict')

    parent_left = fields.Integer('Parent Left', index=True)
    parent_right = fields.Integer('Parent Right', index=True)

    child_ids = fields.One2many('todo.task.tag', 'parent_id', 'Child Tags')

    # Relation fields
    task_ids = fields.Many2many('todo.task', string='Tasks')

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
    tasks = fields.One2many('todo.task', 'stage_id', 'Tasks in this stage')

class TodoTask(models.Model):
    _inherit = 'todo.task'

    _sql_constraints = [('todo_task_name_uniq',
                         'UNIQUE (name, active)',
                         'Task title must be unique!')]


    """FIELDS"""

    stage_id = fields.Many2one('todo.task.stage', 'Stage')

    tag_ids = fields.Many2many('todo.task.tag',     # related model
                               'todo_task_tag_rel', # relation table name
                               'task_id',           # field for "this" record
                               'tag_id',            # field for "other" record
                               strig='Tags')

    refers_to = fields.Reference([('res.user', 'User'),
                                  ('res.partner', 'Partner')],
                                 'Refers to')

    stage_fold = fields.Boolean('Stage Folded?',
                                compute='_compute_stage_fold',
                                store=False,    #default
                                search='_search_stage_fold',
                                inverse='_write_stage_fold')

    stage_state = fields.Selection(related='stage_id.state',
                                   string='Stage State')

    image = fields.Binary(related='stage_id.image',
                          string='Image')

    user_todo_count = fields.Integer('User To-Do Count',
                                     compute='compute_user_todo_count')

    """DEFINITIONS"""

    def _search_stage_fold(self, operator, value):
        return [('stage_id.fold', operator, value)]

    def _write_stage_fold(self):
        self.stage_id.fold = self.stage_fold

    def compute_user_todo_count(self):
        for task in self:
            task.user_todo_count = task.search_count([('user_id', '=', task.user_id.id)])

    @api.depends('stage_id.fold')
    def _compute_stage_fold(self):
        for task in self:
            task.stage_fold = task.stage_id.fold

    @api.constrains('name')
    def _check_name_size(self):
        for todo in self:
            if len(todo.name) < 5:
                raise ValidationError('Must have 5 chars!')
