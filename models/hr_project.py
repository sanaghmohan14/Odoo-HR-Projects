# -*- coding: utf-8 -*-
from odoo import api, fields, models


class HrProject(models.Model):
    _name = 'hr.project'
    _description = 'HR Project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id desc'

    @api.model
    def _default_stage_id(self):
        return self.env['hr.project.stage'].search([], order='sequence, id', limit=1)

    name = fields.Char(string='Project Name', required=True, tracking=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    color = fields.Integer(string='Color Index')
    partner_id = fields.Many2one(
        'res.partner', string='Customer', tracking=True, index=True)
    user_id = fields.Many2one(
        'res.users', string='Project Manager', tracking=True,
        default=lambda self: self.env.user)
    stage_id = fields.Many2one(
        'hr.project.stage', string='Stage', tracking=True, index=True,
        default=_default_stage_id, group_expand='_read_group_stage_ids',
        copy=False, required=True, ondelete='restrict')
    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    description = fields.Html(string='Description')
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    task_ids = fields.One2many(
        'hr.project.task', 'project_id', string='Tasks')

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        """Always show every stage as a kanban column, even when empty."""
        return stages.search([], order=stages._order)
