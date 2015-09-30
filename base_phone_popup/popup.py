# -*- coding: utf-8 -*-
##############################################################################
#
#    Base Phone Pop-up module for Odoo/OpenERP
#    Copyright (C) 2014 Alexis de Lattre <alexis@via.ecp.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp import models, fields, api, _
import logging


logger = logging.getLogger(__name__)


class PhoneCommon(models.AbstractModel):
    _inherit = 'phone.common'

    def _prepare_incall_pop_action(self, record_res, number):
        action = False
        if record_res:
            obj = self.env[record_res[0]]
            action = {
                'name': obj._description,
                'type': 'ir.actions.act_window',
                'res_model': record_res[0],
                'view_mode': 'form,tree',
                'views': [[False, 'form']],  # Beurk, but needed
                'target': 'new',
                'res_id': record_res[1],
                'flags': {'form': {'action_buttons': True}} ,
                }
        else:
            data_obj = self.env['ir.model.data']
            obj, form_view_id = data_obj.get_object_reference('base_phone_popup', 'view_res_partner_notfoundpopup')
            import phonenumbers
            from phonenumbers import geocoder
            query = phonenumbers.parse("+27823374587", None)
            x = query.country_code
            print x
            region = geocoder.description_for_number(query, "en")
            action = {
                'name': _('Number %s (%s) Not Found' % (number, region) ),
                'type': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'view_mode': 'form',
                'views': [[form_view_id, 'form']],
                'target': 'new',
                'context': {'default_phone': number}
            }
            '''action = {
                'name': _('Number Not Found'),
                'type': 'ir.actions.act_window',
                'res_model': 'number.not.found',
                'view_mode': 'form',
                'views': [[False, 'form']],  # Beurk, but needed
                'target': 'new',
                'context': {'default_calling_number': number}
            }'''
        return action

    @api.model
    def incall_notify_by_login(self, params):
        print params
        number = params['number']
        login_list = params['login_list']
        login_list = set(login_list) #make unique
        login_list = list(login_list)
        print login_list

        assert isinstance(login_list, list), 'login_list must be a list'


        blinking_action = {
            "type": "ir.actions.client",
            "tag": "popup.homepage"
        }

        res = self.get_record_from_phone_number(number)
        users = self.env['res.users'].search([('login', 'in', login_list)]) #.filtered(lambda u: u.login in login_list) #search([('login', 'in', login_list)])
        logger.debug(
            'Notify incoming call from number %s to users %s'
            % (number, users))
        action = self._prepare_incall_pop_action(res, number)
        print action
        if action:
            for user in users:
                if user['context_incall_popup']:
                    self.env.uid = user['id']
                    self.env['action.request'].notify(blinking_action)
                    self.env['action.request'].notify(action)
                    logger.debug(
                        'This action has been sent to user ID %d: %s'
                        % (user['id'], action))
        if res:
            callerid = res[2]
        else:
            callerid = False
        return callerid


class ResUsers(models.Model):
    _inherit = 'res.users'

    context_incall_popup =  fields.Boolean('Pop-up on Incoming Calls', default=True)
