# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SmsTemplatePreview(models.TransientModel):
    _name = "sms_template.preview"
    _description = "SMS Template Preview Wizard"

    partner_id = fields.Many2one(
        comodel_name="res.partner", string="Partner", readonly=True
    )
    model_id = fields.Many2one("ir.model", string="Model", readonly=True)
    res_id = fields.Integer("Resource ID")
    name = fields.Char()
    mobile = fields.Char()
    message = fields.Text()
    gateway_id = fields.Many2one(comodel_name="sms.gateway", string="SMS Gateway")

    @api.onchange("res_id")
    def on_change_res_id(self):
        if not self.res_id or not self._context.get("template_id"):
            return

        template = self.env["sms.template"].browse(self._context["template_id"])
        self.name = template.name

        mail_values = template.generate_sms(self.res_id)
        values = mail_values.get(self.res_id, {})

        partner_ids = values.get("partner_ids", [])
        self.partner_id = partner_ids and partner_ids[0]
        self.mobile = values.get("mobile", False)
        self.message = values.get("message", False)

    @api.model
    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        template_id = self._context.get("template_id")
        if template_id:
            template = self.env["sms.template"].browse(template_id)
            result["model_id"] = template.model_id.id
        return result
