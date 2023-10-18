# Copyright 2022 ?Akretion (https://www.akretion.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sms Global Digital",
    "summary": "Send sms using global digital API",
    "version": "16.0.1.0.0",
    "category": "SMS",
    "website": "https://github.com/OCA/connector-telephony",
    "author": "Exo Software",
    "maintainers": ["tiagosrangel"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["base_phone", "sms", "iap_alternative_provider"],
    "data": ["views/iap_account_views.xml", "views/res_config_settings_views.xml"],
}
