# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import api, fields, models


class SmsSms(models.Model):
    _inherit = "sms.sms"

    sms_gateway_id = fields.Many2one("ir.sms.gateway", string="SMS gateway used")

    @api.model_create_multi
    def create(self, vals_list):
        sms_list = super().create(vals_list)
        if self.env.context.get("sms_gateway_id"):
            sms_list.sms_gateway_id = self.env.context.get("sms_gateway_id")
        return sms_list

    def _split_by_api(self):
        """Overwrite to select the default SMS API configured in SMS Gateway."""
        if not self.sms_gateway_id:
            self.sms_gateway_id = self.env["ir.sms.gateway"]._get_default_gateway()
        sms_api = self.sms_gateway_id._get_api_class()
        yield sms_api(self.env, self.sms_gateway_id.iap_account_id), self
