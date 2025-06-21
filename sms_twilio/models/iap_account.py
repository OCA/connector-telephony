# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    from twilio.rest import Client
except ImportError:
    _logger.error("Cannot import twilio dependencies", exc_info=True)


class IapAccount(models.Model):
    _inherit = "iap.account"

    twilio_production_env = fields.Boolean(
        "Production Environment",
        help="Test credentials can currently be used to interact with"
        " the following three resources:\n"
        " - Buying phone numbers"
        " - Sending SMS messages"
        " - Making calls\n"
        "If in test environment, although being able to perform the above actions,"
        " they will not show in your Twilio account, and the only valid Twilio Number"
        " is the TEST Phone.\n"
        "Production keys are needed to perform all the other actions"
        " like retrieve account balance or phone numbers."
        " If this field is not enabled, the three cases mentioned above"
        " will be performed using test credentials.",
    )

    provider = fields.Selection(
        selection_add=[("twilio", "Twilio")],
        ondelete={"twilio": "cascade"},
    )

    twilio_test_account_sid = fields.Char(string="Twilio TEST Account SID")
    twilio_test_auth_token = fields.Char(string="Twilio TEST Auth Token")
    twilio_account_sid = fields.Char(string="Twilio Account SID")
    twilio_auth_token = fields.Char()
    twilio_number_id = fields.Many2one("twilio.phone.number", string="Twilio Number")

    twilio_balance_account = fields.Char(
        string="Account Balance", compute="_compute_balance_twilio"
    )

    def _get_service_from_provider(self):
        if self.provider == "twilio":
            return "sms"
        return super()._get_service_from_provider()

    def _compute_balance_twilio(self):
        for item in self:
            balance = ""
            if item.twilio_account_sid and item.twilio_auth_token:
                try:
                    # Only work with prod creds
                    client = item.get_twilio_client()
                    balance_obj = client.api.balance.fetch()
                    balance = "%s: %s" % (balance_obj.currency, balance_obj.balance)
                except Exception as e:
                    _logger.error("Twilio Error: '%s'", str(e))
            item.twilio_balance_account = balance

    def retrieve_phone_numbers(self):
        for item in self:
            if not item.twilio_account_sid or not item.twilio_auth_token:
                raise UserError(_("Configure Twilio Credentials first"))
            try:
                # Only work with prod creds
                client = item.get_twilio_client()
                phone_numbers = client.incoming_phone_numbers.list()
                for phone in phone_numbers:
                    if not self.env["twilio.phone.number"].search(
                        [("sid", "=", phone.sid)]
                    ):
                        self.env["twilio.phone.number"].sudo().create(
                            {
                                "name": phone.friendly_name,
                                "phone_number": phone.phone_number,
                                "has_sms_enabled": phone.capabilities["sms"],
                                "sid": phone.sid,
                            }
                        )
                if not (
                    self.twilio_production_env
                    and self.env["twilio.phone.number"].search([("sid", "=", "test")])
                ):
                    self.env["twilio.phone.number"].sudo().create(
                        {
                            "name": "TEST Phone",
                            "phone_number": "+15005550006",
                            "has_sms_enabled": True,
                            "sid": "test",
                        }
                    )

            except Exception as e:
                _logger.error("Twilio Error: '%s'", str(e))

    def get_twilio_client(self, production=True):
        if not self.twilio_account_sid or not self.twilio_auth_token:
            raise UserError(_("Configure Twilio Credentials first"))
        if not production:
            return Client(self.twilio_test_account_sid, self.twilio_test_auth_token)
        return Client(self.twilio_account_sid, self.twilio_auth_token)

    @property
    def _server_env_fields(self):
        res = super()._server_env_fields
        res.update(
            {
                "twilio_test_account_sid": {},
                "twilio_test_auth_token": {},
                "twilio_account_sid": {},
                "twilio_auth_token": {},
            }
        )
        return res

    @api.onchange("twilio_production_env")
    def onchange_twilio_production_env(self):
        if self.twilio_production_env:
            if not self.twilio_number_id or self.twilio_number_id == self.env[
                "twilio.phone.number"
            ].search([("sid", "=", "test")]):
                raise UserError(
                    _(
                        "Select a valid Twilio Number before changing to Production"
                        " Environment."
                    )
                )
