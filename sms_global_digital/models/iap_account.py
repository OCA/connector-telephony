from odoo import fields, models


class IapAccount(models.Model):
    _inherit = "iap.account"

    provider = fields.Selection(
        selection_add=[("sms_global_digital", "SMS Global digital")],
        ondelete={"sms_global_digital": "cascade"},
    )

    sms_global_digital_sender_id = fields.Char(string="Sender ID")
    sms_global_digital_api_key = fields.Char(string="Api Key")

    def _get_service_from_provider(self):
        if self.provider == "sms_global_digital":
            return "sms"
        return super()._get_service_from_provider()

    @property
    def _server_env_fields(self):
        res = super()._server_env_fields
        res.update(
            {
                "sms_global_digital_sender_id": {},
                "sms_global_digital_api_key": {},
            }
        )
        return res
