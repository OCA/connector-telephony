# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk click2dial CRM module for OpenERP
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

from openerp import models, api, _


class PhoneCommon(models.AbstractModel):
    _inherit = 'phone.common'

    @api.model
    def click2dial(self, erp_number):
        '''
        Inherit the native click2dial function to trigger
        a wizard "Create Call in CRM" via the Javascript code
        of base_phone
        '''
        res = super(PhoneCommon, self).click2dial(erp_number)
        if (
                self.env.context.get('click2dial_model') in
                ('res.partner', 'crm.lead') and
                self.env.user.context_propose_creation_crm_call):
            res.update({
                'action_name': _('Create Call in CRM'),
                'action_model': 'wizard.create.crm.phonecall',
                })
        return res
