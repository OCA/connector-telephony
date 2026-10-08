import json
from unittest import mock
from urllib.parse import parse_qs, urlparse

import requests

from odoo.tests import TransactionCase


class GlobalDigitalApiMock:
    """``requests.post`` compatible mock of the Global Digital send endpoint.

    API documentation: https://www.globaldigital.pt/pt/documentacao
    (available in the Global Digital customer area, login required).

    :param token: API key the mock accepts; any other token gets a 401
    :param invalid_numbers: numbers reported back in ``invalid_numbers``
    :param failed_numbers: numbers reported back in ``failed_numbers``
    """

    def __init__(self, token, invalid_numbers=(), failed_numbers=()):
        self.token = token
        self.invalid_numbers = set(invalid_numbers)
        self.failed_numbers = set(failed_numbers)
        self.calls = []

    def post(self, url, **kwargs):
        """Emulate ``requests.post`` on ``/api/sms/send.php``.

        API spec::

            POST /api/sms/send.php?token={api_key}&action=simple
            {"sender": str,
             "phone_numbers": "digits-only-number,digits-only-number,..."
                             (country code included, no "+"),
             "message": str}

            200 {"status": "200", "message": "OK.",
                 "data": [{"total_sent": str, "total_failed": str,
                           "failed_numbers": [str],
                           "total_invalid": str, "invalid_numbers": [str]}]}
            Errors: 400 Bad Request, 401 Unauthorized, 403 Forbidden,
                    500/503 server errors
        """
        payload = kwargs.get("json") or {}
        self.calls.append({"url": url, "json": payload})
        params = parse_qs(urlparse(url).query)
        if params.get("action") != ["simple"] or not params.get("token"):
            return self._response(400, "Bad Request.")
        if params["token"] != [self.token]:
            return self._response(401, "Unauthorized.")
        numbers = (payload.get("phone_numbers") or "").split(",")
        invalid = [n for n in numbers if n in self.invalid_numbers]
        failed = [n for n in numbers if n in self.failed_numbers]
        return self._response(
            200,
            "OK.",
            data=[
                {
                    "total_sent": str(len(numbers) - len(invalid) - len(failed)),
                    "total_failed": str(len(failed)),
                    "failed_numbers": failed,
                    "total_invalid": str(len(invalid)),
                    "invalid_numbers": invalid,
                }
            ],
        )

    @staticmethod
    def _response(status_code, message, data=None):
        body = {"status": str(status_code), "message": message}
        if data is not None:
            body["data"] = data
        response = requests.models.Response()
        response.status_code = status_code
        response._content = json.dumps(body).encode()
        response.headers["Content-Type"] = "application/json"
        return response


class TestSmsGlobalDigital(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.api_key = "gd-test-api-key"
        cls.env["iap.account"].create(
            {
                "name": "Global Digital",
                "provider": "sms_global_digital",
                "service_id": cls.env.ref("sms.iap_service_sms").id,
                "sms_global_digital_sender_id": "MyCompany",
                "sms_global_digital_api_key": cls.api_key,
                # scoped to the current company so iap.account.get() prefers
                # it over a pre-existing global Odoo IAP account
                "company_ids": [(4, cls.env.company.id)],
            }
        )

    def _send_sms(self, numbers, body="Hello"):
        """Create outgoing SMS records for ``numbers`` and send them."""
        sms = self.env["sms.sms"].create(
            [{"number": number, "body": body} for number in numbers]
        )
        sms.send()
        return sms

    def test_send_sms(self):
        """An outgoing SMS is sent through the Global Digital API."""
        api = GlobalDigitalApiMock(token=self.api_key)
        with mock.patch.object(requests, "post", api.post):
            sms = self._send_sms(["+351911111111"])
        self.assertEqual(sms.state, "pending")
        (call,) = api.calls
        self.assertIn("action=simple", call["url"])
        self.assertEqual(call["json"]["sender"], "MyCompany")
        self.assertEqual(call["json"]["phone_numbers"], "351911111111")
        self.assertEqual(call["json"]["message"], "Hello")

    def test_send_sms_batch(self):
        """SMS sharing the same body are sent in a single API request."""
        api = GlobalDigitalApiMock(token=self.api_key)
        with mock.patch.object(requests, "post", api.post):
            sms = self._send_sms(["+351911111111", "+351922222222"])
        self.assertEqual(len(api.calls), 1)
        self.assertEqual(
            api.calls[0]["json"]["phone_numbers"], "351911111111,351922222222"
        )
        self.assertEqual(set(sms.mapped("state")), {"pending"})

    def test_send_sms_invalid_number(self):
        """A number rejected by the API gets the number format error."""
        api = GlobalDigitalApiMock(token=self.api_key, invalid_numbers={"351911111111"})
        with mock.patch.object(requests, "post", api.post):
            sms = self._send_sms(["+351911111111"])
        self.assertEqual(sms.state, "error")
        self.assertEqual(sms.failure_type, "sms_number_format")

    def test_send_sms_failed_number(self):
        """A number the API failed to reach gets the server error."""
        api = GlobalDigitalApiMock(token=self.api_key, failed_numbers={"351911111111"})
        with mock.patch.object(requests, "post", api.post):
            sms = self._send_sms(["+351911111111"])
        self.assertEqual(sms.state, "error")
        self.assertEqual(sms.failure_type, "sms_server")

    def test_send_sms_unauthorized(self):
        """A rejected API key marks the SMS with a server error."""
        api = GlobalDigitalApiMock(token="other-api-key")
        with mock.patch.object(requests, "post", api.post):
            sms = self._send_sms(["+351911111111"])
        self.assertEqual(sms.state, "error")
        self.assertEqual(sms.failure_type, "sms_server")
