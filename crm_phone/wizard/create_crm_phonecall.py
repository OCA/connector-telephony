# -*- coding: utf-8 -*-
# © 2012-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _
import phonenumbers


class WizardCreateCrmPhonecall(models.TransientModel):
    _name = "wizard.create.crm.phonecall"

    @api.multi
    def button_create_outgoing_phonecall(self):
        self.ensure_one()
        return self._create_open_crm_phonecall('outbound')

    @api.model
    def _create_open_crm_phonecall(self, direction='outbound'):
        teams = self.env['crm.team'].search(
            [('member_ids', 'in', self._uid)])
        action_ctx = self.env.context.copy()
        action_ctx.update({
            'default_direction': direction,
            'default_team_id': teams and teams[0].id or False,
        })
        domain = False
        if self.env.context.get('click2dial_model') == 'res.partner':
            partner_id = self.env.context.get('click2dial_id')
            action_ctx['default_partner_id'] = partner_id
            domain = [('partner_id', 'child_of', partner_id)]
        elif self.env.context.get('click2dial_model') == 'crm.lead':
            lead_id = self.env.context.get('click2dial_id')
            action_ctx['default_opportunity_id'] = lead_id
            domain = [('opportunity_id', '=', lead_id)]
        parsed_num = phonenumbers.parse(self.env.context.get('phone_number'))
        number_type = phonenumbers.number_type(parsed_num)
        if number_type == 1:
            action_ctx['default_partner_mobile'] =\
                self.env.context.get('phone_number')
        else:
            action_ctx['default_partner_phone'] =\
                self.env.context.get('phone_number')
        return {
            'name': _('Phone Call'),
            'type': 'ir.actions.act_window',
            'res_model': 'crm.phonecall',
            'domain': domain,
            'view_mode': 'form,tree,calendar',
            'nodestroy': False,  # close the pop-up wizard after action
            'target': 'current',
            'context': action_ctx,
        }
