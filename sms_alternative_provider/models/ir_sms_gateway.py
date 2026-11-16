# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from __future__ import annotations

from odoo import api, fields, models

from .sms_api import SmsApiBase


class IrSmsGateway(models.Model):
    _name = "ir.sms.gateway"
    _order = "sequence"
    _description = "SMS gateway provider"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    gateway_type = fields.Selection(
        selection=lambda self: self._compute_gateway_type(),
        string="Type",
        required=True,
    )
    sequence = fields.Integer(default=lambda self: self._default_sequence())
    prefix = fields.Char(
        help="Fill in for which phone number prefix(es) this provider is used, ie "
        "'+31' to use it for NL, '+31 +49' to use it for DE and NL, or '+3120' to use "
        "it for Amsterdam/NL. Leave empty to send to any number.",
    )
    description = fields.Html(compute="_compute_description")
    company_id = fields.Many2one("res.company")
    iap_account_id = fields.Many2one("iap.account")

    def _compute_gateway_type(self):
        return [(cls.KEY, cls.NAME) for cls in SmsApiBase.__subclasses__()]

    def _get_api_registry(self):
        return {cls.KEY: cls for cls in SmsApiBase.__subclasses__()}

    def _get_api_class(self):
        self.ensure_one()
        if not self.gateway_type:
            return SmsApiBase
        registry = self._get_api_registry()
        return registry[self.gateway_type]

    def _default_sequence(self):
        return (
            max(list(filter(None, self.sudo().search([]).mapped("sequence"))) or [0])
            + 1
        )

    @api.depends("gateway_type")
    def _compute_description(self):
        """
        Computes the description based on the value of the value DESCRIPTION
        from the class SmsApi linked to the selected gateway_type.
        """
        for this in self:
            this.description = this._get_api_class().DESCRIPTION

    def _get_valid_gateways(self) -> IrSmsGateway:
        return self.search(
            ["|", ("company_id", "=", False), ("company_id", "=", self.env.company.id)]
        )

    def _get_default_gateway(self) -> IrSmsGateway:
        gateways = self._get_valid_gateways().sorted("sequence")
        if len(gateways) < 1:
            raise NotImplementedError("No Sms Gateway configured")
        return gateways[0]
