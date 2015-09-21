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
from openerp.exceptions import Warning as UserError
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


class partner_sms_send(models.TransientModel):
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

    #TODO move to new API
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
            config_vals = {}
            if serv_config.has_section(global_section_name):
                config_vals.update(serv_config.items(global_section_name))
                custom_section_name = '.'.join((global_section_name,
                                                sms_provider.name
                                                ))
                if serv_config.has_section(custom_section_name):
                    config_vals.update(serv_config.items(custom_section_name))
                for key in config_vals:
                    sms_provider[key] = config_vals[key]

    @api.multi
    @api.depends('method')
    def _get_protocole(self):
        for record in self:
            self.protocole = self.method.split('_')[0]

    name = fields.Char('Gateway Name', required=True)
    url = fields.Char('Gateway URL',
                      help='Base url for message',
                      compute='_get_provider_conf'
                      )
    url_visible = fields.Boolean(default=False)
    method = fields.Selection(
        string='API Method',
        selection='get_method')
    protocole = fields.Char(compute='_get_protocole')
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
    nostop = fields.Boolean(
        help='Do not display STOP clause in the message, this requires that '
             'this is not an advertising message',
        default=True)
    nostop_visible = fields.Boolean(default=False)
    char_limit = fields.Boolean('Character Limit', default=True)
    char_limit_visible = fields.Boolean(default=False)
    default_gateway = fields.Boolean(default=False)
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner')

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
    def _run_send_sms(self):
        sms = self.env['sms.sms'].search([('state', '=', 'draft')])
        return sms.send()


class SmsSms(models.Model):
    _name = 'sms.sms'
    _description = 'SMS'
    _rec_name = 'mobile'

    message = fields.Text(
        size=256,
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]})
    mobile = fields.Char(
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]})
    gateway_id = fields.Many2one(
        'sms.smsclient',
        'SMS Gateway',
        readonly=True,
        states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Queued'),
        ('send', 'Sent'),
        ('cancel', 'Cancel'),
        ('error', 'Error'),
        ], 'Message Status',
        select=True,
        readonly=True,
        default='draft')
    error = fields.Text(
        'Last Error',
        size=256,
        readonly=True,
        states={'draft': [('readonly', False)]})
    validity = fields.Integer(
        'Validity',
        help='The maximum time -in minute(s)- before the message is dropped')
    classes = fields.Selection(
        selection=CLASSES_LIST,
        help='The sms class: flash(0), phone display(1), SIM(2), toolkit(3)')
    deferred = fields.Integer(
        help='The time -in minute(s)- to wait before sending the message')
    priority = fields.Selection(
        selection=PRIORITY_LIST,
        help='The priority of the message ')
    coding = fields.Selection([
        ('1', '7 bit'),
        ('2', 'Unicode')
        ], help='The sms coding: 1 for 7 bit or 2 for unicode')
    tag = fields.Char(
        size=256,
        help='An optional tag')
    nostop = fields.Boolean(
        'NoStop',
        help='Do not display STOP clause in the message, this requires that'
             'this is not an advertising message')

    @api.multi
    def _send_http(self):
        self.ensure_one()
        if not hasattr(self, "_prepare_%s" % self.gateway_id.method):
            raise NotImplemented
        params = getattr(self, "_prepare_%s" % self.gateway_id.method)()
        params_encoded = urllib.urlencode(params)
        answer = urllib.urlopen(
            "%s?%s" % (self.gateway_id.url, params_encoded))
        _logger.debug(answer.read())

    @api.multi
    def send(self):
        for sms in self:
            if sms.gateway_id.char_limit and len(sms.message) > 160:
                sms.write({
                    'state': 'error',
                    'error': 'Size of SMS should not be more then 160 char',
                    })
            if not hasattr(self, "_send_%s" % self.gateway_id.protocole):
                raise NotImplemented
            else:
                try:
                    with sms._cr.savepoint():
                        getattr(sms, "_send_%s" % self.gateway_id.protocole)()
                        sms.write({'state': 'send', 'error': ''})
                except Exception, e:
                    _logger.error('Failed to send sms', e)
                    sms.write({'error': e, 'state': 'error'})
                sms._cr.commit()
        return True

    @api.multi
    def cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def retry(self):
        self.write({'state': 'draft'})
