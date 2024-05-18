# Copyright 2010-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Asterisk connector",
    "version": "17.0.1.0.0",
    "category": "Phone",
    "license": "AGPL-3",
    "summary": "Asterisk-Odoo connector",
    "author": "Akretion,Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/connector-telephony",
    "depends": ["base_phone"],
    "external_dependencies": {"python": ["requests"]},
    "data": [
        "views/asterisk_server.xml",
        "views/res_users.xml",
        "security/ir.model.access.csv",
        "security/asterisk_security.xml",
    ],
    "demo": ["demo/asterisk_click2dial_demo.xml"],
    "qweb": ["static/src/xml/asterisk_click2dial.xml"],
    "application": True,
    "installable": True,
    "assets": {
        "web.assets_backend": [
            "asterisk_click2dial/static/src/scss/*.scss",
            "asterisk_click2dial/static/src/components/**/*.js",
            "asterisk_click2dial/static/src/components/**/*.xml",
        ],
    },
}
