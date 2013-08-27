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

from openerp.osv import fields, orm
from openerp.tools.translate import _

class part_sms(orm.TransientModel):
    _name = 'part.sms'

    def _default_get_gateway(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        sms_obj = self.pool.get('sms.smsclient')
        gateway_ids = sms_obj.search(cr, uid, [], limit=1, context=context)
        return gateway_ids and gateway_ids[0] or False

    def onchange_gateway_mass(self, cr, uid, ids, gateway_id, context=None):
        if context is None:
            context = {}
        if not gateway_id:
            return {}
        sms_obj = self.pool.get('sms.smsclient')
        gateway = sms_obj.browse(cr, uid, gateway_id, context=context)
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

    def _merge_message(self, cr, uid, message, object, partner, context=None):
        def merge(match):
            exp = str(match.group()[2: -2]).strip()
            result = eval(exp, {'object': object, 'partner': partner})
            if result in (None, False):
                return str("--------")
            return str(result)
        com = re.compile('(\[\[.+?\]\])')
        msg = com.sub(merge, message)
        return msg

    def sms_mass_send(self, cr, uid, ids, context=None):
        datas = {}
        gateway_id = self.browse(cr, uid, ids, context)[0].gateway.id
        client_obj = self.pool.get('sms.smsclient')
        partner_obj = self.pool.get('res.partner')
        active_ids = context.get('active_ids')
        for data in self.browse(cr, uid, ids, context) :
            if not data.gateway:
                raise orm.except_orm(_('Error'), _('No Gateway Found'))
            else:
                for partner in partner_obj.browse(cr, uid, active_ids, context=context):
                    data.mobile_to = partner.mobile
                    client_obj._send_message(cr, uid, data, context=context)
        return True

    _columns = {
        'gateway': fields.many2one('sms.smsclient', 'SMS Gateway', required=True),
        'text': fields.text('Text', required=True),
        'validity': fields.integer('Validity',
            help='The maximum time -in minute(s)- before the message is dropped'),
        'classes': fields.selection([
                ('0', 'Flash'),
                ('1', 'Phone display'),
                ('2', 'SIM'),
                ('3', 'Toolkit'),
            ], 'Class',
            help='The sms class: flash(0),phone display(1),SIM(2),toolkit(3)'),
        'deferred': fields.integer('Deferred',
            help='The time -in minute(s)- to wait before sending the message'),
        'priority': fields.selection([
                ('0', '0'),
                ('1', '1'),
                ('2', '2'),
                ('3', '3')
            ], 'Priority', help='The priority of the message'),
        'coding': fields.selection([
                ('1', '7 bit'),
                ('2', 'Unicode')
            ], 'Coding', help='The sms coding: 1 for 7 bit or 2 for unicode'),
        'tag': fields.char('Tag', size=256, help='An optional tag'),
        'nostop': fields.selection([
                ('0', '0'),
                ('1', '1')
            ], 'NoStop',
            help='Do not display STOP clause in the message, this requires that this is not an advertising message'),
    }

    _defaults = {
        'gateway': _default_get_gateway,        
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
