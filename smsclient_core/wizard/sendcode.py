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

from openerp.osv import fields, orm
from openerp.tools.translate import _

class sendcode(orm.TransientModel):
    _name = 'sms.smsclient.code.send'

    def send_code(self, cr, uid, data, context):
        key = md5(time.strftime('%Y-%m-%d %H:%M:%S') + data['form']['smsto']).hexdigest()
        sms_pool = pooler.get_pool(cr.dbname).get('sms.smsclient')
        gate = sms_pool.browse(cr, uid, data['id'])
        msg = key[0:6]
        sms_pool._send_message(cr, uid, data['id'], data['form']['smsto'], msg)
        if not gate.state in('new', 'waiting'):
            raise osv.except_osv(_('Error'), _('Verification Failed. Please check the Server Configuration!'))

        pooler.get_pool(cr.dbname).get('sms.smsclient').write(cr, uid, [data['id']], {'state': 'waiting', 'code': msg})
        return {}

#    states = {
#        'init': {
#            'actions': [],
#            'result': {'type': 'form', 'arch': form, 'fields': fields, 'state': [('end', 'Cancel'), ('send', 'Send Code')]}
#        },
#        'send': {
#            'actions': [send_code],
#            'result': {'type': 'state', 'state': 'end'}
#        }
#    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
