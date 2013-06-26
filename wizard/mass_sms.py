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

import netsvc
from openerp.osv import fields, orm
from openerp.tools.translate import _

class part_sms(orm.TransientModel):
    _name = 'part.sms'
    
    def merge_message(self, cr, uid, message, object, partner):

        def merge(match):
            exp = str(match.group()[2: -2]).strip()
            result = eval(exp, {'object': object, 'partner': partner})
            if result in (None, False):
                return str("--------")
            return str(result)
    
        com = re.compile('(\[\[.+?\]\])')
        msg = com.sub(merge, message)
        return msg
    
    def sms_mass_send(self, cr, uid, ids, context):
        text = self.browse(cr, uid, ids, context)[0].text
        gateway_id = self.browse(cr, uid, ids, context)[0].gateway.id
        client_obj = self.pool.get('sms.smsclient')
        partner_obj = self.pool.get('res.partner')
        active_ids = context.get('active_ids')
        i = 0
        for id in active_ids :
            to = partner_obj.browse(cr, uid, id, context=context).mobile
            client_obj.send_message(cr, uid, gateway_id, to, text)
            i += 1
        print i
        return {}
    
    
    
    _columns = {
                'gateway': fields.many2one('sms.smsclient','SMS Gateway',required = True),
                'text': fields.text('Text', required = True),
        }
    
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
