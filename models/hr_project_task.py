# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError

MANAGER_GROUP = 'hr_project.group_hr_project_manager'

# Fields an HR user (non manager) may write on a task assigned to them.
HR_WRITABLE_FIELDS = {
    'stage_id', 'sequence', 'hiring_required', 'manpower_requirement_id',
}
HR_WRITABLE_PREFIXES = ('message_', 'activity_')


class HrProjectTask(models.Model):
    _name = 'hr.project.task'
    _description = 'HR Task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, id desc'

    @api.model
    def _default_stage_id(self):
        return self.env['hr.project.task.stage'].search([], order='sequence, id', limit=1)

    name = fields.Char(string='Task Title', required=True, tracking=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    color = fields.Integer(string='Color Index')
    description = fields.Html(string='Description')
    project_id = fields.Many2one(
        'hr.project', string='Project', ondelete='cascade', index=True)
    client_id = fields.Many2one(
        'res.partner', string='Client', related='project_id.partner_id',
        store=True, readonly=True, index=True)
    hiring_required = fields.Boolean(
        string='Hiring Required', tracking=True,
        help='Tick this when the task requires a new hire.')
    manpower_requirement_id = fields.Many2one(
        'manpower.requirement', string='Hiring Request', readonly=True,
        copy=False, ondelete='set null')
    stage_id = fields.Many2one(
        'hr.project.task.stage', string='Stage', tracking=True, index=True,
        default=_default_stage_id, group_expand='_read_group_stage_ids',
        copy=False, ondelete='restrict')
    stage_color = fields.Integer(
        string='Stage Color', related='stage_id.color', readonly=True)
    user_ids = fields.Many2many(
        'res.users', 'hr_project_task_user_rel', 'task_id', 'user_id',
        string='Assignees', tracking=True)
    date_deadline = fields.Date(string='Deadline', tracking=True)
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)

    is_project_manager = fields.Boolean(compute='_compute_is_project_manager')

    @api.depends_context('uid')
    def _compute_is_project_manager(self):
        is_manager = self.env.user.has_group(MANAGER_GROUP)
        for task in self:
            task.is_project_manager = is_manager

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        """Always show every stage as a kanban column, even when empty."""
        return stages.search([], order=stages._order)

    def _subscribe_assignees(self):
        for task in self:
            partners = task.user_ids.partner_id
            if partners:
                task.message_subscribe(partner_ids=partners.ids)

    def action_create_manpower_requirement(self):
        self.ensure_one()
        if self.env.user.has_group(MANAGER_GROUP) or not self.env.user.has_group('hr_project.group_hr_project_hr'):
            raise AccessError(_('Only HR users can create a hiring request.'))
        if not self.hiring_required:
            raise UserError(_('Enable Hiring Required before creating a hiring request.'))
        if self.manpower_requirement_id:
            return self.action_view_manpower_requirement()

        requirement = self.env['manpower.requirement'].create({
            'request_type': 'hiring',
            'state': 'hr_review',
            'client_id': self.client_id.id,
            'job_title': self.name,
            'vacancies': 1,
            'reason': 'project',
            'call_notes': self.description or False,
            'requested_by_id': self.env.user.id,
            'submitted_date': fields.Datetime.now(),
        })
        self.write({'manpower_requirement_id': requirement.id})
        return self.action_view_manpower_requirement()

    def action_view_manpower_requirement(self):
        self.ensure_one()
        if self.env.user.has_group(MANAGER_GROUP) or not self.env.user.has_group('hr_project.group_hr_project_hr'):
            raise AccessError(_('Only HR users can view hiring requests.'))
        if not self.manpower_requirement_id:
            raise UserError(_('No hiring request has been created for this task.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Hiring Request'),
            'res_model': 'manpower.requirement',
            'res_id': self.manpower_requirement_id.id,
            'view_mode': 'form',
        }

    @api.model_create_multi
    def create(self, vals_list):
        tasks = super().create(vals_list)
        tasks._subscribe_assignees()
        return tasks

    def write(self, vals):
        # HR users may only move their tasks between stages.
        if not self.env.su and not self.env.user.has_group(MANAGER_GROUP):
            forbidden = [
                fname for fname in vals
                if fname not in HR_WRITABLE_FIELDS
                and not fname.startswith(HR_WRITABLE_PREFIXES)
            ]
            if forbidden:
                raise AccessError(_(
                    "You can only change the stage of the tasks assigned to you."))
        result = super().write(vals)
        if 'user_ids' in vals:
            self._subscribe_assignees()
        return result
