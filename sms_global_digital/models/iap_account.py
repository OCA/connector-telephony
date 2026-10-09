import logging

import requests

from odoo import fields, models

_logger = logging.getLogger(__name__)

GLOBAL_DIGITAL_USERS_ENDPOINT = "https://www.globaldigital.pt/api/users/list.php?token="


class IapAccount(models.Model):
    _inherit = "iap.account"

    provider = fields.Selection(
        selection_add=[("sms_global_digital", "SMS Global digital")],
        ondelete={"sms_global_digital": "cascade"},
    )

    sms_global_digital_sender_id = fields.Char(string="Sender ID")
    sms_global_digital_api_key = fields.Char(string="Api Key")
    sms_global_digital_test_mode = fields.Boolean(
        string="Test Mode",
        help="In test mode no SMS is sent to Global Digital: "
        "it is marked as failed with a 'Test Mode' reason instead. "
        "Set automatically by database neutralization.",
    )

    def _get_account_information_from_iap(self):
        # Global Digital accounts fetch their balance from the provider API
        # instead of the Odoo IAP endpoint
        global_digital_accounts = self.filtered(
            lambda account: account.provider == "sms_global_digital"
        )
        for account in global_digital_accounts:
            account._get_global_digital_account_information()
        return super(
            IapAccount, self - global_digital_accounts
        )._get_account_information_from_iap()

    def _get_global_digital_account_information(self):
        """Fetch the account balance from the Global Digital users endpoint.

        GET /api/users/list.php?token={api_key}&action=list returns the
        account data, including the "credits" field.
        """
        if not self.sms_global_digital_api_key:
            return
        try:
            response = requests.get(
                GLOBAL_DIGITAL_USERS_ENDPOINT
                + self.sms_global_digital_api_key
                + "&action=list",
                timeout=10,
            )
            response.raise_for_status()
            credit_balance = response.json()["data"][0]["credits"]
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            _logger.info("Global Digital account info request failed: %s", e)
            return
        self.with_context(disable_iap_update=True, tracking_disable=True).write(
            {"balance": f"{credit_balance} credits"}
        )

    def _get_service_from_provider(self):
        if self.provider == "sms_global_digital":
            return self.env.ref("sms.iap_service_sms")
        return super()._get_service_from_provider()

    @property
    def _server_env_fields(self):
        res = super()._server_env_fields
        res.update(
            {
                "sms_global_digital_sender_id": {},
                "sms_global_digital_api_key": {},
            }
        )
        return res
