# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis@via.ecp.fr>
# @migration from 12.0 to 13.0: Christophe Langenberg <Christophe@Langenberg.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Base Phone",
    "version": "17.0.1.0.1",
    "category": "Phone",
    "license": "AGPL-3",
    "summary": "Validate phone numbers",
    "author": "Akretion,Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/connector-telephony",
    "depends": ["phone_validation", "base_setup"],
    "external_dependencies": {"python": ["phonenumbers"]},
    "data": [
        "security/phone_security.xml",
        "security/ir.model.access.csv",
        "wizard/res_config_settings.xml",
        "views/res_users_view.xml",
        "wizard/reformat_all_phonenumbers_view.xml",
        "wizard/number_not_found_view.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "base_phone/static/src/components/**/*",
        ],
    },
    "installable": True,
}
