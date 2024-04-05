from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    partner_phone = fields.Char("Phone", related="partner_id.phone")
    partner_mobile = fields.Char("Mobile", related="partner_id.mobile")

    def cloudcti_open_outgoing_notification(self):
        called_id = self._context.get("call_no")
        caller_id = self.env.user.phone
        if caller_id and called_id and caller_id != called_id:
            self.partner_id.cloudcti_outgoing_call_notification()
