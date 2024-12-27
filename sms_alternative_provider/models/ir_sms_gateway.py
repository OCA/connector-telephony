# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import _, api, exceptions, fields, models


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
                this, "_get_description_%s" % this.gateway_type, lambda: False
            )()

    # SMS sending functions

    def _send_via_self(self, messages):
        """
        Send a list of SMS via the current provider

        Return list of dictionaries [{
            'id': sms.sms id,
            'state': sms.sms#state,
            'failure_type': sms.sms#failure_type
        }]
        """
        self.ensure_one()
        result = getattr(self, "_send_%s" % self.gateway_type)(messages) or []
        return [dict(result_dict, sms_gateway_id=self.id) for result_dict in result]

    @api.model
    def _send(self, messages, handle_results=True, raise_exception=True):
        """
        Select provider(s) based on messages, call their provider specific function
        _send_$gateway_type to actually send SMS

        messages is a list of dictionaries [{
            'id': sms.sms id,
            'number': phone number,
            'content': sms content,
        }]

        Returns list of dictionaries [{
            'id': sms.sms id,
            'state': sms.sms#state,
            'failure_type': sms.sms#failure_type,
            'sms_gateway_id': ir.sms.gateway id
        }]
        """
        SmsSms = self.env["sms.sms"]
        result = []
        providers = self._send_get_providers(messages)
        provider2messages = providers._send_partition_providers(messages)
        for provider, messages_to_send in provider2messages.items():
            if not provider and raise_exception:
                raise exceptions.UserError(
                    _("No suitable provider found for messages %s") % messages_to_send
                )
            provider_result = provider._send_via_self(messages_to_send) or []
            sms = SmsSms.browse(
                filter(None, map(lambda x: x.get("id"), provider_result))
            )
            sms.write({"sms_gateway_id": provider.id})
            if handle_results:
                provider._handle_results(messages_to_send, provider_result)
            result.extend(provider_result)
        return result

    @api.model
    def _send_get_providers(self, messages):
        """
        Return all providers potentially suitable for the current context
        """
        return self.search(
            ["|", ("company_id", "=", False), ("company_id", "=", self.env.company.id)]
        )

    def _send_partition_providers(self, messages):
        """
        Return a dict with providers in self as keys and lists of messages a provider
        will handle as value
        ie
        {
            ir.gateway.record(42,): [{message1}, {message2}],
            ir.gateway.record(43,): [{message3}],
            ir.gateway.record(44,): [],
            ir.gateway.record(): [{messages not handled by any available provider}],
        }
        """
        result = {}
        remaining_messages = messages[:]
        while remaining_messages:
            message = remaining_messages.pop()
            for this in self:
                if this._can_send(message):
                    result.setdefault(this, []).append(message)
                    break
            else:
                result.setdefault(self.browse([]), []).append(message)
        return result

    def _can_send(self, message):
        """
        Determine if the provider can send a message
        """
        self.ensure_one()
        if not self.prefix:
            return True
        return any(
            (message.get("number") or "").startswith(prefix)
            for prefix in self.prefix.split()
        )

    def _handle_results(self, messages, results, unlink_failed=False, unlink_sent=True):
        """
        Write state of sms.sms objects based on results.

        messages is the list of messages passed to _send
        results is the list of results (provider-specific) as returned by _send
        """
        self.ensure_one()
        SmsSms = self.env["sms.sms"]
        to_unlink = SmsSms.browse([])
        for result in results:
            data = {
                key: value
                for key, value in result.items()
                if key in SmsSms._fields and key not in ("id", "sms_gateway_id")
            }
            if not data:
                continue
            sms = SmsSms.browse(result.get("id", []))
            if not sms:
                continue
            sms.write(data)
            if sms.state == "error" and unlink_failed:
                to_unlink += sms
            if sms.state == "sent" and unlink_sent:
                to_unlink += sms
            self.env["mail.notification"].sudo().search(
                [
                    ("notification_type", "=", "sms"),
                    ("sms_id", "=", sms.id),
                    ("notification_status", "not in", ("sent", "canceled")),
                ]
            ).write(
                {
                    "notification_status": "sent"
                    if sms.state == "sent"
                    else "exception",
                    "failure_type": sms.failure_type,
                }
            )
        to_unlink.unlink()

    # implementation of the iap (odoo native) provider
    def _get_description_iap(self):
        return _(
            "Make sure you've configured an SMS provider in the IAP settings for "
            "this to work"
        )

    def _send_iap(self, messages):
        return [
            dict(result, id=result.get("res_id"))
            for result in self.env["sms.api"]
            .with_context(force_iap=True)
            ._send_sms_batch(
                [dict(message, res_id=message.get("id")) for message in messages]
            )
        ]
