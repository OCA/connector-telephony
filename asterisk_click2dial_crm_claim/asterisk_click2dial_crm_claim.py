# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk click2dial CRM module for OpenERP
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com)
#    Copyright (c) 2012-2013 Akretion (http://www.akretion.com)
#    Copyright (C) 2013 Invitu <contact@invitu.com>
#    @author: Jesús Martín <jmartin@zikzakmedia.com>
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

from openerp.addons.base_status.base_stage import base_stage
from openerp.osv import osv, fields
# Lib required to print logs
import logging
# Lib to translate error messages
from openerp.tools.translate import _
# Lib for phone number reformating -> pip install phonenumbers
import phonenumbers
# Lib py-asterisk from http://code.google.com/p/py-asterisk/
# We need a version which has this commit : http://code.google.com/p/py-asterisk/source/detail?r=8d0e1c941cce727c702582f3c9fcd49beb4eeaa4
# so a version after Nov 20th, 2012
from Asterisk import Manager

_logger = logging.getLogger(__name__)


class crm_claim(osv.osv):
    _name = 'crm.claim'
    _inherit = ['crm.claim', 'asterisk.common']


    def format_phonenumber_to_e164(self, cr, uid, ids, name, arg, context=None):
        return self.generic_phonenumber_to_e164(cr, uid, ids, [('partner_phone', 'partner_phone_e164')], context=context)


    _columns = {
        'partner_phone_e164': fields.function(format_phonenumber_to_e164, type='char', size=64, string='Phone in E.164 format', readonly=True, multi="e164claim", store={
            'crm.claim': (lambda self, cr, uid, ids, c={}: ids, ['partner_phone'], 10),
            }),
        }


    def create(self, cr, uid, vals, context=None):
        vals_reformated = self.generic_reformat_phonenumbers(cr, uid, vals, context=context)
        return super(crm_claim, self).create(cr, uid, vals_reformated, context=context)


    def write(self, cr, uid, ids, vals, context=None):
        vals_reformated = self.generic_reformat_phonenumbers(cr, uid, vals, context=context)
        return super(crm_claim, self).write(cr, uid, ids, vals_reformated, context=context)

