# Copyright 2026 INVITU (<https://www.invitu.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import secrets

from odoo import api, fields, models


class IapAccount(models.Model):
    _inherit = "iap.account"

    provider = fields.Selection(
        selection_add=[("sms_smsbox_http", "SMSBOX (HTTP API)")],
        ondelete={"sms_smsbox_http": "cascade"},
    )
    sms_smsbox_http_api_key = fields.Char(
        string="SMSBOX API Key", groups="base.group_system"
    )
    sms_smsbox_http_mode = fields.Selection(
        selection=[("Standard", "Standard"), ("Expert", "Expert")],
        string="SMSBOX Mode",
        default="Standard",
        help="Expert mode sends with the SMSBOX Sender, Standard mode with a "
        "short code.",
    )
    sms_smsbox_http_sender = fields.Char(
        string="SMSBOX Sender",
        help="Sender name registered in SMSBOX, used in Expert mode only.",
    )
    sms_smsbox_http_strategy = fields.Selection(
        selection=[
            ("1", "Private"),
            ("2", "Alert / Notification"),
            ("3", "Group (non commercial)"),
            ("4", "Commercial"),
        ],
        string="SMSBOX Strategy",
        default="2",
    )
    sms_smsbox_http_callback_token = fields.Char(
        string="SMSBOX Callback Token",
        compute="_compute_sms_smsbox_http_callback_token",
        store=True,
        readonly=False,
        copy=False,
        groups="base.group_system",
    )
    sms_smsbox_http_callback_url = fields.Char(
        string="SMSBOX Delivery Reports URL",
        compute="_compute_sms_smsbox_http_callback_url",
        groups="base.group_system",
    )

    @api.depends("provider")
    def _compute_sms_smsbox_http_callback_token(self):
        for account in self:
            if (
                account.provider == "sms_smsbox_http"
                and not account.sms_smsbox_http_callback_token
            ):
                account.sms_smsbox_http_callback_token = secrets.token_urlsafe(24)

    @api.depends("sms_smsbox_http_callback_token")
    def _compute_sms_smsbox_http_callback_url(self):
        for account in self:
            token = account.sms_smsbox_http_callback_token
            account.sms_smsbox_http_callback_url = (
                f"{account.get_base_url()}/sms_smsbox_http/status/{token}"
                if token
                else False
            )

    def _get_service_from_provider(self):
        if self.provider == "sms_smsbox_http":
            return self.env.ref("sms_smsbox_http.iap_service_sms_smsbox_http")
        return super()._get_service_from_provider()
