# -*- coding: utf-8 -*-
# (c) 2016 credativ ltd. - Ondřej Kuzník
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Show phonecalls on partner',
    'summary': 'Adds a phonecall log to partner',
    'version': '9.0.1.0.0',
    'category': 'Customer Relationship Management',
    'author': 'credativ ltd., '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': [
        'crm_phone',
    ],
    'data': [
        'views/partner_view.xml',
    ],
    'application': True,
    'installable': True,
}
