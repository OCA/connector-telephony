# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IapAccount(models.Model):
    _inherit = "iap.account"

    provider = fields.Selection(selection_add=[("sms_ovh_http", "SMS OVH http")])
    sms_ovh_http_account = fields.Char(string="Account")
    sms_ovh_http_login = fields.Char(string="Login")
    sms_ovh_http_password = fields.Char(string="Password")
    sms_ovh_http_from = fields.Char(string="Expeditor Number")

    def _get_service_from_provider(self):
        if self.provider == "sms_ovh_http":
            return "sms"

    @property
    def _server_env_fields(self):
        res = super()._server_env_fields
        res.update(
            {
                "sms_ovh_http_account": {},
                "sms_ovh_http_login": {},
                "sms_ovh_http_password": {},
                "sms_ovh_http_from": {},
            }
        )
        return res
