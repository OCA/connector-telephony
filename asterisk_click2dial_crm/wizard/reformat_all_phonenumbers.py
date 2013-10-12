# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk click2dial CRM module for OpenERP
#    Copyright (c) 2013 Akretion (http://www.akretion.com)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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

from openerp.osv import orm


class reformat_all_phonenumbers(orm.TransientModel):
    _inherit = "reformat.all.phonenumbers"

    def _extend_reformat_phonenumbers(self, cr, uid, context=None):
        res = super(reformat_all_phonenumbers, self)._extend_reformat_phonenumbers(cr, uid, context=context)
        res[self.pool['crm.lead']] = {
            'allids': self.pool['crm.lead'].search(cr, uid, [], context=context),
            'phonefields': ['phone', 'fax', 'mobile'],
            'namefield': 'partner_name',
            }
        return res
