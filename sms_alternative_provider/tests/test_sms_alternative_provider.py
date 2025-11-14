# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo.tests.common import TransactionCase


class TestSmsGateway(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Disable mail notifications to avoid search on non-stored sms_id
        cls.env = cls.env(
            context=dict(
                cls.env.context, mail_create_nosubscribe=True, mail_notify_noemail=True
            )
        )

        cls.gateway = cls.env["ir.sms.gateway"].create(
            {
                "name": "Test Gateway",
                "gateway_type": "iap",
                "sequence": 1,
                "active": True,
            }
        )

    def test_handle_results_success(self):
        sms = self.env["sms.sms"].create(
            {
                "number": "+11111",
                "body": "OK",
                "sms_gateway_id": self.gateway.id,
            }
        )

        results = [{"uuid": sms.uuid, "state": "success"}]

        self.gateway._handle_results([{"uuid": sms.uuid}], results)

        self.assertEqual(sms.state, "sent")
        self.assertFalse(sms.failure_type)

    def test_handle_results_error(self):
        sms = self.env["sms.sms"].create(
            {
                "number": "+22222",
                "body": "ERR",
                "sms_gateway_id": self.gateway.id,
            }
        )

        results = [{"uuid": sms.uuid, "state": "server_error"}]

        self.gateway._handle_results([{"uuid": sms.uuid}], results)

        self.assertEqual(sms.state, "error")
        self.assertEqual(sms.failure_type, "sms_server")
