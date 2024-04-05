from odoo import _, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_phone = fields.Char("Phone", related="partner_id.phone")
    partner_mobile = fields.Char("Mobile", related="partner_id.mobile")
    invoice_phone = fields.Char("Phone", related="partner_invoice_id.phone")
    invoice_mobile = fields.Char("Mobile", related="partner_invoice_id.mobile")
    delivery_phone = fields.Char("Phone", related="partner_shipping_id.phone")
    delivery_mobile = fields.Char("Mobile", related="partner_shipping_id.mobile")

    def action_test_sticky(self):
        action = {
            "name": _("Partner"),
            "type": "ir.actions.act_window",
            "res_model": "phone.common",
            "view_mode": "tree,kanban",
            "target": "current",
        }

        return action

    def cloudcti_open_outgoing_notification(self):
        called_id = self._context.get("call_no")
        caller_id = self.env.user.phone
        if caller_id and called_id and caller_id != called_id:
            self.partner_id.cloudcti_outgoing_call_notification()
