# Copyright 2014-2018 Akretion France
# @author: Alexis de Lattre <alexis@via.ecp.fr>
# @migration from 12.0 to 13.0: Christophe Langenberg <Christophe@Langenberg.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Base Phone",
    "version": "13.0.1.0.1",
    "category": "Phone",
    "license": "AGPL-3",
    "summary": "Validate phone numbers",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "http://www.akretion.com/",
    "depends": ["phone_validation", "base_setup"],
    "external_dependencies": {"python": ["phonenumbers"]},
    "data": [
        "security/phone_security.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings.xml",
        "views/res_users_view.xml",
        "wizard/reformat_all_phonenumbers_view.xml",
        "wizard/number_not_found_view.xml",
        "views/web_phone.xml",
    ],
    "qweb": ["static/src/xml/phone.xml"],
    "images": [],
    "installable": True,
}
