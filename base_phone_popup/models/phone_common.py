# Copyright 2014-2016 Akretion, Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
import logging


_logger = logging.getLogger(__name__)


class PhoneCommon(models.AbstractModel):
    _inherit = 'phone.validation.mixin'

    @api.model
    def get_record_from_phone_number(self, presented_number):
        """If it finds something, it returns (object name, ID, record name)
        For example : ('res.partner', 42, u'Alexis de Lattre (Akretion)')
        """
        _logger.debug(
            "Call get_name_from_phone_number with number = %s"
            % presented_number)
        if not presented_number.isdigit():
            _logger.warning(
                "Number '%s' should only contain digits." % presented_number)
        nr_digits_to_match_from_end = \
            self.env.user.company_id.number_of_digits_to_match_from_end
        if len(presented_number) >= nr_digits_to_match_from_end:
            end_number_to_match = presented_number[
                -nr_digits_to_match_from_end:len(presented_number)]
        else:
            end_number_to_match = presented_number
        sorted_phonemodels = self._get_phone_models()
        for obj_dict in sorted_phonemodels:
            obj = obj_dict['object']
            pg_search_number = str('%' + end_number_to_match)
            _logger.debug(
                "Will search phone and mobile numbers in %s ending with '%s'",
                obj._name, end_number_to_match)
            domain = []
            for field in obj_dict['fields']:
                domain.append((field, '=like', pg_search_number))
            if len(domain) > 1:
                domain = ['|'] * (len(domain) - 1) + domain
            _logger.debug('searching on %s with domain=%s', obj._name, domain)
            res_obj = obj.search(domain)
            if len(res_obj) > 1:
                _logger.warning(
                    "There are several %s (IDS = %s) with a phone number "
                    "ending with '%s'. Taking the first one.",
                    obj._name, res_obj.ids, end_number_to_match)
                res_obj = res_obj[0]
            if res_obj:
                name = res_obj.name_get()[0][1]
                res = (obj._name, res_obj.id, name)
                _logger.debug(
                    "Answer get_record_from_phone_number: (%s, %d, %s)",
                    res[0], res[1], res[2])
                return res
            else:
                _logger.debug(
                    "No match on %s for end of phone number '%s'",
                    obj._name, end_number_to_match)
        return False

    @api.model
    def _get_phone_models(self):
        # Hook to get models and fields on which search
        # You must inherit if you want to search into another fields
        res = [
            {'fields': ['phone', 'mobile'], 'object': self.env['res.partner']},
            {'fields': ['phone', 'mobile'], 'object': self.env['crm.lead']},
        ]
        return res

    @api.model
    def _prepare_incall_pop_action(self, record_res, number):
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
                }
        else:
            action = {
                'name': _('Number Not Found'),
                'type': 'ir.actions.act_window',
                'res_model': 'number.not.found',
                'view_mode': 'form',
                'views': [[False, 'form']],  # Beurk, but needed
                'target': 'new',
                'context': {'default_calling_number': number}
            }
        return action

    @api.model
    def incall_notify_by_login(self, number, login_list):
        assert isinstance(login_list, list), 'login_list must be a list'
        res = self.get_record_from_phone_number(number)
        users = self.env['res.users'].search(
            [('login', 'in', login_list)])
        _logger.debug(
            'Notify incoming call from number %s to users %s'
            % (number, users.ids))
        action = self._prepare_incall_pop_action(res, number)
        if action:
            for user in users:
                if user.context_incall_popup:
                    self.sudo(user.id).env['bus.bus'].sendone(
                        '%s_%d' % (self._name, self.env.uid), action)
                    _logger.debug(
                        'This action has been sent to user ID %d: %s'
                        % (user.id, action))
        if res:
            callerid = res[2]
        else:
            callerid = False
        return callerid
