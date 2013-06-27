# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011 SYLEAM (<http://syleam.fr/>)
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import urllib
from openerp.osv import fields, orm, osv
from openerp.tools.translate import _


from SOAPpy import WSDL

class partner_sms_send(orm.Model):
    _name = "partner.sms.send"
    
    def _default_get_mobile(self, cr, uid, fields, context = None):
        if context is None:
            context = {}
        partner_pool = self.pool.get('res.partner')
        active_ids = fields.get('active_ids')
        res = {}
        i = 0
        for partner in partner_pool.browse(cr, uid, active_ids, context=context): 
                i +=1           
                res = partner.mobile
        if i > 1:
            raise osv.except_osv(_('Error'), _('You can only select one partner'))
        return res
    
    def _default_get_gateway(self, cr, uid, fields, context = None):
        if context is None:
            context = {}
        sms_obj = self.pool.get('sms.smsclient')
        gateway_id = sms_obj.search(cr, uid, [], limit=1)[0]
        return gateway_id
    
    
    def onchange_gateway(self,cr,uid,ids,gateway_id,context = None):
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
        
    _columns = {
        'mobile_to': fields.char('To', size=256, required=True),
        'app_id': fields.char('API ID', size=256),
        'user': fields.char('Login', size=256),
        'password': fields.char('Password', size=256),
        'text': fields.text('SMS Message',required=True),
        'gateway': fields.many2one('sms.smsclient','SMS Gateway',required = True),
        'validity': fields.integer('Validity',help='the maximum time -in minute(s)- before the message is dropped'),
        'classes': fields.selection([('0','0'),('1','1'),('2','2'),('3','3')],'Class',help='the sms class: flash(0),phone display(1),SIM(2),toolkit(3)'),
        'deferred': fields.integer('Deferred',help='the time -in minute(s)- to wait before sending the message'),
        'priority': fields.selection([('0','0'),('1','1'),('2','2'),('3','3')],'Priority',help='the priority of the message '),
        'coding': fields.selection([('1','1'),('2','2')],'Coding',help='the sms coding: 1 for 7 bit or 2 for unicode'),
        'tag': fields.char('Tag', size=256,help='an optional tag'),
        'nostop': fields.selection([('0','0'),('1','1')],'NoStop',help='do not display STOP clause in the message, this requires that this is not an advertising message'),
    }
    
    _defaults = {
        'mobile_to': _default_get_mobile,
        'gateway': _default_get_gateway,        
    }
    
    def sms_send(self, cr, uid, ids, context):
        client_obj = self.pool.get('sms.smsclient')
        datas = {}
        for data in self.browse(cr, uid, ids, context) :
            if not data.gateway:
                raise osv.except_osv(_('Error'), _('No Gateway Found'))
            else:
                datas['gateway'] = data.gateway.id
                datas['to'] = data.mobile_to
                datas['text'] = data.text
                datas['validity'] = data.validity
                datas['classes'] = data.classes
                datas['deferred'] = data.deferred
                datas['priority'] = data.priority
                datas['coding'] = data.coding
                datas['tag'] = data.tag
                datas['nostop'] = data.nostop
                client_obj.send_message(cr, uid, datas)
        return {}
     

class SMSClient(orm.Model):
    _name = 'sms.smsclient'
    _description = 'SMS Client'

    _columns = {
        'name': fields.char('Gateway Name', size=256, required=True),
        'url': fields.char('Gateway URL', size=256, required=True, help='Base url for message'),
        'property_ids': fields.one2many('sms.smsclient.parms', 'gateway_id', 'Parameters'),
        'history_line': fields.one2many('sms.smsclient.history', 'gateway_id', 'History'),
        'method': fields.selection([
            ('http', 'HTTP Method'),
            ('smpp', 'SMPP Method')
        ], 'API Method', select=True),
        'state': fields.selection([
            ('new', 'Not Verified'),
            ('waiting', 'Waiting for Verification'),
            ('confirm', 'Verified'),
        ], 'Gateway Status', select=True, readonly=True),
        'users_id': fields.many2many('res.users', 'res_smsserver_group_rel', 'sid', 'uid', 'Users Allowed'),
        'code': fields.char('Verification Code', size=256),
        'body': fields.text('Message', help="The message text that will be send along with the email which is send through this server"),
        'validity': fields.integer('Validity',help='the maximum time -in minute(s)- before the message is dropped'),
        'classes': fields.selection([('0','0'),('1','1'),('2','2'),('3','3')],'Class',help='the sms class: flash(0),phone display(1),SIM(2),toolkit(3)'),
        'deferred': fields.integer('Deferred',help='the time -in minute(s)- to wait before sending the message'),
        'priority': fields.selection([('0','0'),('1','1'),('2','2'),('3','3')],'Priority',help='the priority of the message '),
        'coding': fields.selection([('1','1'),('2','2')],'Coding',help='the sms coding: 1 for 7 bit or 2 for unicode'),
        'tag': fields.char('Tag', size=256,help='an optional tag'),
        'nostop': fields.selection([('0','0'),('1','1')],'NoStop',help='do not display STOP clause in the message, this requires that this is not an advertising message'),
    }

    _defaults = {
        'state': lambda *a: 'new',
        'method': lambda *a: 'http',
        'validity': 10,
        'classes': '1',
        'deferred': 0, 
        'priority': '3',
        'coding': '1',
        'nostop': '1',
    }

    def check_permissions(self, cr, uid, id):
        cr.execute('select * from res_smsserver_group_rel where sid=%s and uid=%s' % (id, uid))
        data = cr.fetchall()
        if len(data) <= 0:
            return False
        return True

    def send_message(self, cr, uid, datas):
        print datas
        gateway_id = datas['gateway']
        gate = self.browse(cr, uid, gateway_id)

        if not self.check_permissions(cr, uid, gateway_id):
            raise osv.except_osv(_('Permission Error!'), _('You have no permission to access %s ') % (gate.name,))

        if gate.method != 'http':
            raise osv.except_osv(_('Error'), _('This method is not implemented (%s)') % (gate.name,))

        url = gate.url
        prms = {}
        for p in gate.property_ids:
            if p.type == 'to':
                prms[p.name] = to
            elif p.type == 'sms':
                prms[p.name] = text
            else:
                prms[p.name] = p.value

        params = urllib.urlencode(prms)
        req = url + "?" + params
        queue = self.pool.get('sms.smsclient.queue')
        queue.create(cr, uid, {
                    'name': req,
                    'gateway_id': gateway_id,
                    'state': 'draft',
                    'mobile': datas['to'],
                    'msg': datas['text'],
                    'validity': datas['validity'], 
                    'classes': datas['classes'], 
                    'deffered': datas['deferred'], 
                    'priorirty': datas['priority'], 
                    'coding': datas['coding'], 
                    'tag': datas['tag'], 
                    'nostop': datas['nostop'], 
                    
                })
        return True

    def _check_queue(self, cr, uid, ids=False, context=None):
        if context is None:
            context = {}
        queue = self.pool.get('sms.smsclient.queue')
        history = self.pool.get('sms.smsclient.history')
        sids = queue.search(cr, uid, [('state', '!=', 'send'), ('state', '!=', 'sending')], limit=30, context=context)
        queue.write(cr, uid, sids, {'state': 'sending'})
        error = []
        sent = []
        for sms in queue.browse(cr, uid, sids, context=context):
#             f = urllib.urlopen(sms.name)
            
            if len(sms.msg) > 160:
                error.append(sms.id)
                continue
            
            ### New Send Process OVH Dedicated ###
            ## Parameter Fetch ##
            for p in sms.gateway_id.property_ids:
                if p.type == 'user':
                    login = p.value
                elif p.type == 'password':
                    pwd = p.value
                elif p.type == 'sender':
                    sender = p.value
                elif p.type == 'sms':
                    account = p.value
            soap = WSDL.Proxy(sms.gateway_id.url)
            result = soap.telephonySmsUserSend(str(login), str(pwd), str(account), str(sender), str(sms.mobile), str(sms.msg), int(sms.validity), int(sms.classes), int(sms.deferred), int(sms.priority), int(sms.coding), int(sms.nostop))
            ### End of the new process ###
            history.create(cr, uid, {
                        'name': _('SMS Sent'),
                        'gateway_id': sms.gateway_id.id,
                        'sms': sms.msg,
                        'to': sms.mobile,
                    }, context=context)
            sent.append(sms.id)
             ## Send Function ##
        queue.write(cr, uid, sent, {'state': 'send'})
        queue.write(cr, uid, error, {'state': 'error', 'error': 'Size of SMS should not be more then 160 char'})
        return True



class SMSQueue(orm.Model):
    _name = 'sms.smsclient.queue'
    _description = 'SMS Queue'

    _columns = {
        'name': fields.text('SMS Request', size=256, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'msg': fields.text('SMS Text', size=256, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'mobile': fields.char('Mobile No', size=256, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'gateway_id': fields.many2one('sms.smsclient', 'SMS Gateway', readonly=True, states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft', 'Queued'),
            ('sending', 'Waiting'),
            ('send', 'Sent'),
            ('error', 'Error'),
        ], 'Message Status', select=True, readonly=True),
        'error': fields.text('Last Error', size=256, readonly=True, states={'draft': [('readonly', False)]}),
        'date_create': fields.datetime('Date', readonly=True),
        'validity': fields.integer('Validity',help='the maximum time -in minute(s)- before the message is dropped'),
        'classes': fields.selection([('0','0'),('1','1'),('2','2'),('3','3')],'Class',help='the sms class: flash(0),phone display(1),SIM(2),toolkit(3)'),
        'deferred': fields.integer('Deferred',help='the time -in minute(s)- to wait before sending the message'),
        'priority': fields.selection([('0','0'),('1','1'),('2','2'),('3','3')],'Priority',help='the priority of the message '),
        'coding': fields.selection([('1','1'),('2','2')],'Coding',help='the sms coding: 1 for 7 bit or 2 for unicode'),
        'tag': fields.char('Tag', size=256,help='an optional tag'),
        'nostop': fields.selection([('0','0'),('1','1')],'NoStop',help='do not display STOP clause in the message, this requires that this is not an advertising message'),
        
    }

    _defaults = {
        'date_create': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': 'draft',
    }



class Properties(orm.Model):
    _name = 'sms.smsclient.parms'
    _description = 'SMS Client Properties'

    _columns = {
        'name': fields.char('Property name', size=256, required=True, help='Name of the property whom appear on the URL'),
        'value': fields.char('Property value', size=256, required=True, help='Value associate on the property for the URL'),
        'gateway_id': fields.many2one('sms.smsclient', 'SMS Gateway'),
        'type': fields.selection([
            ('user', 'User'),
            ('password', 'Password'),
            ('sender', 'Sender Name'),
            ('to', 'Recipient No'),
            ('sms', 'SMS Message')
        ], 'API Method', select=True, help='If parameter concern a value to substitute, indicate it'),
    }

Properties()


class HistoryLine(orm.Model):
    _name = 'sms.smsclient.history'
    _description = 'SMS Client History'

    _columns = {
        'name': fields.char('Description', size=160, required=True, readonly=True),
        'date_create': fields.datetime('Date', readonly=True),
        'user_id': fields.many2one('res.users', 'Username', readonly=True, select=True),
        'gateway_id': fields.many2one('sms.smsclient', 'SMS Gateway', ondelete='set null', required=True),
        'to': fields.char('Mobile No', size=15, readonly=True),
        'sms': fields.text('SMS', size=160, readonly=True),
    }

    _defaults = {
        'date_create': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda obj, cr, uid, context: uid,
    }

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}

        super(HistoryLine, self).create(cr, uid, vals, context=context)
        cr.commit()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
