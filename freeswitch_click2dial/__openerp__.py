# -*- coding: utf-8 -*-
# © 2010-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# © 2014-2016 Trever L. Adams
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    'name': 'FreeSWITCH Click2dial',
    'version': '9.0.1.0.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'FreeSWITCH-Odoo connector',
    'author': "Trever L. Adams, Akretion,Odoo Community Association (OCA)",
    'website': 'https://github.com/treveradams/connector-telephony',
    'depends': ['base_phone'],
    'external_dependencies': {'python': ['freeswitchESL']},
    'data': [
        'freeswitch_server_view.xml',
        'res_users_view.xml',
        'security/ir.model.access.csv',
        'web_freeswitch_click2dial.xml',
        ],
    'demo': ['freeswitch_click2dial_demo.xml'],
    'qweb': ['static/src/xml/*.xml'],
    'css': ['static/src/css/*.css'],
    'application': True,
    'installable': True,
}
