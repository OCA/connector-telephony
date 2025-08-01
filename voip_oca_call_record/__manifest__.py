# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Voip OCA Call Record",
    "summary": "Extends VoIP OCA to record calls",
    "version": "18.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/connector-telephony",
    "license": "AGPL-3",
    "category": "Productivity/VOIP",
    "excludes": ["voip"],
    "depends": ["voip_oca"],
    "maintainers": ["jordibforgeflow"],
    "data": [
        "views/voip_call_views.xml",
        "views/res_users_views.xml",
        "views/voip_pbx_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "voip_oca_call_record/static/src/components/call/*",
            "voip_oca_call_record/static/src/services/*",
        ],
    },
    "installable": True,
}
