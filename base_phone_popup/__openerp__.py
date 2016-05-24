# -*- coding: utf-8 -*-
# © 2014-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    'name': 'Base Phone Pop-up',
    'version': '9.0.1.0.0',
    'category': 'Phone',
    'license': 'AGPL-3',
    'summary': 'Pop-up the related form view to the user on incoming calls',
    'description': """
Base Phone Pop-up
=================

When the user receives a phone call, OpenERP can automatically open the
corresponding partner/lead/employee/... in a pop-up without any action from the
user.

The module *web_action_request* can be downloaded with Mercurial:

hg clone http://bitbucket.org/anybox/web_action_request

It depends on 2 other modules, *web_longpolling* and *web_socketio*, that can
be downloaded with this command:

hg clone http://bitbucket.org/anybox/web_socketio

You will find some hints in this documentation :
https://bitbucket.org/anybox/web_action_request

Warning : proxying WebSockets is only supported since Nginx 1.3.13 ; the
feature provided by this module won't work with older versions of Nginx.

TODO : document this new feature on the Akretion Web site :
http://www.akretion.com/products-and-services/openerp-asterisk-voip-connector
""",
    'author': "Akretion,Odoo Community Association (OCA)",
    'website': 'http://www.akretion.com/',
    'depends': ['base_phone', 'web_action_request'],
    'data': ['res_users_view.xml'],
    'installable': True,
}
