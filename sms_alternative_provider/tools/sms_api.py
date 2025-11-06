# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo.addons.sms.tools.sms_api import SmsApi


class SmsApiCustom(SmsApi):
    """
    Extend the standard SmsApi (IAP) behavior to optionally route SMS
    through ir.sms.gateway if not forced via context.
    """

    def _send_sms_batch(self, messages, delivery_reports_url=False):
        """
        Divert SMS sending to the gateway model unless 'force_iap' is set
        in the context.
        """
        if self.env.context.get("force_iap"):
            # Default IAP behavior
            return super()._send_sms_batch(
                messages, delivery_reports_url=delivery_reports_url
            )

        # Custom: use ir.sms.gateway instead
        # Convert messages to gateway format
        gateway_messages = []
        for message in messages:
            for number_info in message.get("numbers", []):
                gateway_messages.append(
                    {
                        "id": None,  # Will be filled by gateway
                        "uuid": number_info.get("uuid"),
                        "number": number_info.get("number"),
                        "content": message.get("content"),
                    }
                )

        return self.env["ir.sms.gateway"]._send(
            gateway_messages, handle_results=False, raise_exception=False
        )
