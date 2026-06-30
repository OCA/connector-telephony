# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.tests import TransactionCase

from ..models.sms_api import OVH_API_ENDPOINT


class SendSmsCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.account = cls.env["iap.account"].create(
            {
                "name": "OVH",
                "provider": "sms_ovh_http",
                "sms_ovh_http_app_key": "app_key_test",
                "sms_ovh_http_app_secret": "app_secret_test",
                "sms_ovh_http_consumer_key": "consumer_key_test",
                "sms_ovh_http_service_name": "sms-test-1",
                "sms_ovh_http_from": "+33642424242",
            }
        )

    def test_check_service_name(self):
        self.assertEqual(self.account.service_name, "sms")

    def test_sending_sms(self):
        with patch("ovh.Client") as mock_client:
            mock_instance = mock_client.return_value
            self.env["sms.api"]._send_sms_batch(
                [
                    {
                        "number": "+3360707070707",
                        "content": "Alpha Bravo Charlie",
                        "res_id": 42,
                    }
                ]
            )
            mock_client.assert_called_once_with(
                endpoint=OVH_API_ENDPOINT,
                application_key="app_key_test",
                application_secret="app_secret_test",
                consumer_key="consumer_key_test",
            )
            mock_instance.post.assert_called_once_with(
                "/sms/sms-test-1/jobs",
                message="Alpha Bravo Charlie",
                sender="+33642424242",
                receivers=["+3360707070707"],
                noStopClause=True,
            )

    def test_partner_message_sms(self):
        with patch("ovh.Client") as mock_client:
            mock_instance = mock_client.return_value
            partner = self.env["res.partner"].create(
                {"name": "FOO", "mobile": "+3360707070707"}
            )
            partner._message_sms("Alpha Bravo Charlie")
            mock_client.assert_called_once_with(
                endpoint=OVH_API_ENDPOINT,
                application_key="app_key_test",
                application_secret="app_secret_test",
                consumer_key="consumer_key_test",
            )
            mock_instance.post.assert_called_once_with(
                "/sms/sms-test-1/jobs",
                message="Alpha Bravo Charlie",
                sender="+33642424242",
                receivers=["+3360707070707"],
                noStopClause=True,
            )
