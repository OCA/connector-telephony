# -*- coding: utf-8 -*-
# © 2010-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError
import logging
from pprint import pformat

try:
    # pip install py-Asterisk
    from Asterisk import Manager
except ImportError:
    Manager = None

_logger = logging.getLogger(__name__)


class AsteriskServer(models.Model):
    '''Asterisk server object, stores the parameters of the Asterisk IPBXs'''
    _name = "asterisk.server"
    _description = "Asterisk Servers"

    name = fields.Char(string='Asterisk Server Name', required=True)
    active = fields.Boolean(
        string='Active', default=True)
    ip_address = fields.Char(
        string='Asterisk IP address or DNS', required=True)
    port = fields.Integer(
        string='Port', required=True, default=5038,
        help="TCP port on which the Asterisk Manager Interface listens. "
        "Defined in /etc/asterisk/manager.conf on Asterisk.")
    out_prefix = fields.Char(
        string='Out Prefix', size=4, help="Prefix to dial to make outgoing "
        "calls. If you don't use a prefix to make outgoing calls, "
        "leave empty.")
    login = fields.Char(
        string='AMI Login', required=True,
        help="Login that Odoo will use to communicate with the "
        "Asterisk Manager Interface. Refer to /etc/asterisk/manager.conf "
        "on your Asterisk server.")
    password = fields.Char(
        string='AMI Password', required=True,
        help="Password that Odoo will use to communicate with the "
        "Asterisk Manager Interface. Refer to /etc/asterisk/manager.conf "
        "on your Asterisk server.")
    context = fields.Char(
        string='Dialplan Context', required=True,
        help="Asterisk dialplan context from which the calls will be "
        "made. Refer to /etc/asterisk/extensions.conf on your Asterisk "
        "server.")
    wait_time = fields.Integer(
        string='Wait Time', required=True, default=15,
        help="Amount of time (in seconds) Asterisk will try to reach "
        "the user's phone before hanging up.")
    extension_priority = fields.Integer(
        string='Extension Priority', required=True, default=1,
        help="Priority of the extension in the Asterisk dialplan. Refer "
        "to /etc/asterisk/extensions.conf on your Asterisk server.")
    alert_info = fields.Char(
        string='Alert-Info SIP Header',
        help="Set Alert-Info header in SIP request to user's IP Phone "
        "for the click2dial feature. If empty, the Alert-Info header "
        "will not be added. You can use it to have a special ring tone "
        "for click2dial (a silent one !) or to activate auto-answer "
        "for example.")
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get(
            'asterisk.server'),
        help="Company who uses the Asterisk server.")

    @api.multi
    @api.constrains(
        'out_prefix', 'wait_time', 'extension_priority', 'port',
        'context', 'alert_info', 'login', 'password')
    def _check_validity(self):
        for server in self:
            out_prefix = ('Out prefix', server.out_prefix)
            dialplan_context = ('Dialplan context', server.context)
            alert_info = ('Alert-Info SIP header', server.alert_info)
            login = ('AMI login', server.login)
            password = ('AMI password', server.password)

            if out_prefix[1] and not out_prefix[1].isdigit():
                raise ValidationError(
                    _("Only use digits for the '%s' on the Asterisk server "
                        "'%s'" % (out_prefix[0], server.name)))
            if server.wait_time < 1 or server.wait_time > 120:
                raise ValidationError(
                    _("You should set a 'Wait time' value between 1 and 120 "
                        "seconds for the Asterisk server '%s'" % server.name))
            if server.extension_priority < 1:
                raise ValidationError(
                    _("The 'extension priority' must be a positive value for "
                        "the Asterisk server '%s'" % server.name))
            if server.port > 65535 or server.port < 1:
                raise ValidationError(
                    _("You should set a TCP port between 1 and 65535 for the "
                        "Asterisk server '%s'" % server.name))
            for check_str in [dialplan_context, alert_info, login, password]:
                if check_str[1]:
                    try:
                        check_str[1].encode('ascii')
                    except UnicodeEncodeError:
                        raise ValidationError(
                            _("The '%s' should only have ASCII caracters for "
                                "the Asterisk server '%s'"
                                % (check_str[0], server.name)))

    @api.model
    def _connect_to_asterisk(self):
        '''
        Open the connection to the Asterisk Manager
        Returns an instance of the Asterisk Manager

        '''
        user = self.env.user
        ast_server = user.get_asterisk_server_from_user()
        # We check if the current user has a chan type
        if not user.asterisk_chan_type:
            raise UserError(
                _('No channel type configured for the current user.'))

        # We check if the current user has an internal number
        if not user.resource:
            raise UserError(
                _('No resource name configured for the current user'))

        _logger.debug(
            "User's phone: %s/%s", user.asterisk_chan_type, user.resource)
        _logger.debug(
            "Asterisk server: %s:%d", ast_server.ip_address, ast_server.port)

        # Connect to the Asterisk Manager Interface
        try:
            ast_manager = Manager.Manager(
                (ast_server.ip_address, ast_server.port),
                ast_server.login, ast_server.password)
        except Exception, e:
            _logger.error(
                "Error in the request to the Asterisk Manager Interface %s",
                ast_server.ip_address)
            _logger.error("Here is the error message: %s", e)
            raise UserError(
                _("Problem in the request from Odoo to Asterisk. "
                  "Here is the error message: %s" % e))

        return (user, ast_server, ast_manager)

    @api.multi
    def test_ami_connection(self):
        self.ensure_one()
        ast_manager = False
        try:
            ast_manager = Manager.Manager(
                (self.ip_address, self.port),
                self.login,
                self.password)
        except Exception, e:
            raise UserError(
                _("Connection Test Failed! The error message is: %s" % e))
        finally:
            if ast_manager:
                ast_manager.Logoff()
        raise UserError(_(
            "Connection Test Successfull! Odoo can successfully login to "
            "the Asterisk Manager Interface."))

    @api.model
    def _get_calling_number_from_channel(self, chan, user):
        '''Method designed to be inherited to work with
        very old or very new versions of Asterisk'''
        sip_account = user.asterisk_chan_type + '/' + user.resource
        internal_number = user.internal_number
        # 4 = Ring
        # 6 = Up
        if (
                chan.get('ChannelState') in ('4', '6') and (
                    chan.get('ConnectedLineNum') == internal_number or
                    chan.get('EffectiveConnectedLineNum') == internal_number or
                    sip_account in chan.get('BridgedChannel', ''))):
            _logger.debug(
                "Found a matching Event with channelstate = %s",
                chan.get('ChannelState'))
            return chan.get('CallerIDNum')
        # Compatibility with Asterisk 1.4
        if (
                chan.get('State') == 'Up' and
                sip_account in chan.get('Link', '')):
            _logger.debug("Found a matching Event in 'Up' state")
            return chan.get('CallerIDNum')
        return False

    @api.model
    def _get_calling_number(self):
        user, ast_server, ast_manager = self._connect_to_asterisk()
        calling_party_number = False
        try:
            list_chan = ast_manager.Status()
            # from pprint import pprint
            # pprint(list_chan)
            _logger.debug("Result of Status AMI request:")
            _logger.debug(pformat(list_chan))
            for chan in list_chan.values():
                calling_party_number = self._get_calling_number_from_channel(
                    chan, user)
                if calling_party_number:
                    break
        except Exception, e:
            _logger.error(
                "Error in the Status request to Asterisk server %s",
                ast_server.ip_address)
            _logger.error(
                "Here are the details of the error: '%s'", unicode(e))
            raise UserError(
                _("Can't get calling number from  Asterisk.\nHere is the "
                    "error: '%s'" % unicode(e)))

        finally:
            ast_manager.Logoff()

        _logger.debug("Calling party number: '%s'", calling_party_number)
        return calling_party_number

    @api.model
    def get_record_from_my_channel(self):
        calling_number = self.env['asterisk.server']._get_calling_number()
        # calling_number = "0641981246"
        if calling_number:
            record = self.env['phone.common'].get_record_from_phone_number(
                calling_number)
            if record:
                return record
            else:
                return calling_number
        else:
            return False


class ResUsers(models.Model):
    _inherit = "res.users"

    internal_number = fields.Char(
        string='Internal Number', copy=False,
        help="User's internal phone number.")
    dial_suffix = fields.Char(
        string='User-specific Dial Suffix',
        help="User-specific dial suffix such as aa=2wb for SCCP auto answer.")
    callerid = fields.Char(
        string='Caller ID', copy=False,
        help="Caller ID used for the calls initiated by this user.")
    # You'd probably think: Asterisk should reuse the callerID of sip.conf!
    # But it cannot, cf
    # http://lists.digium.com/pipermail/asterisk-users/
    # 2012-January/269787.html
    cdraccount = fields.Char(
        string='CDR Account',
        help="Call Detail Record (CDR) account used for billing this user.")
    asterisk_chan_type = fields.Selection([
        ('SIP', 'SIP'),
        ('IAX2', 'IAX2'),
        ('DAHDI', 'DAHDI'),
        ('Zap', 'Zap'),
        ('Skinny', 'Skinny'),
        ('MGCP', 'MGCP'),
        ('mISDN', 'mISDN'),
        ('H323', 'H323'),
        ('SCCP', 'SCCP'),
        # Local works for click2dial, but it won't work in
        # _get_calling_number() when trying to identify the
        # channel of the user, so it's better not to propose it
        # ('Local', 'Local'),
        ], string='Asterisk Channel Type', default='SIP',
        help="Asterisk channel type, as used in the Asterisk dialplan. "
        "If the user has a regular IP phone, the channel type is 'SIP'.")
    resource = fields.Char(
        string='Resource Name', copy=False,
        help="Resource name for the channel type selected. For example, "
        "if you use 'Dial(SIP/phone1)' in your Asterisk dialplan to ring "
        "the SIP phone of this user, then the resource name for this user "
        "is 'phone1'.  For a SIP phone, the phone number is often used as "
        "resource name, but not always.")
    alert_info = fields.Char(
        string='User-specific Alert-Info SIP Header',
        help="Set a user-specific Alert-Info header in SIP request to "
        "user's IP Phone for the click2dial feature. If empty, the "
        "Alert-Info header will not be added. You can use it to have a "
        "special ring tone for click2dial (a silent one !) or to "
        "activate auto-answer for example.")
    variable = fields.Char(
        string='User-specific Variable',
        help="Set a user-specific 'Variable' field in the Asterisk "
        "Manager Interface 'originate' request for the click2dial "
        "feature. If you want to have several variable headers, separate "
        "them with '|'.")
    asterisk_server_id = fields.Many2one(
        'asterisk.server', string='Asterisk Server',
        help="Asterisk server on which the user's phone is connected. "
        "If you leave this field empty, it will use the first Asterisk "
        "server of the user's company.")

    @api.multi
    @api.constrains('resource', 'internal_number', 'callerid')
    def _check_validity(self):
        for user in self:
            strings_to_check = [
                (_('Resource Name'), user.resource),
                (_('Internal Number'), user.internal_number),
                (_('Caller ID'), user.callerid),
                ]
            for check_string in strings_to_check:
                if check_string[1]:
                    try:
                        check_string[1].encode('ascii')
                    except UnicodeEncodeError:
                        raise ValidationError(_(
                            "The '%s' for the user '%s' should only have "
                            "ASCII caracters")
                            % (check_string[0], user.name))

    @api.multi
    def get_asterisk_server_from_user(self):
        '''Returns an asterisk.server recordset'''
        self.ensure_one()
        # We check if the user has an Asterisk server configured
        if self.asterisk_server_id:
            ast_server = self.asterisk_server_id
        else:
            asterisk_servers = self.env['asterisk.server'].search(
                [('company_id', '=', self.company_id.id)])
            # If the user doesn't have an asterisk server,
            # we take the first one of the user's company
            if not asterisk_servers:
                raise UserError(
                    _("No Asterisk server configured for the company '%s'.")
                    % self.company_id.name)
            else:
                ast_server = asterisk_servers[0]
        return ast_server


class PhoneCommon(models.AbstractModel):
    _inherit = 'phone.common'

    @api.model
    def click2dial(self, erp_number):
        res = super(PhoneCommon, self).click2dial(erp_number)
        if not erp_number:
            raise UserError(_('Missing phone number'))

        user, ast_server, ast_manager = \
            self.env['asterisk.server']._connect_to_asterisk()
        ast_number = self.convert_to_dial_number(erp_number)
        # Add 'out prefix'
        if ast_server.out_prefix:
            _logger.debug('Out prefix = %s', ast_server.out_prefix)
            ast_number = '%s%s' % (ast_server.out_prefix, ast_number)
        _logger.debug('Number to be sent to Asterisk = %s', ast_number)

        # The user should have a CallerID
        if not user.callerid:
            raise UserError(_('No callerID configured for the current user'))

        variable = []
        if user.asterisk_chan_type == 'SIP':
            # We can only have one alert-info header in a SIP request
            if user.alert_info:
                variable.append(
                    'SIPAddHeader=Alert-Info: %s' % user.alert_info)
            elif ast_server.alert_info:
                variable.append(
                    'SIPAddHeader=Alert-Info: %s' % ast_server.alert_info)
            if user.variable:
                for user_variable in user.variable.split('|'):
                    variable.append(user_variable.strip())
        channel = '%s/%s' % (user.asterisk_chan_type, user.resource)
        if user.dial_suffix:
            channel += '/%s' % user.dial_suffix

        try:
            ast_manager.Originate(
                channel,
                context=ast_server.context,
                extension=ast_number,
                priority=unicode(ast_server.extension_priority),
                timeout=unicode(ast_server.wait_time * 1000),
                caller_id=user.callerid,
                account=user.cdraccount,
                variable=variable)
        except Exception, e:
            _logger.error(
                "Error in the Originate request to Asterisk server %s",
                ast_server.ip_address)
            _logger.error(
                "Here are the details of the error: '%s'", unicode(e))
            raise UserError(
                _("Click to dial with Asterisk failed.\nHere is the error: "
                    "'%s'")
                % unicode(e))
        finally:
            ast_manager.Logoff()

        res['dialed_number'] = ast_number
        return res
