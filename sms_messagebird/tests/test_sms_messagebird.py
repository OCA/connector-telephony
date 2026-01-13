# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from unittest.mock import patch

from odoo.tests.common import TransactionCase

from odoo.addons.sms_alternative_provider.tests.test_sms_alternative_provider import (
    iap_post as messagebird_post,
)


@patch("odoo.addons.sms_messagebird.models.ir_sms_gateway.requests.post")
class TestSmsMessagebird(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["ir.sms.gateway"].search([]).unlink()
        cls.provider = cls.env["ir.sms.gateway"].create(
            {
                "name": "messagebird test provider",
                "gateway_type": "messagebird",
                "messagebird_apikey": "42",
            }
        )

    def test_success(self, patched_post):
        """Test sending an SMS successfully"""
        sms = self.env["sms.sms"].create({"number": "424242", "body": "hello world"})
        patched_post.side_effect = messagebird_post(
            {"recipients": {"items": [{"recipient": "424242", "status": "sent"}]}}
        )
        sms.send(unlink_sent=False)
        self.assertEqual(sms.state, "sent")
        self.assertEqual(sms.sms_gateway_id, self.provider)

    def test_failure(self, patched_post):
        """Test sending an SMS with errors"""
        sms = self.env["sms.sms"].create({"number": "+1 424242", "body": "hello world"})
        patched_post.side_effect = messagebird_post(
            {"errors": {"description": "messagebird error"}},
        )

        with self.assertLogs(
            "odoo.addons.sms_messagebird.models.ir_sms_gateway"
        ) as sms_logs:
            sms.send()
        self.assertTrue(any("messagebird error" in log for log in sms_logs.output))
        self.assertEqual(sms.state, "error")
        self.assertEqual(sms.failure_type, "sms_server")
