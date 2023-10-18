from odoo import models


class SmsSms(models.Model):
    _inherit = "sms.sms"

    def _split_batch(self):
        if self.env["sms.api"]._is_sent_with_global_digital():
            # No batch with Global Digital
            for record in self:
                yield [record.id]
        else:
            yield from super()._split_batch()
