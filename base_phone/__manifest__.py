# -*- coding: utf-8 -*-
# Copyright 2014-2018 Akretion France
# @author: Alexis de Lattre <alexis@via.ecp.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Base Phone',
    'version': '12.0.1.0.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'Validate phone numbers',
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com/',
    'depends': ['phone_validation', 'base_setup'],
    'external_dependencies': {'python': ['phonenumbers']},
    'data': [
        'security/phone_security.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'views/res_users_view.xml',
        'wizard/reformat_all_phonenumbers_view.xml',
<<<<<<< HEAD
<<<<<<< HEAD
        'web_phone.xml',
=======
        'wizard/number_not_found_view.xml',
        ],
    'js': [
        'static/src/js/*.js',
        'static/lib/js/*.js',
>>>>>>> Feature "Open Calling Partner" replaced by "Open Caller", with a completely new behavior
=======
        'wizard/number_not_found_view.xml',
        'views/web_phone.xml',
>>>>>>> Port to v12 base_phone, asterisk_click2dial, crm_phone, hr_phone, event_phone and hr_recruitment_phone
        ],
    'qweb': ['static/src/xml/phone.xml'],
    'images': [],
    'installable': True,
}
