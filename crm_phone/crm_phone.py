# -*- encoding: utf-8 -*-
##############################################################################
#
#    CRM phone module for Odoo/OpenERP
#    Copyright (c) 2012-2014 Akretion (http://www.akretion.com)
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

from openerp import models, fields, api, _


class CrmLead(models.Model):
    _name = 'crm.lead'
    _inherit = ['crm.lead', 'phone.common']
    _phone_fields = ['phone', 'mobile', 'fax']
    _phone_name_sequence = 20
    _country_field = 'country_id'
    _partner_field = None

    def create(self, vals):
        vals_reformated = self._generic_reformat_phonenumbers(None, vals)
        return super(CrmLead, self).create(vals_reformated)

    def write(self, ids, vals):
        vals_reformated = self._generic_reformat_phonenumbers(
            ids, vals)
        return super(CrmLead, self).write(ids, vals_reformated)

    def name_get(self, ids):
        if self.env.context.get('callerid'):
            res = []
            if isinstance(ids, (int, long)):
                ids = [ids]
            for lead in self.browse(ids):
                if lead.partner_name and lead.contact_name:
                    name = u'%s (%s)' % (lead.contact_name, lead.partner_name)
                elif lead.partner_name:
                    name = lead.partner_name
                elif lead.contact_name:
                    name = lead.contact_name
                else:
                    name = lead.name
                res.append((lead.id, name))
            return res
        else:
            return super(CrmLead, self).name_get(ids)


'''class CrmPhonecall(models.Model):
    _name = 'crm.phonecall'
    _inherit = ['crm.phonecall', 'phone.common']
    _phone_fields = ['partner_phone', 'partner_mobile']
    _country_field = None
    _partner_field = 'partner_id'

    def create(self, vals):
        vals_reformated = self._generic_reformat_phonenumbers(
            None, vals)
        return super(CrmPhonecall, self).create(
            vals_reformated)

    def write(self, ids, vals):
        vals_reformated = self._generic_reformat_phonenumbers(
            ids, vals)
        return super(CrmPhonecall, self).write(
            ids, vals_reformated)
'''

class ResUsers(models.Model):
    _inherit = "res.users"

    # Field name starts with 'context_' to allow modification by the user
    # in his preferences, cf server/openerp/addons/base/res/res_users.py
    # in "def write()" of "class res_users(osv.osv)"
    context_propose_creation_crm_call = fields.Boolean(
        string='Propose to create a call in CRM after a click2dial',
        default=True)


class PhoneCommon(models.AbstractModel):
    _inherit = 'phone.common'

    @api.model
    def click2dial(self, erp_number):
        res = super(PhoneCommon, self).click2dial(erp_number)
        if (
                self.env.user.context_propose_creation_crm_call and
                self.env.context.get('click2dial_model')
                in ('res.partner', 'crm.lead')):
            res.update({
                'action_name': _('Create Call in CRM'),
                'action_model': 'wizard.create.crm.phonecall',
                })
        return res
