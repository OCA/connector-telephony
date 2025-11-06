# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

import logging

from odoo import _, api, exceptions, fields, models

_logger = logging.getLogger(__name__)


class IrSmsGateway(models.Model):
    _name = "ir.sms.gateway"
    _order = "sequence"
    _description = "SMS gateway provider"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    gateway_type = fields.Selection([("iap", "Odoo IAP")], string="Type", required=True)
    sequence = fields.Integer(default=lambda self: self._default_sequence())
    prefix = fields.Char(
        help="Fill in for which phone number prefix(es) this provider is used, ie "
        "'+31' to use it for NL, '+31 +49' to use it for DE and NL, or '+3120' to use "
        "it for Amsterdam/NL. Leave empty to send to any number.",
    )
    description = fields.Html(compute="_compute_description")
    company_id = fields.Many2one("res.company")

    def _default_sequence(self):
        return (
            max(list(filter(None, self.sudo().search([]).mapped("sequence"))) or [0])
            + 1
        )

    @api.depends("gateway_type")
    def _compute_description(self):
        """
        Call a provider specific function _get_description_$gateway_type if defined
        to show a description/help text on the gateway form
        """
        for this in self:
            this.description = getattr(
                this, f"_get_description_{this.gateway_type}", lambda: False
            )()

    # SMS sending functions

    def _send_via_self(self, sms_records):
        """
        Send SMS records via the current provider

        Return list of dictionaries [{
            'uuid': sms.sms uuid,
            'state': sms state,
            'failure_reason': optional failure reason
        }]
        """
        self.ensure_one()
        # Convert sms records to message format for compatibility
        messages = [
            {
                "id": sms.id,
                "uuid": sms.uuid,
                "number": sms.number,
                "content": sms.body,
            }
            for sms in sms_records
        ]

        result = getattr(self, f"_send_{self.gateway_type}")(messages) or []
        return [dict(result_dict, sms_gateway_id=self.id) for result_dict in result]

    @api.model
    def _send_sms_batch(self, sms_records):
        """
        Send SMS records using appropriate gateways

        sms_records: sms.sms records to send

        Returns list of dictionaries [{
            'uuid': sms.sms uuid,
            'state': sms state,
            'failure_reason': optional failure reason,
            'sms_gateway_id': ir.sms.gateway id
        }]
        """
        # First ensure all SMS have gateways assigned
        sms_records._assign_gateways()

        # Convert to message format for existing logic
        messages = [
            {
                "id": sms.id,
                "uuid": sms.uuid,
                "number": sms.number,
                "content": sms.body,
            }
            for sms in sms_records
        ]

        return self._send(messages, handle_results=False, raise_exception=False)

    @api.model
    def _send(self, messages, handle_results=True, raise_exception=True):
        """
        Use the already-assigned gateways for each SMS
        """
        SmsSms = self.env["sms.sms"]
        result = []

        # Group by assigned gateway
        gateway_groups = {}
        for message in messages:
            sms_id = message.get("id")
            sms = SmsSms.browse(sms_id)
            if sms.exists():
                gateway = sms.sms_gateway_id
                gateway_groups.setdefault(gateway, []).append(message)

        # Process each gateway
        for gateway, messages_to_send in gateway_groups.items():
            if not gateway:
                if raise_exception:
                    raise exceptions.UserError(
                        _("No gateway assigned for messages %s") % messages_to_send
                    )
                continue

            sms_records = SmsSms.browse([msg["id"] for msg in messages_to_send])
            provider_result = gateway._send_via_self(sms_records) or []

            if handle_results:
                gateway._handle_results(messages_to_send, provider_result)
            result.extend(provider_result)

        return result

    @api.model
    def _send_get_providers(self, messages):
        """
        Return all providers potentially suitable for the current context
        """
        providers = self.search(
            [
                ("active", "=", True),
                "|",
                ("company_id", "=", False),
                ("company_id", "=", self.env.company.id),
            ]
        )
        _logger.info(
            "_send_get_providers found: %s",
            [(p.id, p.name, p.gateway_type, p.active) for p in providers],
        )
        return providers

    def _send_partition_providers(self, messages):
        """
        Return a dict with providers in self as keys and lists of messages a provider
        will handle as value
        """
        result = {}
        remaining_messages = messages[:]

        # Sort providers by sequence (priority)
        sorted_providers = self.sorted(key=lambda p: p.sequence)
        _logger.info(
            "Sorted providers by sequence: %s",
            [(p.name, p.sequence) for p in sorted_providers],
        )

        while remaining_messages:
            message = remaining_messages.pop()
            assigned = False
            for provider in sorted_providers:
                can_send = provider._can_send(message)
                _logger.info(
                    "Provider %s can send to %s: %s",
                    provider.name,
                    message.get("number"),
                    can_send,
                )
                if can_send:
                    result.setdefault(provider, []).append(message)
                    assigned = True
                    _logger.info(
                        "Assigned message %s to provider %s",
                        message.get("id"),
                        provider.name,
                    )
                    break
            if not assigned:
                result.setdefault(self.browse([]), []).append(message)
                _logger.info("No provider found for message %s", message.get("id"))
        return result

    def _can_send(self, message):
        """
        Determine if the provider can send a message
        """
        self.ensure_one()
        if not self.prefix:
            return True
        number = message.get("number", "")
        return any(number.startswith(prefix.strip()) for prefix in self.prefix.split())

    def _handle_results(self, messages, results, unlink_failed=False, unlink_sent=True):
        """
        Write state of sms.sms objects based on results.
        """
        self.ensure_one()
        SmsSms = self.env["sms.sms"]

        # Group results by UUID for processing
        results_by_uuid = {result.get("uuid"): result for result in results}

        # Process each message
        for message in messages:
            sms_uuid = message.get("uuid")
            result = results_by_uuid.get(sms_uuid, {})

            if not result:
                continue

            # Find SMS record by UUID
            sms = SmsSms.search([("uuid", "=", sms_uuid)], limit=1)
            if not sms:
                continue

            # Update SMS state based on result
            state = result.get("state", "error")
            # Remove the unused failure_reason variable
            # failure_reason = result.get('failure_reason')

            if state == "success":
                sms.write({"state": "sent", "failure_type": False})
            else:
                # Map failure types appropriately
                failure_type = "sms_server"  # Default failure type
                sms.write({"state": "error", "failure_type": failure_type})

            # Update notifications
            self.env["mail.notification"].sudo().search(
                [
                    ("notification_type", "=", "sms"),
                    ("sms_id", "=", sms.id),
                    ("notification_status", "not in", ("sent", "canceled")),
                ]
            ).write(
                {
                    "notification_status": "sent"
                    if state == "success"
                    else "exception",
                    "failure_type": sms.failure_type,
                }
            )

    # implementation of the iap (odoo native) provider
    def _get_description_iap(self):
        return _(
            "Make sure you've configured an SMS provider in the IAP settings for "
            "this to work"
        )

    def _send_iap(self, messages):
        """
        Send messages using the IAP provider through the new SmsApi class.
        """
        # Use context to force IAP and bypass our custom SmsApi
        sms_api_class = self.env.company._get_sms_api_class()
        sms_api = sms_api_class(self.env)  # Correct syntax

        # Convert messages to IAP format
        iap_messages = []
        for message in messages:
            iap_messages.append(
                {
                    "content": message["content"],
                    "numbers": [
                        {"number": message["number"], "uuid": message.get("uuid", "")}
                    ],
                }
            )

        delivery_reports_url = (
            self.env["ir.config_parameter"].sudo().get_param("web.base.url")
            + "/sms/status"
        )

        try:
            # Apply force_iap context when calling the batch method
            results = sms_api.with_context(force_iap=True)._send_sms_batch(
                iap_messages, delivery_reports_url=delivery_reports_url
            )

            # Convert IAP results to our format
            formatted_results = []
            for result in results:
                formatted_results.append(
                    {
                        "uuid": result.get("uuid"),
                        "state": result.get("state", "server_error"),
                        "failure_reason": result.get("failure_reason"),
                    }
                )
            return formatted_results

        except Exception as e:
            # Return error results for all messages
            return [
                {
                    "uuid": message.get("uuid"),
                    "state": "server_error",
                    "failure_reason": str(e),
                }
                for message in messages
            ]
