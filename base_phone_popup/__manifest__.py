# -*- coding: utf-8 -*-
# Copyright 2014-2018 Akretion France
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    'name': 'Base Phone Pop-up',
    'version': '10.0.1.0.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'Show a pop-up on incoming calls',
    'description': """
Base Phone Pop-up
=================

When the user receives a phone call, Odoo will display a notification
at the top-right of the screen that contains a link to the corresponding
partner/lead/employee/... and a link to the *Number not found* wizard.
""",
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com/',
    'depends': ['base_phone', 'web_notify'],
    'installable': True,
}
