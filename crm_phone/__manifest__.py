# Copyright 2014-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "CRM Phone",
    "version": "16.0.1.0.1",
    "category": "Phone",
    "license": "AGPL-3",
    "summary": "Improve phone support in CRM",
    "author": "Akretion,Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/connector-telephony",
    "depends": ["base_phone", "crm"],
    "external_dependencies": {"python": ["phonenumbers"]},
    "conflicts": ["crm_voip"],
    "data": [
        "security/phonecall_security.xml",
        "security/ir.model.access.csv",
        "views/crm_phonecall.xml",
        "views/crm_lead.xml",
        "views/res_partner.xml",
        "views/res_users.xml",
        "wizard/number_not_found_view.xml",
        "wizard/create_crm_phonecall_view.xml",
    ],
    "demo": ["demo/crm_phonecall.xml"],
    "installable": True,
    "auto_install": True,
}
