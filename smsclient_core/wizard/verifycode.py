##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>)
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

import wizard
import pooler
from openerp.osv import fields, orm
from openerp.tools.translate import _

form = '''<?xml version="1.0"?>
<form string="Verify Code">
    <field name="code" colspan="4"/>
</form>'''

fields = {
    'code': {'string': 'Verification Code', 'required': True, 'size': 255,
             'type': 'char', 'help': 'Enter the verification code that you get in your verification sms'}
}


class verifycode(orm.TransientModel):
    _name = 'sms.smsclient.code.verify'
    
    def checkcode(self, cr, uid, data, context):

        gate = pooler.get_pool(cr.dbname).get('sms.smsclient').browse(cr, uid, data['id'], context)
        if gate.state == 'confirm':
            raise osv.except_osv(_('Error'), _('Gateway already verified!'))

        if gate.code == data['form']['code']:
            pooler.get_pool(cr.dbname).get('sms.smsclient').write(cr, uid, [data['id']], {'state': 'confirm'})
        else:
            raise osv.except_osv(_('Error'), _('Verification failed. Invalid Verification Code!'))
        return {}

    states = {
        'init': {
            'actions': [],
            'result': {'type': 'form', 'arch': form, 'fields': fields, 'state': [('end', 'Cancel'), ('check', 'Verify Code')]}
        },
        'check': {
            'actions': [checkcode],
            'result': {'type': 'state', 'state': 'end'}
        }
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
