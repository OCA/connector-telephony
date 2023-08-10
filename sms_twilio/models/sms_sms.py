# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SmsSms(models.Model):
    _inherit = "sms.sms"

    error_detail = fields.Text(readonly=True)

    def _split_batch(self):
        if self.env["sms.api"]._get_twilio_sms_account():
            # No batch with Twilio
            for record in self:
                yield [record.id]
        else:
            yield from super()._split_batch()
