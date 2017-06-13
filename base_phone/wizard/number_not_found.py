# -*- coding: utf-8 -*-
# © 2010-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
try:
    import phonenumbers
except (ImportError, IOError) as err:
    _logger.debug(err)


class NumberNotFound(models.TransientModel):
    _name = "number.not.found"
    _description = "Number not found"

    calling_number = fields.Char(string='Calling Number', size=64,
                                 readonly=True,
                                 help="Phone number of calling party that has "
                                 "been obtained from the telephony server, in "
                                 "the format used by the telephony server "
                                 "(not E.164).")
    e164_number = fields.Char(string='E.164 Number', size=64,
                              help="E.164 equivalent of the calling number.")
    number_type = fields.Selection(selection=[
        ('phone', 'Fixed'),
        ('mobile', 'Mobile')
    ], string='Fixed/Mobile', required=True)
    to_update_partner_id = fields.Many2one(comodel_name='res.partner',
                                           string='Partner to Update',
                                           help="Partner on which the phone "
                                           "number will be written")
    current_partner_phone = fields.Char(related='to_update_partner_id.phone',
                                        string='Current Phone', readonly=True)
    current_partner_mobile = fields.Char(related='to_update_partner_id.mobile',
                                         string='Current Mobile',
                                         readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super(NumberNotFound, self).default_get(fields_list)
        if not res:
            res = {}
        if res.get('calling_number'):
            if not self.env.user.company_id.country_id:
                raise UserError(_(
                    'Missing country on company %s'
                    % self.env.user.company_id.name))
            country_code = self.env.user.company_id.country_id.code
            try:
                parsed_num = phonenumbers.parse(
                    res['calling_number'], country_code)
                res['e164_number'] = phonenumbers.format_number(
                    parsed_num, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                number_type = phonenumbers.number_type(parsed_num)
                if number_type == 1:
                    res['number_type'] = 'mobile'
                else:
                    res['number_type'] = 'phone'
            except Exception, e:
                _logger.error(
                    "Cannot reformat the phone number '%s': %s",
                    res['calling_number'], e)
                pass
        return res

    @api.multi
    def create_partner(self):
        '''Function called by the related button of the wizard'''
        wiz = self[0]
        parsed_num = phonenumbers.parse(wiz.e164_number, None)
        phonenumbers.number_type(parsed_num)

        context = dict(self._context or {})
        context.update({'default_%s' % wiz.number_type: wiz.e164_number})
        action = {
            'name': _('Create New Partner'),
            'view_mode': 'form,tree,kanban',
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            'nodestroy': False,
            'target': 'current',
            'context': context,
        }
        return action

    @api.multi
    def update_partner(self):
        self.ensure_one()
        wiz = self[0]
        if not wiz.to_update_partner_id:
            raise UserError(_('Select the Partner to Update.'))
        wiz.to_update_partner_id.write(
            {wiz.number_type: wiz.e164_number})
        action = {
            'name': _('Partner: %s' % wiz.to_update_partner_id.name),
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'form,tree,kanban',
            'nodestroy': False,
            'target': 'current',
            'res_id': wiz.to_update_partner_id.id,
            'context': self._context,
        }
        return action
