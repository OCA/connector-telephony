# -*- coding: utf-8 -*-
# (c) 2016 credativ Ltd (<http://credativ.co.uk>).
# (c) 2016 Trever L. Adams
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html


{
    'name': 'FreeSwitch Phone Log-call',
    'version': '9.0.1.0.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'Necessary bridge between log-call and FreeSWITCH Click2dial',
    'author': "Trever L. Adams,Odoo Community Association (OCA)",
    'website': '',
    'depends': ['logcall', 'freeswitch_click2dial'],
    'data': [
        'security/ir.model.access.csv',
        'views/freeswitch_server_view.xml',
    ],
    'application': True,
    'installable': True,
}
