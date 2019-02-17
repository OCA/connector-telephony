# -*- coding: utf-8 -*-
# © 2014-2019 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>) & K (Vladimir Andreyev hoka.spb@gmail.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Base Phone Pop-up',
    'version': '11.0.1.0.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'Pop-up the related form view to the user on incoming calls',
    'description': """
Base Phone Pop-up
=================
When the user receives a phone call, OpenERP can automatically open the corresponding partner/lead/employee/... 
in a pop-up without any action from the user.
http://www.akretion.com/products-and-services/openerp-asterisk-voip-connector
""",
    'author': "Akretion,Odoo Community Association (OCA) & K",
    'website': 'http://www.akretion.com/',
    'depends': ['base_phone'],
    'data': [
             'views/res_users.xml',
             'views/template.xml',
            ],
    'installable': True,
}
