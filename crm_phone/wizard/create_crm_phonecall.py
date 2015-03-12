# -*- encoding: utf-8 -*-
##############################################################################
#
#    CRM Phone module for Odoo
#    Copyright (c) 2012-2015 Akretion (http://www.akretion.com)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api, _
import phonenumbers


class wizard_create_crm_phonecall(models.TransientModel):
    _name = "wizard.create.crm.phonecall"

    @api.multi
    def button_create_outgoing_phonecall(self):
        self.ensure_one()
        return self._create_open_crm_phonecall(crm_categ='Outbound')

    @api.model
    def _create_open_crm_phonecall(self, crm_categ):
        categ = self.with_context(lang='en_US').env['crm.case.categ'].search(
            [('name', '=', crm_categ)])
        case_section = self.env['crm.case.section'].search(
            [('member_ids', 'in', self._uid)])
        action_ctx = self.env.context.copy()
        action_ctx.update({
            'default_categ_id': categ and categ[0].id or False,
            'default_section_id':
            case_section and case_section[0].id or False,
        })
        domain = False
        if self.env.context.get('click2dial_model') == 'res.partner':
            partner_id = self.env.context.get('click2dial_id')
            action_ctx['default_partner_id'] = partner_id
            domain = [('partner_id', '=', partner_id)]
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
            'domain': domain,
            'res_model': 'crm.phonecall',
            'view_mode': 'form,tree',
            'type': 'ir.actions.act_window',
            'nodestroy': False,  # close the pop-up wizard after action
            'target': 'current',
            'context': action_ctx,
        }
