# Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "SMS sendinblue HTTP",
    "summary": "Send sms using sendinblue http API",
    "version": "15.0.1.0.0",
    "category": "SMS",
    "website": "https://github.com/OCA/connector-telephony",
    "author": "Pierre Verkest <pierreverkest84@gmail.com>, Odoo Community Association (OCA)",
    "maintainers": ["petrus-v"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": ["sms", "iap_alternative_provider"],
    "data": [
        "views/iap_account_view.xml",
        "views/sms_sms_view.xml",
    ],
    "demo": [],
}
