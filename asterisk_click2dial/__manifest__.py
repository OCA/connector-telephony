# Copyright 2010-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Asterisk connector",
    "version": "15.0.1.0.0",
    "category": "Phone",
    "license": "AGPL-3",
    "summary": "Asterisk-Odoo connector",
    "author": "Akretion,Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/connector-telephony",
    "depends": ["base_phone"],
    "external_dependencies": {"python": ["requests"]},
    "data": [
        "security/ir.model.access.csv",
        "security/asterisk_security.xml",
        "views/asterisk_server.xml",
        "views/res_users.xml",
    ],
    "assets": {
        "web.assets_qweb": [
            "asterisk_click2dial/static/src/xml/asterisk_click2dial.xml"
        ],
        "web.assets_backend": [
            "asterisk_click2dial/static/src/js/asterisk_click2dial.js"
        ],
        "web._assets_primary_variables": [
            "asterisk_click2dial/static/src/scss/asterisk.scss"
        ],
    },
    "demo": ["demo/asterisk_click2dial_demo.xml"],
}
