# Copyright 2020 Akretion (https://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SmsSms(models.Model):
    _inherit = "sms.sms"

    error_detail = fields.Text(readonly=True)

    def _split_batch(self):
        if self.env["sms.api"]._is_sent_with_ovh():
            # No batch with OVH
            for record in self:
                yield [record.id]
        else:
            yield from super()._split_batch()
