# -*- coding: utf-8 -*-
# © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'CRM Phone',
    'version': '9.0.1.0.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'Validate phone numbers in CRM',
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com/',
    'depends': ['base_phone', 'crm'],
    'conflicts': ['crm_voip'],
    'external_dependencies': {'python': ['phonenumbers']},
    'data': [
        'security/phonecall_security.xml',
        'security/ir.model.access.csv',
        'view/crm_phonecall.xml',
        'view/crm_lead.xml',
        'view/res_partner.xml',
        'view/res_users.xml',
        'wizard/number_not_found_view.xml',
        'wizard/create_crm_phonecall_view.xml',
        ],
    'demo': ['demo/crm_phonecall.xml'],
    'installable': True,
    'auto_install': True,
}
