# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SmsComposeMessage(models.TransientModel):

    _name = 'sms.compose.message'
    _description = 'Sms Compose Message'

    model = fields.Char(required=True)
    res_id = fields.Integer(required=True)
    gateway_id = fields.Many2one(
        comodel_name='sms.gateway', string='SMS Gateway'
    )
    mobile = fields.Char(required=True)
    partner_id = fields.Many2one(comodel_name='res.partner')
    message = fields.Text(size=256, required=True, translate=False)
    template_id = fields.Many2one(
        comodel_name='sms.template',
        string='Use Template',
        domain="[('model', '=', model)]",
    )

    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)
        result['model'] = result.get(
            'model', self._context.get('active_model')
        )
        result['res_id'] = result.get('res_id', self._context.get('active_id'))
        if result['model'] == 'res.users' and result['res_id'] == self._uid:
            result['model'] = 'res.partner'
            result['res_id'] = self.env.user.partner_id.id
        return result

    @api.onchange('template_id')
    def _onchange_template_id(self):
        mail_values = self.template_id.generate_sms(self.res_id)
        partner_ids = mail_values.get(self.res_id).get('partner_ids', False)
        self.partner_id = partner_ids and partner_ids[0]
        self.mobile = mail_values.get(self.res_id).get('mobile', False)
        self.message = mail_values.get(self.res_id).get('message', False)
        self.gateway_id = mail_values.get(self.res_id).get('gateway_id', False)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.mobile = self.partner_id.mobile

    @api.multi
    def _prepare_sms_vals(self):
        self.ensure_one()
        return {
            'gateway_id': self.gateway_id.id,
            'state': 'draft',
            'message': self.message,
            'partner_id': self.partner_id.id,
            'mobile': self.mobile,
            'company_id': self.env.user.company_id.id,
            # mail.message values
            'body': self.message,
            'partner_ids': [(6, 0, self.partner_id.ids)],
            'needaction_partner_ids': [(6, 0, self.partner_id.ids)],
            'model': self.model,
            'res_id': self.res_id,
            'message_type': 'sms',
        }

    @api.multi
    def send_sms(self):
        sms_model = self.env['sms.sms']
        for wizard in self:
            sms_model.create(wizard._prepare_sms_vals())
        return True
