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
from openerp.addons.server_environment import serv_config
_logger = logging.getLogger(__name__)


PRIORITY_LIST = [
    ('0', '0'),
    ('1', '1'),
    ('2', '2'),
    ('3', '3')
]

CLASSES_LIST = [
    ('0', 'Flash'),
    ('1', 'Phone display'),
    ('2', 'SIM'),
    ('3', 'Toolkit')
]


class partner_sms_send(models.Model):
    _name = "partner.sms.send"

    @api.model
    def _default_get_mobile(self):
        partner_pool = self.env['res.partner']
        active_ids = self._context.get('active_ids')
        res = {}
        if len(active_ids) > 1:
            raise Warning(_('You can only select one partner'))
        for partner in partner_pool.browse(active_ids):
            res = partner.mobile
        return res

    @api.model
    def _default_get_gateway(self):
        sms_obj = self.env['sms.smsclient']
        gateways = sms_obj.search([], limit=1)
        return gateways or False

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

    mobile_to = fields.Char('To', required=True,
                            default=_default_get_mobile)
    app_id = fields.Char('API ID')
    user = fields.Char('Login')
    password = fields.Char('Password')
    text = fields.Text('SMS Message', required=True)
    gateway = fields.Many2one('sms.smsclient', 'SMS Gateway', required=True,
                              default=_default_get_gateway
                              )
    validity = fields.Integer('Validity',
                              help='the maximum time -in minute(s)-'
                                   'before the message is dropped')
    classes = fields.Selection(
        CLASSES_LIST,
        'Class',
        help='the sms class: flash(0), phone display(1), SIM(2), toolkit(3)')
    deferred = fields.Integer('Deferred',
                              help='the time -in minute(s)- '
                                   'to wait before sending the message')
    priority = fields.Selection(PRIORITY_LIST, 'Priority',
                                help='The priority of the message')
    coding = fields.Selection([
        ('1', '7 bit'),
        ('2', 'Unicode')
        ], 'Coding', help='The SMS coding: 1 for 7 bit or 2 for unicode')
    tag = fields.Char('Tag', help='an optional tag')
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

    @api.model
    def get_method(self):
        return []

    @api.multi
    def _get_provider_conf(self):
        for sms_provider in self:
            global_section_name = 'sms_provider'
            # default vals
            config_vals = {}
            if serv_config.has_section(global_section_name):
                config_vals.update((serv_config.items(global_section_name)))
                custom_section_name = '.'.join((global_section_name,
                                                sms_provider.name
                                                ))
                if serv_config.has_section(custom_section_name):
                    config_vals.update(serv_config.items(custom_section_name))
                    if config_vals.get('url_service'):
                        sms_provider.url = config_vals['url_service']
                    if config_vals.get('sms_account'):
                        sms_provider.sms_account = config_vals['sms_account']
                    if config_vals.get('login'):
                        sms_provider.login_provider = config_vals['login']
                    if config_vals.get('password'):
                        sms_provider.password_provider = config_vals['password']
                    if config_vals.get('from'):
                        sms_provider.from_provider = config_vals['from']


    name = fields.Char('Gateway Name', required=True)
    url = fields.Char('Gateway URL',
                      help='Base url for message',
                      compute='_get_provider_conf'
                      )
    url_visible = fields.Boolean(default=False)
    method = fields.Selection(string='API Method',
                              selection='get_method',
                              index=True,
                              )
    state = fields.Selection([
        ('new', 'Not Verified'),
        ('waiting', 'Waiting for Verification'),
        ('confirm', 'Verified'),
        ], 'Gateway Status', index=True, readonly=True, default='new')
    user_ids = fields.Many2many(
        'res.users',
        string='Users Allowed')
    sms_account = fields.Char(compute='_get_provider_conf')
    sms_account_visible = fields.Boolean(default=False)
    login_provider = fields.Char(compute='_get_provider_conf')
    login_provider_visible = fields.Boolean(default=False)
    password_provider = fields.Char(compute='_get_provider_conf')
    password_provider_visible = fields.Boolean(default=False)
    from_provider = fields.Char(compute='_get_provider_conf')
    from_provider_visible = fields.Boolean(default=False)
    code = fields.Char('Verification Code')
    code_visible = fields.Boolean(default=False)
    body = fields.Text('Message',
                       help="The message text that will be send along with the"
                            " email which is send through this server")
    validity = fields.Integer(
        help='The maximum time - in minute(s) - before the message is dropped',
        default=10,
        )
    validity_visible = fields.Boolean(default=False)
    classes = fields.Selection(
        CLASSES_LIST, 'Class',
        help='The SMS class: flash(0),phone display(1),SIM(2),toolkit(3)',
        default='1'
        )
    classes_visible = fields.Boolean(default=False)
    deferred = fields.Integer(
        'Deferred',
        help='The time -in minute(s)- to wait before sending the message',
        default=0)
    deferred_visible = fields.Boolean(default=False)

    priority = fields.Selection(PRIORITY_LIST,
                                'Priority',
                                help='The priority of the message ',
                                default='3')
    priority_visible = fields.Boolean(default=False)
    coding = fields.Selection([
        ('1', '7 bit'),
        ('2', 'Unicode')
        ], 'Coding',
        help='The SMS coding: 1 for 7 bit (160 chracters max'
             'lenght) or 2 for unicode (70 characters max'
             'lenght)',
        default='1'
    )
    coding_visible = fields.Boolean(default=False)
    tag = fields.Char('Tag', help='an optional tag')
    tag_visible = fields.Boolean(default=False)
    nostop = fields.Boolean('NoStop',
                            help='Do not display STOP clause in the message,'
                                 'this requires that this is not an'
                                 'advertising message',
                            default=True
                            )
    nostop_visible = fields.Boolean(default=False)
    char_limit = fields.Boolean('Character Limit', default=True)
    char_limit_visible = fields.Boolean(default=False)
    default_gateway = fields.Boolean(default=False)

    @api.onchange('method')
    def onchange_method(self):
        if not self.method:
            self.url_visible = False
            self.sms_account_visible = False
            self.login_provider_visible = False
            self.password_provider_visible = False
            self.from_provider_visible = False
            self.validity_visible = False
            self.classes_visible = False
            self.deferred_visible = False
            self.nostop_visible = False
            self.priority_visible = False
            self.coding_visible = False
            self.tag_visible = False
            self.char_limit_visible = False

    @api.multi
    def _check_permissions(self):
        self.ensure_one()
        if not self.env.uid in self.sudo().user_ids.ids:
            return False
        return True

    @api.model
    def _prepare_sms(self, data, name):
        return {
            'name': name,
            'gateway_id': data.gateway.id,
            'state': 'draft',
            'mobile': data.mobile_to,
            'msg': data.text,
            'validity': data.validity,
            'classes': data.classes,
            'deffered': data.deferred,
            'priority': data.priority,
            'coding': data.coding,
            'tag': data.tag,
            'nostop': data.nostop,
        }

    # This method must be inherit to forming the url according to the provider
    @api.model
    def _send_message(self, data):
        return True

    @api.model
    def _check_queue(self):
        sms_obj = self.env['sms.sms']
        sids = sms_obj.search([
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
            if 'http' in sms.gateway_id.method:
                try:
                    answer = urllib.urlopen(sms.name)
                    _logger.info(answer.read())
                except Exception, e:
                    raise Warning(e)
            sent_ids.append(sms.id)
        rec_sent_ids = sms_obj.browse(sent_ids)
        rec_sent_ids.write({'state': 'send'})
        rec_error_ids = sms_obj.browse(error_ids)
        rec_error_ids.write({
            'state': 'error',
            'error': 'Size of SMS should not be more then 160 char'
            })
        return True


class SmsSms(models.Model):
    _name = 'sms.sms'
    _description = 'SMS'

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
        CLASSES_LIST,
        'Class',
        help='The sms class: flash(0), phone display(1), SIM(2), toolkit(3)')
    deferred = fields.Integer(
        'Deferred',
        help='The time -in minute(s)- to wait before sending the message')

    priority = fields.Selection(PRIORITY_LIST, 'Priority',
                                help='The priority of the message ')
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
