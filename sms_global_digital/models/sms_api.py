import logging
import re

import requests

from odoo.addons.sms.tools.sms_api import SmsApi

_logger = logging.getLogger(__name__)

GLOBAL_DIGITAL_ENDPOINT = "https://www.globaldigital.pt/api/sms/send.php?token="


class SmsApiGlobalDigital(SmsApi):
    """Send SMS through the Global Digital HTTP API.

    API documentation: https://www.globaldigital.pt/pt/documentacao
    (available in the Global Digital customer area, login required).
    """

    PROVIDER_TO_SMS_FAILURE_TYPE = SmsApi.PROVIDER_TO_SMS_FAILURE_TYPE | {
        "test_mode": "sms_test",
    }

    def _prepare_global_digital_params(self, numbers, message):
        # Phone numbers must include the country code, digits only (no "+")
        return {
            "sender": self.account.sms_global_digital_sender_id,
            "phone_numbers": ",".join(re.sub(r"\D", "", n) for n in numbers),
            "message": message,
        }

    def _send_sms_with_global_digital(self, number_entries, message):
        """Send `message` to `number_entries` with a single API request.

        :param number_entries: list of ``{"number": ..., "uuid": ...}``
        :return: dict mapping each number to an Odoo provider state
        """
        states = {entry["number"]: "wrong_number_format" for entry in number_entries}
        to_send = [entry for entry in number_entries if entry["number"]]
        if not to_send:
            return states
        if self.account.sms_global_digital_test_mode:
            # Test mode (e.g. neutralized databases): never send a real SMS;
            # the send resolves as an error so the chatter shows it was not sent
            states.update({entry["number"]: "test_mode" for entry in to_send})
            return states
        if not self.account.sms_global_digital_api_key:
            # Missing provider configuration is not a server error
            _logger.info("Global Digital SMS not sent: no API key configured")
            states.update({entry["number"]: "unregistered" for entry in to_send})
            return states
        try:
            response = requests.post(
                GLOBAL_DIGITAL_ENDPOINT
                + self.account.sms_global_digital_api_key
                + "&action=simple",
                json=self._prepare_global_digital_params(
                    [entry["number"] for entry in to_send], message
                ),
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()["data"][0]
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            _logger.info("Global Digital SMS request failed: %s", e)
            states.update({entry["number"]: "server_error" for entry in to_send})
            return states

        failed = set(data.get("failed_numbers") or [])
        invalid = set(data.get("invalid_numbers") or [])
        for entry in to_send:
            raw_number = re.sub(r"\D", "", entry["number"])
            if raw_number in invalid:
                states[entry["number"]] = "wrong_number_format"
            elif raw_number in failed:
                states[entry["number"]] = "server_error"
            else:
                states[entry["number"]] = "success"
        return states

    def _is_sent_with_global_digital(self):
        return self.account.provider == "sms_global_digital"

    def _send_sms_batch(self, messages, delivery_reports_url=False):
        if self._is_sent_with_global_digital():
            results = []
            for message in messages:
                states = self._send_sms_with_global_digital(
                    message["numbers"], message["content"]
                )
                results += [
                    {
                        "state": states[number["number"]],
                        "credit": 0,
                        "uuid": number["uuid"],
                        "failure_reason": (
                            self.env._("Test mode: not sent to the Global Digital API")
                            if states[number["number"]] == "test_mode"
                            else False
                        ),
                    }
                    for number in message["numbers"]
                ]
            return results
        return super()._send_sms_batch(
            messages, delivery_reports_url=delivery_reports_url
        )
