# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo import fields, models


class IrSmsGateway(models.Model):

    _inherit = "ir.sms.gateway"

    gateway_type = fields.Selection(
        selection_add=[("dummy", "Dummy")],
        ondelete={"dummy": "cascade"},
    )
    dummy_state = fields.Selection(
        lambda self: self.env["sms.sms"]._fields["state"].selection, "State"
    )
    dummy_result = fields.Text("Sent messages")

    def _send_dummy(self, messages):
        result = []
        dummy_result = self.dummy_result or ""
        for message in messages:
            dummy_result += "\n %s " % fields.Datetime.now() + message["content"]
            result.append(
                {
                    "id": message.get("id"),
                    "state": self.dummy_state,
                    "failure_type": "sms_server"
                    if self.dummy_state == "error"
                    else False,
                }
            )
        self.write({"dummy_result": dummy_result})
        return result
