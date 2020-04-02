# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SmsTemplatePreview(models.TransientModel):

    _name = "sms_template.preview"
    _inherit = ["email_template.preview", "sms.template"]
    _description = "SMS Template Preview Wizard"

    @api.onchange('res_id')
    @api.multi
    def on_change_res_id(self):
        if not self.res_id:
            return {}
        mail_values = {}
        if self._context.get('template_id'):
            template = self.env['sms.template'].browse(
                self._context['template_id'])
            self.name = template.name
            mail_values = template.generate_sms(self.res_id)
        for field in ['mobile', 'message', 'partner_ids']:
            setattr(self, field, mail_values.get(field, False))
