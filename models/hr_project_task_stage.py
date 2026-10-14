# -*- coding: utf-8 -*-
from odoo import fields, models


class HrProjectTaskStage(models.Model):
    _name = 'hr.project.task.stage'
    _description = 'HR Task Stage'
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True, translate=True)
    sequence = fields.Integer(default=10)
    color = fields.Integer(string='Color Index')
    fold = fields.Boolean(
        string='Folded in Kanban',
        help='Folded stages are collapsed in the kanban view.')
    active = fields.Boolean(default=True)
