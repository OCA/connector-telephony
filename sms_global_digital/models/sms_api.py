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

    def _prepare_global_digital_params(self, numbers, message):
        # Phone numbers must include the country code, digits only (no "+")
        return {
            "sender": self.account.sms_global_digital_sender_id,
            "phone_numbers": ",".join(re.sub(r"\D", "", n) for n in numbers),
            "message": message,
        }

    def _send_sms_with_global_digital(self, numbers, message):
        """Send `message` to `numbers` with a single API request.

        :return: dict mapping each number to an Odoo provider state
        """
        states = dict.fromkeys(numbers, "wrong_number_format")
        to_send = [number for number in numbers if number]
        if not to_send:
            return states
        try:
            response = requests.post(
                GLOBAL_DIGITAL_ENDPOINT
                + self.account.sms_global_digital_api_key
                + "&action=simple",
                json=self._prepare_global_digital_params(to_send, message),
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()["data"][0]
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:
            _logger.info("Global Digital SMS request failed: %s", e)
            states.update(dict.fromkeys(to_send, "server_error"))
            return states

        failed = set(data.get("failed_numbers") or [])
        invalid = set(data.get("invalid_numbers") or [])
        for number in to_send:
            raw_number = re.sub(r"\D", "", number)
            if raw_number in invalid:
                states[number] = "wrong_number_format"
            elif raw_number in failed:
                states[number] = "server_error"
            else:
                states[number] = "success"
        return states

    def _is_sent_with_global_digital(self):
        return self.account.provider == "sms_global_digital"

    def _send_sms_batch(self, messages, delivery_reports_url=False):
        if self._is_sent_with_global_digital():
            results = []
            for message in messages:
                numbers = [number["number"] for number in message["numbers"]]
                states = self._send_sms_with_global_digital(numbers, message["content"])
                results += [
                    {
                        "state": states[number["number"]],
                        "credit": 0,
                        "uuid": number["uuid"],
                    }
                    for number in message["numbers"]
                ]
            return results
        return super()._send_sms_batch(
            messages, delivery_reports_url=delivery_reports_url
        )
