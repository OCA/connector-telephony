# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IapAccount(models.Model):
    _inherit = "iap.account"

    provider = fields.Selection(
        selection_add=[("sms_ovh_http", "SMS OVH http")],
        ondelete={"sms_ovh_http": "cascade"},
    )
    sms_ovh_http_from = fields.Char(string="Sender Name")
    sms_ovh_http_app_key = fields.Char(string="Application Key")
    sms_ovh_http_app_secret = fields.Char(string="Application Secret")
    sms_ovh_http_consumer_key = fields.Char(string="Consumer Key")
    sms_ovh_http_service_name = fields.Char(string="Service Name")

    def _get_service_from_provider(self):
        if self.provider == "sms_ovh_http":
            return "sms"

    @property
    def _server_env_fields(self):
        res = super()._server_env_fields
        res.update(
            {
                "sms_ovh_http_from": {},
                "sms_ovh_http_app_key": {},
                "sms_ovh_http_app_secret": {},
                "sms_ovh_http_consumer_key": {},
                "sms_ovh_http_service_name": {},
            }
        )
        return res
