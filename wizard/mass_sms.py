##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>)
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
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
    
    def _default_get_gateway(self, cr, uid, fields, context = None):
        if context is None:
            context = {}
        sms_obj = self.pool.get('sms.smsclient')
        gateway_id = sms_obj.search(cr, uid, [], limit=1)[0]
        return gateway_id
    
    
    def onchange_gateway_mass(self,cr,uid,ids,gateway_id,context = None):
        if context is None:
            context = {}
        sms_obj = self.pool.get('sms.smsclient')
        gateway = sms_obj.browse(cr,uid,gateway_id,context=context)
        return {
                'value': {
                    'validity': gateway.validity, 
                    'classes': gateway.classes,
                    'deferred': gateway.deferred,
                    'priority': gateway.priority,
                    'coding': gateway.coding,
                    'tag': gateway.tag,
                    'nostop': gateway.nostop,
                        }
                }
    
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
        datas = {}
        gateway_id = self.browse(cr, uid, ids, context)[0].gateway.id
        client_obj = self.pool.get('sms.smsclient')
        partner_obj = self.pool.get('res.partner')
        active_ids = context.get('active_ids')
        for data in self.browse(cr, uid, ids, context) :
            if not data.gateway:
                raise osv.except_osv(_('Error'), _('No Gateway Found'))
            else:
                datas['gateway'] = data.gateway.id
                datas['text'] = data.text
                datas['validity'] = data.validity
                datas['classes'] = data.classes
                datas['deferred'] = data.deferred
                datas['priority'] = data.priority
                datas['coding'] = data.coding
                datas['tag'] = data.tag
                datas['nostop'] = data.nostop
        for id in active_ids :
            datas['to'] = partner_obj.browse(cr, uid, id, context=context).mobile
            client_obj.send_message(cr, uid, datas)
        return {}
    
    
    
    _columns = {
                'gateway': fields.many2one('sms.smsclient','SMS Gateway',required = True),
                'text': fields.text('Text', required = True),
                'validity': fields.integer('Validity',help='the maximum time -in minute(s)- before the message is dropped'),
                'classes': fields.selection([('0','0'),('1','1'),('2','2'),('3','3')],'Class',help='the sms class: flash(0),phone display(1),SIM(2),toolkit(3)'),
                'deferred': fields.integer('Deferred',help='the time -in minute(s)- to wait before sending the message'),
                'priority': fields.selection([('0','0'),('1','1'),('2','2'),('3','3')],'Priority',help='the priority of the message '),
                'coding': fields.selection([('1','1'),('2','2')],'Coding',help='the sms coding: 1 for 7 bit or 2 for unicode'),
                'tag': fields.char('Tag', size=256,help='an optional tag'),
                'nostop': fields.selection([('0','0'),('1','1')],'NoStop',help='do not display STOP clause in the message, this requires that this is not an advertising message'),
        }
    _defaults = {
        'gateway': _default_get_gateway,        
    }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
