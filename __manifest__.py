# -*- coding: utf-8 -*-
{
    'name': 'HR Project',
    'version': '19.0.1.0.0',
    'category': 'Services/Project',
    'summary': 'Manage projects and standalone HR tasks with kanban stages',
    'description': """
HR Project
==========
* Projects (model ``hr.project``) with default stages New, Ongoing, Completed
  and Cancelled, shown in a kanban view, with a customer field.
* Standalone tasks (model ``hr.project.task``), not linked to projects, with
  manually created stages, kanban view, user assignment and activities.
* Two user groups: Project Manager and HR.
""",
    'author': 'Custom',
    'license': 'LGPL-3',
    'depends': ['base', 'mail', 'manpower_requisition'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/hr_project_stage_data.xml',
        'views/hr_project_stage_views.xml',
        'views/hr_project_views.xml',
        'views/hr_project_task_stage_views.xml',
        'views/hr_project_task_views.xml',
        'views/menus.xml',
    ],
    'application': True,
    'installable': True,
}
