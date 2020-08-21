# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
# Copyright (C) 2015 Valentin Chemiere <valentin.chemiere@akretion.com>
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

from odoo.tools import pycompat


class SmsTemplate(models.Model):

    _name = 'sms.template'
    _inherit = ["mail.template", "sms.abstract"]
    _description = 'Sms Template'

    mobile = fields.Char(required=True)
    message = fields.Text(translate=True)

    @api.multi
    def generate_sms(self, res_ids, fields=None):
        self.ensure_one()
        if isinstance(res_ids, pycompat.integer_types):
            res_ids = [res_ids]
        if fields is None:
            fields = ['message', 'mobile', 'partner_to']

        res_ids_to_templates = self.get_email_template(res_ids)

        # templates: res_id -> template; template -> res_ids
        templates_to_res_ids = {}
        for res_id, template in res_ids_to_templates.items():
            templates_to_res_ids.setdefault(template, []).append(res_id)

        results = dict()
        template_model = self.env['sms.template']

        for template, template_res_ids in templates_to_res_ids.items():
            generated_lang = {}
            if template.lang:
                generated_lang = template_model._render_template(
                    getattr(template, 'lang'), template.model, template_res_ids
                )
            for template_res_id in template_res_ids:
                lang = generated_lang.get(
                    template_res_id, template._context.get('lang')
                )
                template_model = template_model.with_context(lang=lang)
                for field in fields:
                    generated_field_values = template_model._render_template(
                        getattr(template.with_context(lang=lang), field),
                        template.model,
                        [template_res_id],
                        post_process=(field == 'message'),
                    )
                    for res_id, field_value in generated_field_values.items():
                        results.setdefault(res_id, dict())[field] = field_value
            # compute recipients
            if any(field in fields for field in ['mobile', 'partner_to']):
                results = template.generate_recipients(
                    results, template_res_ids
                )
            # update values for all res_ids
            for res_id in template_res_ids:
                values = results[res_id]
                partner_ids = values['partner_ids']
                partner_id = (
                    partner_ids[0]
                    if partner_ids and isinstance(partner_ids, list)
                    else False
                )
                values.update(
                    gateway_id=template.gateway_id.id or False,
                    auto_delete=template.auto_delete,
                    partner_id=partner_id,
                    # mail.message values
                    body=values['message'],
                    partner_ids=[(6, 0, partner_ids)],
                    needaction_partner_ids=[(6, 0, partner_ids)],
                    model=template.model,
                    res_id=res_id or False,
                    message_type='sms',
                )

        return results

    @api.multi
    def send_sms(
        self, res_id, force_send=False, raise_exception=False, sms_values=None
    ):
        self.ensure_one()
        generated_sms = self.generate_sms(res_id)
        sms = self.env['sms.sms'].create(list(generated_sms.values()))
        if force_send:
            sms.send(raise_exception=raise_exception)
        return sms.ids

    @api.multi
    def create_action(self):
        act_window_model = self.env['ir.actions.act_window']
        view = self.env.ref('base_sms_client.sms_compose_message_form_view')
        for template in self:
            button_name = _('Send SMS (%s)') % template.name
            action = act_window_model.create(
                {
                    'name': button_name,
                    'type': 'ir.actions.act_window',
                    'res_model': 'sms.compose.message',
                    'src_model': template.model_id.model,
                    'view_type': 'form',
                    'context': "{'default_template_id' : %d, "
                    "'default_use_template': True}" % (template.id),
                    'view_mode': 'form,tree',
                    'view_id': view.id,
                    'target': 'new',
                    'binding_model_id': template.model_id.id,
                }
            )
            template.write({'ref_ir_act_window': action.id})
        return True
