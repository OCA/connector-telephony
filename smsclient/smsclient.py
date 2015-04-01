# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011 SYLEAM (<http://syleam.fr/>)
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#    Copyright (C) 2015 Valentin Chemiere <valentin.chemiere@akretion.com>
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

from openerp import models, fields, api, _
from openerp.exceptions import Warning
import urllib
import logging
_logger = logging.getLogger(__name__)

try:
    from SOAPpy import WSDL
except:
    _logger.warning("ERROR IMPORTING SOAPpy, if not installed, please install"
                    "it: e.g.: apt-get install python-soappy")


class partner_sms_send(models.Model):
    _name = "partner.sms.send"

    @api.model
    def _default_get_mobile(self):
        partner_pool = self.env['res.partner']
        active_ids = self._context.get('active_ids')
        res = {}
        i = 0
        for partner in partner_pool.browse(active_ids):
            i += 1
            res = partner.mobile
        if i > 1:
            raise Warning(_('You can only select one partner'))
        return res

    @api.model
    def _default_get_gateway(self):
        sms_obj = self.env['sms.smsclient']
        gateway_ids = sms_obj.search([], limit=1)
        return gateway_ids and gateway_ids[0] or False

    @api.multi
    def onchange_gateway(self, gateway_id):
        sms_obj = self.env['sms.smsclient']
        if not gateway_id:
            return {}
        gateway = sms_obj.browse(gateway_id)
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

    mobile_to = fields.Char('To', size=256, required=True,
                            default=_default_get_mobile)
    app_id = fields.Char('API ID', size=256)
    user = fields.Char('Login', size=256)
    password = fields.Char('Password', size=256)
    text = fields.Text('SMS Message', required=True)
    gateway = fields.Many2one('sms.smsclient', 'SMS Gateway', required=True,
                              default=_default_get_gateway
                              )
    validity = fields.Integer('Validity',
                              help='the maximum time -in minute(s)-'
                                   'before the message is dropped')
    classes = fields.Selection([
        ('0', 'Flash'),
        ('1', 'Phone display'),
        ('2', 'SIM'),
        ('3', 'Toolkit')
        ],
        'Class',
        help='the sms class: flash(0), phone display(1), SIM(2), toolkit(3)')
    deferred = fields.Integer('Deferred',
                              help='the time -in minute(s)- '
                                   'to wait before sending the message')
    priority = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3')
        ], 'Priority', help='The priority of the message')
    coding = fields.Selection([
        ('1', '7 bit'),
        ('2', 'Unicode')
        ], 'Coding', help='The SMS coding: 1 for 7 bit or 2 for unicode')
    tag = fields.Char('Tag', size=256, help='an optional tag')
    nostop = fields.Boolean('NoStop',
                            help='Do not display STOP clause in the message,'
                                 'this requires that this is not an '
                                 'advertising message')

    @api.multi
    def sms_send(self):
        client_obj = self.env['sms.smsclient']
        for data in self:
            if not data.gateway:
                raise Warning(_('No Gateway Found'))
            else:
                client_obj._send_message(data)
        return {}


class SMSClient(models.Model):
    _name = 'sms.smsclient'
    _description = 'SMS Client'

    name = fields.Char('Gateway Name', size=256, required=True)
    url = fields.Char('Gateway URL', size=256,
                      required=True, help='Base url for message')
    property_ids = fields.One2many('sms.smsclient.parms',
                                   'gateway_id', 'Parameters')
    history_line = fields.One2many('sms.smsclient.history',
                                   'gateway_id', 'History')
    method = fields.Selection([
        ('http', 'HTTP Method'),
        ('smpp', 'SMPP Method')
        ], 'API Method', select=True, default='http')
    state = fields.Selection([
        ('new', 'Not Verified'),
        ('waiting', 'Waiting for Verification'),
        ('confirm', 'Verified'),
        ], 'Gateway Status', select=True, readonly=True, default='new')
    users_id = fields.Many2many('res.users',
                                'res_smsserver_group_rel',
                                'sid',
                                'uid',
                                'Users Allowed')
    code = fields.Char('Verification Code', size=256)
    body = fields.Text('Message',
                       help="The message text that will be send along with the"
                            "email which is send through this server")
    validity = fields.Integer('Validity',
                              help='The maximum time - in minute(s) -'
                                   'before the message is dropped',
                              default=10
                              )
    classes = fields.Selection([
        ('0', 'Flash'),
        ('1', 'Phone display'),
        ('2', 'SIM'),
        ('3', 'Toolkit')
        ], 'Class',
        help='The SMS class: flash(0),phone display(1),SIM(2),toolkit(3)',
        default='1'
    )
    deferred = fields.Integer(
        'Deferred',
        help='The time -in minute(s)- to wait before sending the message',
        default=0)

    priority = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3')
        ], 'Priority', help='The priority of the message ', default='3')
    coding = fields.Selection([
        ('1', '7 bit'),
        ('2', 'Unicode')
        ], 'Coding', help='The SMS coding: 1 for 7 bit or 2 for unicode',
        default='1'
    )
    tag = fields.Char('Tag', size=256, help='an optional tag')
    nostop = fields.Boolean('NoStop',
                            help='Do not display STOP clause in the message,'
                                 'this requires that this is not an'
                                 'advertising message',
                            default=True
                            )
    char_limit = fields.Boolean('Character Limit', default=True)

    @api.model
    def _check_permissions(self, gateway):
        cr = self.env.cr
        cr.execute('select * from res_smsserver_group_rel'
                   ' where sid= %s and uid= %s' % (gateway.id, self.env.uid))
        data = cr.fetchall()
        if len(data) <= 0:
            return False
        return True

    @api.model
    def _prepare_smsclient_queue(self, data, name):
        return {
            'name': name,
            'gateway_id': data.gateway.id,
            'state': 'draft',
            'mobile': data.mobile_to,
            'msg': data.text,
            'validity': data.validity,
            'classes': data.classes,
            'deffered': data.deferred,
            'priorirty': data.priority,
            'coding': data.coding,
            'tag': data.tag,
            'nostop': data.nostop,
        }

    @api.model
    def _send_message(self, data):
        gateway = data.gateway
        if gateway:
            if not self._check_permissions(gateway):
                raise Warning(_('You have no permission to access %s ')
                              % (gateway.name,))
            url = gateway.url
            name = url
            if gateway.method == 'http':
                prms = {}
                for p in data.gateway.property_ids:
                    if p.type == 'user':
                        prms[p.name] = p.value
                    elif p.type == 'password':
                        prms[p.name] = p.value
                    elif p.type == 'to':
                        prms[p.name] = data.mobile_to
                    elif p.type == 'sms':
                        prms[p.name] = data.text
                    elif p.type == 'extra':
                        prms[p.name] = p.value
                params = urllib.urlencode(prms)
                name = url + "?" + params
            queue_obj = self.env['sms.smsclient.queue']
            vals = self._prepare_smsclient_queue(data, name)
            queue_obj.create(vals)
        return True

    @api.model
    def _check_queue(self):
        queue_obj = self.env['sms.smsclient.queue']
        history_obj = self.env['sms.smsclient.history']
        sids = queue_obj.search([
            ('state', '!=', 'send'),
            ('state', '!=', 'sending')
            ], limit=30)
        error_ids = []
        sent_ids = []
        for sms in sids:
            sms.state = 'sending'
            if sms.gateway_id.char_limit:
                if len(sms.msg) > 160:
                    error_ids.append(sms.id)
                    continue
            if sms.gateway_id.method == 'http':
                try:
                    answer = urllib.urlopen(sms.name)
                    print answer.read()
                except Exception, e:
                    raise Warning(e)
            # New Send Process OVH Dedicated #
            # Parameter Fetch #
            if sms.gateway_id.method == 'smpp':
                for p in sms.gateway_id.property_ids:
                    if p.type == 'user':
                        login = p.value
                    elif p.type == 'password':
                        pwd = p.value
                    elif p.type == 'sender':
                        sender = p.value
                    elif p.type == 'sms':
                        account = p.value
                try:
                    soap = WSDL.Proxy(sms.gateway_id.url)
                    message = ''
                    if sms.coding == '2':
                        message = str(
                            sms.msg).decode('iso-8859-1').encode('utf8')
                    if sms.coding == '1':
                        message = str(sms.msg)
                    soap.telephonySmsUserSend(
                        str(login), str(pwd), str(account), str(sender), str(
                            sms.mobile), message, int(
                            sms.validity), int(
                            sms.classes), int(
                            sms.deferred), int(
                            sms.priority), int(
                            sms.coding), str(
                            sms.gateway_id.tag), int(
                            sms.gateway_id.nostop))
                    # End of the new process #
                except Exception, e:
                    raise Warning('Error', e)
            history_obj.create({
                'name': _('SMS Sent'),
                'gateway_id': sms.gateway_id.id,
                'sms': sms.msg,
                'to': sms.mobile,
                })
            sent_ids.append(sms.id)
        rec_sent_ids = queue_obj.browse(sent_ids)
        rec_sent_ids.write({'state': 'send'})
        rec_error_ids = queue_obj.browse(error_ids)
        rec_error_ids.write({
            'state': 'error',
            'error': 'Size of SMS should not be more then 160 char'
            })
        return True


class SMSQueue(models.Model):
    _name = 'sms.smsclient.queue'
    _description = 'SMS Queue'

    name = fields.Text('SMS Request', size=256,
                       required=True, readonly=True,
                       states={'draft': [('readonly', False)]})
    msg = fields.Text('SMS Text', size=256,
                      required=True, readonly=True,
                      states={'draft': [('readonly', False)]})
    mobile = fields.Char('Mobile No', size=256,
                         required=True, readonly=True,
                         states={'draft': [('readonly', False)]})
    gateway_id = fields.Many2one('sms.smsclient',
                                 'SMS Gateway', readonly=True,
                                 states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Queued'),
        ('sending', 'Waiting'),
        ('send', 'Sent'),
        ('error', 'Error'),
    ], 'Message Status', select=True, readonly=True, default='draft')
    error = fields.Text('Last Error', size=256,
                        readonly=True,
                        states={'draft': [('readonly', False)]})
    date_create = fields.Datetime('Date', readonly=True,
                                  default=fields.Datetime.now)
    validity = fields.Integer(
        'Validity',
        help='The maximum time -in minute(s)- before the message is dropped')

    classes = fields.Selection(
        [('0', 'Flash'), ('1', 'Phone display'), ('2', 'SIM'),
         ('3', 'Toolkit')], 'Class',
        help='The sms class: flash(0), phone display(1), SIM(2), toolkit(3)')
    deferred = fields.Integer(
        'Deferred',
        help='The time -in minute(s)- to wait before sending the message')

    priority = fields.Selection([
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3')
        ], 'Priority', help='The priority of the message ')
    coding = fields.Selection([
        ('1', '7 bit'),
        ('2', 'Unicode')
        ], 'Coding', help='The sms coding: 1 for 7 bit or 2 for unicode')
    tag = fields.Char('Tag', size=256,
                      help='An optional tag')
    nostop = fields.Boolean(
        'NoStop',
        help='Do not display STOP clause in the message, this requires that'
             'this is not an advertising message')


class Properties(models.Model):
    _name = 'sms.smsclient.parms'
    _description = 'SMS Client Properties'

    name = fields.Char('Property name', size=256,
                       help='Name of the property whom appear on the URL')
    value = fields.Char('Property value', size=256,
                        help='Value associate on the property for the URL')
    gateway_id = fields.Many2one('sms.smsclient', 'SMS Gateway')
    type = fields.Selection([
        ('user', 'User'),
        ('password', 'Password'),
        ('sender', 'Sender Name'),
        ('to', 'Recipient No'),
        ('sms', 'SMS Message'),
        ('extra', 'Extra Info')
        ], 'API Method', select=True,
        help='If parameter concern a value to substitute, indicate it')


class HistoryLine(models.Model):
    _name = 'sms.smsclient.history'
    _description = 'SMS Client History'

    @api.model
    def _get_default_user(self):
        return self.env.uid

    name = fields.Char('Description', size=160, required=True, readonly=True)
    date_create = fields.Datetime(
        'Date',
        readonly=True,
        default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', 'Username', readonly=True,
                              select=True, default=_get_default_user)
    gateway_id = fields.Many2one(
        'sms.smsclient',
        'SMS Gateway',
        ondelete='set null',
        required=True)
    to = fields.Char('Mobile No', size=15, readonly=True)
    sms = fields.Text('SMS', size=160, readonly=True)

    @api.model
    def create(self, vals):
        super(HistoryLine, self).create(vals)
        self.env.cr.commit()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
