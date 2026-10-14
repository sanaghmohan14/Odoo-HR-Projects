# -*- coding: utf-8 -*-
from odoo import fields, models


class HrProjectStage(models.Model):
    _name = 'hr.project.stage'
    _description = 'HR Project Stage'
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True, translate=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(
        string='Folded in Kanban',
        help='Folded stages are collapsed in the kanban view.')
    active = fields.Boolean(default=True)
