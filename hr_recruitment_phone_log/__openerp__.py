# -*- coding: utf-8 -*-
# (c) 2016 credativ ltd. - Ondřej Kuzník
# (c) 2016 Trever L. Adams
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Show phonecalls on HR Applicant',
    'summary': 'Adds a phonecall log to HR Applicant',
    'version': '9.0.1.0.0',
    'category': 'Human Resources',
    'author': 'credativ ltd., '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': [
        'logcall',
        'hr_recruitment_phone',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/recruitment_view.xml',
    ],
    'application': True,
    'installable': True,
}
