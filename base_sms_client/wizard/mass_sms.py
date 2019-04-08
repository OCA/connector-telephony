# coding: utf-8
# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
# Copyright (C) 2015 Valentin Chemiere <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class WizardMassSms(models.TransientModel):
    _name = 'wizard.mass.sms'

    @api.model
    def _default_get_gateway(self):
        return self.env['sms.gateway'].search([], limit=1).id

    @api.model
    def _default_get_partner(self):
        if self._context.get('active_model') == 'res.partner':
            return self._context.get('active_ids')
        else:
            rec = self.env[self._context.get('active_model')].browse(
                self._context.get('active_id'))
            if hasattr(rec, 'message_follower_ids'):
                rec.message_follower_ids.mapped('partner_id')

    gateway_id = fields.Many2one(
        'sms.gateway',
        required=True,
        default=_default_get_gateway)
    message = fields.Text(required=True)
    validity = fields.Integer(
        help='The maximum time -in minute(s)- before the message is dropped')
    classes = fields.Selection([
        ('0', 'Flash'),
        ('1', 'Phone display'),
        ('2', 'SIM'),
        ('3', 'Toolkit'),
    ], help='The sms class: flash(0),phone display(1),SIM(2),toolkit(3)')
    deferred = fields.Integer(
        help='The time -in minute(s)- to wait before sending the message')
    priority = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3')
    ], help='The priority of the message')
    coding = fields.Selection([
        ('1', '7 bit'),
        ('2', 'Unicode')
        ], help='The sms coding: 1 for 7 bit or 2 for unicode')
    tag = fields.Char(size=256, help='An optional tag')
    nostop = fields.Boolean(
        help='Do not display STOP clause in the message, this requires that '
             'this is not an advertising message')
    partner_ids = fields.Many2many('res.partner', default=_default_get_partner)

    @api.onchange('gateway_id')
    def onchange_gateway_mass(self):
        for key in ['validity', 'classes', 'deferred', 'priority',
                    'coding', 'tag', 'nostop']:
            self[key] = self.gateway_id[key]

    @api.model
    def _prepare_sms_vals(self, partner):
        return {
            'gateway_id': self.gateway_id.id,
            'state': 'draft',
            'message': self.message,
            'validity': self.validity,
            'classes': self.classes,
            'deferred': self.deferred,
            'priority': self.priority,
            'coding': self.coding,
            'tag': self.tag,
            'nostop': self.nostop,
            'partner_id': partner.id,
            'mobile': partner.mobile,
        }

    @api.multi
    def send(self):
        sms_obj = self.env['sms.sms']
        for partner in self.partner_ids:
            vals = self._prepare_sms_vals(partner)
            sms_obj.create(vals)
        src_model = self.env[self._context.get('active_model')]
        if hasattr(src_model, 'message_follower_ids'):
            rec = src_model.browse(self._context.get('active_id'))
            rec.message_post(body=self.message)
            self.env['bus.bus'].sendone(
                'refresh', [self.env.cr.dbname, self._name, self._uid])
        return {'type': 'ir.actions.act_window_close'}

    def redirect_to_sms_wizard(self, **kwargs):
        id = kwargs.get("id")
        model = kwargs.get("model")
        action = self.env['wizard.mass.sms'].action_wizard_mass_sms()
        action['src_model'] = model
        action['domain'] = [('res_id', '=', id)]
        return action

    @api.model
    def action_wizard_mass_sms(self):
        action = self.env.ref(
            'base_sms_client.action_wizard_mass_sms').read()[0]
        return action
