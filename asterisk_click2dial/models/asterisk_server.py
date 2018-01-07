# -*- coding: utf-8 -*-
# © 2010-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from pprint import pformat
import logging
_logger = logging.getLogger(__name__)

try:
    # pip install py-Asterisk
    from Asterisk import Manager
except ImportError:
    _logger.debug('Cannot import Asterisk')
    Manager = None


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
        except Exception as e:
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
        except Exception as e:
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
            for chan in list(list_chan.values()):
                calling_party_number = self._get_calling_number_from_channel(
                    chan, user)
                if calling_party_number:
                    break
        except Exception as e:
            _logger.error(
                "Error in the Status request to Asterisk server %s",
                ast_server.ip_address)
            _logger.error(
                "Here are the details of the error: '%s'", str(e))
            raise UserError(
                _("Can't get calling number from  Asterisk.\nHere is the "
                    "error: '%s'" % str(e)))

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
