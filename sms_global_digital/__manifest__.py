# Copyright 2022 ?Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sms Global Digital",
    "summary": "Send sms using global digital API",
    "version": "19.0.1.0.0",
    "category": "SMS",
    "website": "https://github.com/OCA/connector-telephony",
    "author": "Exo Software, Odoo Community Association (OCA)",
    "maintainers": ["tiagosrangel"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sms", "iap_alternative_provider"],
    "data": ["views/iap_account_views.xml"],
}
