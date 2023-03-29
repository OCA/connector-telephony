# © 2023 CONINPE Consultores Informaticos: Telmo Suarez Venero <tsuarez@zertek.es>
# License AGPL-3.0 or later (http://gnu.org/license/agpl.html).
{
    "name": "Centrex VozTelecom Connector",
    "summary": "Integración de la API de Centrex de VozTelecom con Odoo",
    "version": "14.0.1.0.0",
    "author": "Coninpe,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/connector-telephony",
    "category": "Connector",
    "depends": ["crm_phone", "web_notify"],
    "data": [
        "security/ir.model.access.csv",
        "views/voztelecom_config_views.xml",
        "views/crm_phonecall.xml",
        "views/res_partner.xml",
        "data/res_partner_data.xml",
        "data/res_users_data.xml",
    ],
    "installable": True,
}
