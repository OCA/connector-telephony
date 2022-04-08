# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sms OVH HTTP",
    "summary": "Send sms using ovh http API",
    "version": "14.0.1.0.1",
    "category": "SMS",
    "website": "https://github.com/OCA/connector-telephony",
    "author": "Akretion, Odoo Community Association (OCA)",
    "maintainers": ["sebastienbeau"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": ["base_phone", "sms", "iap_alternative_provider"],
    "data": [
        "views/iap_account_view.xml",
        "views/sms_sms_view.xml",
    ],
    "demo": [],
    "qweb": [],
}
