# -*- coding: utf-8 -*-
# © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    'name': 'Event Phone',
    'version': '9.0.1.0.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'Validate phone numbers in Events',
    'description': """
Event Phone
===========

This module validate phone numbers in the Event module, just like the
*base_phone* module valide phone numbers in the Partner form. Please refer to
the description of the *base_phone* module for more information.

This module is independant from the Asterisk connector.

Please contact Alexis de Lattre from Akretion <alexis.delattre@akretion.com>
for any help or question about this module.
""",
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com/',
    'depends': ['base_phone', 'event'],
    'data': [
        'security/ir.model.access.csv',
        'event_view.xml',
        ],
    'installable': True,
    'auto_install': True,
}
