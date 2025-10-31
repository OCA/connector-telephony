# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from unittest.mock import patch

from odoo.tests.common import TransactionCase

from odoo.addons.iap.tools.iap_tools import iap_patch


def iap_post(json_result):
    class mock_request:
        def raise_for_status(self):
            pass

        def json(self):
            return json_result

    def return_mock_request(*args, **kwargs):
        return mock_request()

    return return_mock_request


@patch("odoo.addons.iap.tools.iap_tools.requests.post")
@patch("odoo.addons.sms.models.sms_api.SmsApi._contact_iap")
class TestSmsAlternativeProvider(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.iap_gateway = cls.env.ref("sms_alternative_provider.gateway_iap")

    def setUp(self):
        super().setUp()
        # disable core's disabling of iap, we patch the call ourselves
        iap_patch.stop()

    def test_iap(self, patched_contact_iap, patched_iap_post):
        """Test that without extra configuration, we just use IAP"""
        self.env["iap.account"].search([("service_name", "=", "sms")]).unlink()
        sms = self.env["sms.sms"].create({"number": "424242", "body": "hello world"})
        patched_iap_post.side_effect = iap_post(
            {"result": [{"res_id": sms.id, "state": "success"}]}
        )
        patched_contact_iap.return_value = [{"res_id": sms.id, "state": "success"}]

        sms.send(unlink_sent=False)
        self.assertEqual(sms.state, "sent")
        self.assertEqual(sms.sms_gateway_id, self.iap_gateway)

    def test_restrictions(self, patched_contact_iap, patched_iap_post):
        """Test that we can restrict gateways to certain numbers"""
        gw_no_restriction = self.iap_gateway
        gw_no_restriction.sequence = 99
        gw_31 = self.iap_gateway.copy({"sequence": 1, "prefix": "+31"})
        gw_32_49 = gw_31.copy({"sequence": 2, "prefix": "+32 +49"})

        sms = self.env["sms.sms"].create(
            {"number": "+49 424242", "body": "hello world"}
        )
        patched_iap_post.side_effect = iap_post(
            {"result": [{"res_id": sms.id, "state": "success"}]}
        )
        patched_contact_iap.return_value = [{"res_id": sms.id, "state": "success"}]
        sms.send(unlink_sent=False)
        self.assertEqual(sms.state, "sent")
        self.assertEqual(sms.sms_gateway_id, gw_32_49)

        sms = self.env["sms.sms"].create({"number": "+1 424242", "body": "hello world"})
        patched_iap_post.side_effect = iap_post(
            {"result": [{"res_id": sms.id, "state": "success"}]}
        )
        patched_contact_iap.return_value = [{"res_id": sms.id, "state": "success"}]
        sms.send(unlink_sent=False)
        self.assertEqual(sms.state, "sent")
        self.assertEqual(sms.sms_gateway_id, gw_no_restriction)

        gw_no_restriction.prefix = "+2"
        sms = self.env["sms.sms"].create({"number": "+1 424242", "body": "hello world"})
        with self.assertLogs("odoo.addons.sms.models.sms_sms") as sms_logs:
            sms.send()
        self.assertTrue(
            any(
                "No suitable provider found for messages" in log
                for log in sms_logs.output
            )
        )
        self.assertEqual(sms.state, "error")
        self.assertEqual(sms.failure_type, "sms_server")
