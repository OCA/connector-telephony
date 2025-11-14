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
    def _send(self, sms_records, handle_results=True, raise_exception=True):
        """
        Send SMS records using their assigned gateways.
        sms_records: sms.sms recordset
        Returns list of dictionaries with keys:
          'uuid', 'state', 'failure_reason', 'sms_gateway_id'
        """
        self.ensure_one()  # if this is meant to be called on a gateway record
        SmsSms = self.env["sms.sms"]
        result = []

        if not sms_records:
            return result

        # Group SMS records by assigned gateway
        gateway_groups = {}
        for sms in sms_records:
            gateway = sms.sms_gateway_id
            gateway_groups.setdefault(gateway, SmsSms.browse([]))  # empty recordset
            gateway_groups[gateway] |= sms  # add sms to the recordset

        # Send messages per gateway
        for gateway, records_to_send in gateway_groups.items():
            if not gateway:
                if raise_exception:
                    raise exceptions.UserError(
                        _("No gateway assigned for messages %s")
                        % records_to_send.mapped("id")
                    )
                continue

            # Call the gateway's _send_via_self with the recordset
            provider_result = gateway._send_via_self(records_to_send) or []

            if handle_results:
                gateway._handle_results(records_to_send, provider_result)

            result.extend(provider_result)

        return result

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
            if state == "success":
                sms.write({"state": "sent", "failure_type": False})
            else:
                # Map failure types appropriately
                failure_type = "sms_server"
                sms.write({"state": "error", "failure_type": failure_type})
