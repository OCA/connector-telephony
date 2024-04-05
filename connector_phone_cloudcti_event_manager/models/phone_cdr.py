from odoo import models


class PhoneCDR(models.Model):
    _inherit = "phone.cdr"

    def cloudcti_open_outgoing_notification(self):
        called_id = self._context.get("call_no")
        caller_id = self.env.user.phone
        if caller_id and called_id and caller_id != called_id:
            if self.partner_id:
                self.partner_id.cloudcti_outgoing_call_notification()
