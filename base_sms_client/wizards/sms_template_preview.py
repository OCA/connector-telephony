# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SmsTemplatePreview(models.TransientModel):

    _name = "sms_template.preview"
    _inherit = ["email_template.preview", "sms.template"]
    _description = "SMS Template Preview Wizard"

    partner_id = fields.Many2one(
        comodel_name="res.partner", string="partner", readonly=True
    )

    @api.onchange('res_id')
    def on_change_res_id(self):
        if not self.res_id:
            return {}
        mail_values = {}
        if self._context.get('template_id'):
            template = self.env['sms.template'].browse(
                self._context['template_id']
            )
            self.name = template.name
            mail_values = template.generate_sms(self.res_id)
        partner_ids = mail_values.get(self.res_id).get('partner_ids', False)
        self.partner_id = partner_ids and partner_ids[0]
        self.mobile = mail_values.get(self.res_id).get('mobile', False)
        self.message = mail_values.get(self.res_id).get('message', False)

    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)
        if self._context.get('template_id'):
            result['model_id'] = (
                self.env['sms.template']
                .browse(self._context['template_id'])
                .model_id.id
            )
        return result
