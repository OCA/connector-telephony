# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk click2dial CRM module for OpenERP
#    Copyright (c) 2011 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#    Copyright (c) 2012 Akretion (http://www.akretion.com)
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

from osv import osv, fields
# Lib to translate error messages
from tools.translate import _


class res_users(osv.osv):
    _inherit = "res.users"

    _columns = {
        # Field name starts with 'context_' to allow modification by the user
        # in his preferences, cf server/openerp/addons/base/res/res_users.py
        # in "def write" of "class users"
        # This exists in since OpenERP 6.0 (it is not in OpenERP 5.0)
        'context_propose_creation_crm_call': fields.boolean('Propose to create a call in CRM after a click2dial'),
        }

    _defaults = {
        'context_propose_creation_crm_call': lambda *a: True,
        }

res_users()

