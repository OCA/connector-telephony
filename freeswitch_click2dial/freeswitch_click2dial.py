# -*- coding: utf-8 -*-
# © 2010-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# © 2014-2016 Trever L. Adams
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import models, fields, api, _
from openerp.exceptions import UserError, ValidationError
import logging
# from pprint import pformat
try:
    from freeswitchESL import ESL
except ImportError:
    import ESL
# import sys
import StringIO
import re
import json

_logger = logging.getLogger(__name__)


class FreeSWITCHServer(models.Model):
    '''FreeSWITCH server object, stores the parameters of the FreeSWITCH Servers'''
    _name = "freeswitch.server"
    _description = "FreeSWITCH Servers"
    name = fields.Char(string='FreeSWITCH Server Name', required=True)
    active = fields.Boolean(
        string='Active', help="The active field allows you to hide the "
        "FreeSWITCH server without deleting it.", default=True)
    ip_address = fields.Char(
        string='FreeSWITCH IP address or DNS', required=True,
        help="IP address or DNS name of the FreeSWITCH server.")
    port = fields.Integer(
        string='Port', required=True, default=8021,
        help="TCP port on which the FreeSWITCH Event Socket listens. "
        "Defined in "
        "/etc/freeswitch/autoload_configs/event_socket.conf.xml on "
        "FreeSWITCH.")
    out_prefix = fields.Char(
        string='Out Prefix', size=4, help="Prefix to dial to make outgoing "
        "calls. If you don't use a prefix to make outgoing calls, "
        "leave empty.")
    password = fields.Char(
        string='Event Socket Password', required=True,
        help="Password that OpenERP will use to communicate with the "
        "FreeSWITCH Event Socket. Refer to "
        "/etc/freeswitch/autoload_configs/event_socket.conf.xml "
        "on your FreeSWITCH server.")
    context = fields.Char(
        string='Dialplan Context', required=True, default="XML default",
        help="FreeSWITCH dialplan context from which the calls will be "
        "made; e.g. 'XML default'. Refer to /etc/freeswitch/dialplan/* "
        "on your FreeSWITCH server.")
    wait_time = fields.Integer(
        string='Wait Time (sec)', required=True,
        help="Amount of time (in seconds) FreeSWITCH will try to reach "
        "the user's phone before hanging up.", default=60)
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
            'freeswitch.server'),
        help="Company who uses the FreeSWITCH server.")

    @api.multi
    @api.constrains(
        'out_prefix', 'wait_time', 'port', 'context', 'alert_info', 'password')
    def _check_validity(self):
        for server in self:
            out_prefix = ('Out prefix', server.out_prefix)
            dialplan_context = ('Dialplan context', server.context)
            alert_info = ('Alert-Info SIP header', server.alert_info)
            password = ('Event Socket password', server.password)

            if out_prefix[1] and not out_prefix[1].isdigit():
                raise ValidationError(
                    _("Only use digits for the '%s' on the FreeSWITCH server "
                        "'%s'" % (out_prefix[0], server.name)))
            if server.wait_time < 1 or server.wait_time > 120:
                raise ValidationError(
                    _("You should set a 'Wait time' value between 1 and 120 "
                        "seconds for the FreeSWITCH server '%s'"
                        % server.name))
            if server.port > 65535 or server.port < 1:
                raise ValidationError(
                    _("You should set a TCP port between 1 and 65535 for the "
                        "FreeSWITCH server '%s'" % server.name))
            for check_str in [dialplan_context, alert_info, password]:
                if check_str[1]:
                    try:
                        check_str[1].encode('ascii')
                    except UnicodeEncodeError:
                        raise ValidationError(
                            _("The '%s' should only have ASCII characters for "
                                "the FreeSWITCH server '%s'"
                                % (check_str[0], server.name)))

    @api.model
    def _connect_to_freeswitch(self):
        '''
        Open the connection to the FreeSWITCH Event Socket
        Returns an instance of the FreeSWITCH Event Socket

        '''
        user = self.env.user

        fs_server = user.get_freeswitch_server_from_user()
        # We check if the current user has a chan type
        if not user.freeswitch_chan_type:
            raise UserError(
                _('No channel type configured for the current user.'))

        # We check if the current user has an internal number
        if not user.resource:
            raise UserError(
                _('No resource name configured for the current user'))

        _logger.debug(
            "User's phone: %s/%s", user.freeswitch_chan_type, user.resource)
        _logger.debug(
            "FreeSWITCH server: %s:%d", fs_server.ip_address, fs_server.port)

        # Connect to the FreeSWITCH Event Socket
        try:
            fs_manager = ESL.ESLconnection(
                str(fs_server.ip_address),
                str(fs_server.port), str(fs_server.password))
        except Exception, e:
            _logger.error(
                "Error in the request to the FreeSWITCH Event Socket %s",
                fs_server.ip_address)
            _logger.error("Here is the error message: %s", e)
            raise UserError(
                _("Problem in the request from Odoo to FreeSWITCH. "
                  "Here is the error message: %s" % e))
            # return (False, False, False)

        return (user, fs_server, fs_manager)

    @api.multi
    def test_es_connection(self):
        self.ensure_one()
        fs_manager = False
        try:
            fs_manager = ESL.ESLconnection(
                str(self.ip_address),
                str(self.port), str(self.password))
        except Exception, e:
            raise UserError(
                _("Connection Test Failed! The error message is: %s" % e))
        finally:
            try:
                if fs_manager.connected() is not 1:
                    raise UserError(
                        _("Connection Test Failed! Check Host, Port and "
                          "Password"))
                else:
                    fs_manager.disconnect()
            except Exception, e:
                pass
        raise UserError(_(
            "Connection Test Successfull! Odoo can successfully login to "
            "the FreeSWITCH Event Socket."))

    @api.model
    def _get_calling_number(self):
        user, fs_server, fs_manager = self._connect_to_freeswitch()
        calling_party_number = False
        try:
            is_fq_res = user.resource.rfind('@')
            if is_fq_res:
                if len(user.resource) != is_fq_res:
                    is_fq_res = True
                else:
                    is_fq_res = False
            request = "channels like /" + re.sub(r'/', r':', user.resource) + \
                (("/" if user.freeswitch_chan_type == "FreeTDM" else "@")
                 if not is_fq_res else "") + " as json"
            ret = fs_manager.api('show', str(request))
            f = json.load(StringIO.StringIO(ret.getBody()))
            if int(f['row_count']) > 0:
                if (f['rows'][0]['cid_num'] == user.internal_number or
                    len(f['rows'][0]['cid_num']) < 3):
                        calling_party_number = f['rows'][0]['dest']
                else:
                    calling_party_number = f['rows'][0]['cid_num']
        except Exception, e:
            _logger.error(
                "Error in the Status request to FreeSWITCH server %s",
                fs_server.ip_address)
            _logger.error(
                "Here are the details of the error: '%s'" % unicode(e))
            raise UserError(
                _("Can't get calling number from FreeSWITCH.\nHere is the "
                    "error: '%s'" % unicode(e)))

        finally:
            fs_manager.disconnect()

        _logger.debug("Calling party number: '%s'", calling_party_number)
        return calling_party_number

    @api.model
    def get_record_from_my_channel(self):
        calling_number = self.env['freeswitch.server']._get_calling_number()
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
        string='Internal Number',
        help="User's internal phone number.")
    dial_suffix = fields.Char(
        string='User-specific Dial Suffix',
        help="User-specific dial suffix such as aa=2wb for SCCP "
        "auto answer.")
    callerid = fields.Char(
        string='Caller ID', copy=False,
        help="Caller ID used for the calls initiated by this user. "
        "This must be in the form of 'Name <NUMBER>'.")
    cdraccount = fields.Char(
        string='CDR Account',
        help="Call Detail Record (CDR) account used for billing this "
        "user.")
    freeswitch_chan_type = fields.Selection([
        ('user', 'SIP'),
        ('FreeTDM', 'FreeTDM'),
        ('verto.rtc', 'Verto'),
        ('skinny', 'Skinny'),
        ('h323', 'H323'),
        ('dingaling', 'XMPP/JINGLE'),
        ('gsmopen', 'GSM SMS/Voice'),
        ('skypeopen', 'SkypeOpen'),
        ('Khomp', 'Khomp'),
        ('opal', 'Opal Multi-protocol'),
        ('portaudio', 'Portaudio'),
        ], string='FreeSWITCH Channel Type', default='user',
        help="FreeSWITCH channel type, as used in the FreeSWITCH "
        "dialplan. If the user has a regular IP phone, the channel type "
        "is 'SIP'. Use Verto for verto.rtc connections only if you "
        "haven't added '${verto_contact ${dialed_user}@${dialed_domain}}' "
        "to the default dial string. Otherwise, use SIP. (This better "
        "allows for changes to the user directory and changes in type of "
        "phone without the need for further changes in OpenERP/Odoo.)")
    resource = fields.Char(
        string='Resource Name',
        help="Resource name for the channel type selected. For example, "
        "if you use 'user/phone1' in your FreeSWITCH dialplan to ring "
        "the SIP phone of this user, then the resource name for this user "
        "is 'phone1'.  For a SIP phone, the phone number is often used as "
        "resource name, but not always. FreeTDM will be the span followed "
        "by the port (i.e. 1/5).")
    alert_info = fields.Char(
        string='User-specific Alert-Info SIP Header',
        help="Set a user-specific Alert-Info header in SIP request to "
        "user's IP Phone for the click2dial feature. If empty, the "
        "Alert-Info header will not be added. You can use it to have a "
        "special ring tone for click2dial (a silent one !) or to "
        "activate auto-answer for example.")
    variable = fields.Char(
        string='User-specific Variable',
        help="Set a user-specific 'Variable' field in the FreeSWITCH "
        "Event Socket 'originate' request for the click2dial "
        "feature. If you want to have several variable headers, separate "
        "them with '|'.")
    freeswitch_server_id = fields.Many2one(
        'freeswitch.server', string='FreeSWITCH Server',
        help="FreeSWITCH server on which the user's phone is connected. "
        "If you leave this field empty, it will use the first FreeSWITCH "
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
                            "ASCII caracters"),
                            check_string[0], user.name)

    @api.multi
    def get_freeswitch_server_from_user(self):
        '''Returns an freeswitch.server recordset'''
        self.ensure_one()
        # We check if the user has an FreeSWITCH server configured
        if self.freeswitch_server_id.id:
            fs_server = self.freeswitch_server_id
        else:
            freeswitch_servers = self.env['freeswitch.server'].search(
                [('company_id', '=', self.company_id.id)])
        # If the user doesn't have an FreeSWITCH server,
        # we take the first one of the user's company
            if not freeswitch_servers:
                raise UserError(
                    _("No FreeSWITCH server configured for the company '%s'.")
                    % self.company_id.name)
            else:
                fs_server = freeswitch_servers[0]
        return fs_server


class PhoneCommon(models.AbstractModel):
    _inherit = 'phone.common'

    @api.model
    def click2dial(self, erp_number):
        res = super(PhoneCommon, self).click2dial(erp_number)
        if not erp_number:
            raise UserError(_('Missing phone number'))

        user, fs_server, fs_manager = \
            self.env['freeswitch.server']._connect_to_freeswitch()
        fs_number = self.convert_to_dial_number(erp_number)
        # Add 'out prefix'
        if fs_server.out_prefix:
            _logger.debug('Out prefix = %s', fs_server.out_prefix)
            fs_number = '%s%s' % (fs_server.out_prefix, fs_number)
        _logger.debug('Number to be sent to FreeSWITCH = %s', fs_number)

        # The user should have a CallerID
        if not user.callerid:
            raise UserError(_('No callerID configured for the current user'))

        variable = ""
        if user.freeswitch_chan_type == 'user':
            # We can only have one alert-info header in a SIP request
            if user.alert_info:
                variable += 'alert_info=' + user.alert_info
            elif fs_server.alert_info:
                variable += 'alert_info=' + fs_server.alert_info
            if user.variable:
                for user_variable in user.variable.split('|'):
                    if len(variable) and len(user_variable):
                        variable += ','
                    variable += user_variable.strip()
        if user.callerid:
            caller_name = re.search(r'([^<]*).*',
                                    user.callerid).group(1).strip()
            caller_number = re.search(r'.*<(.*)>.*',
                                      user.callerid).group(1).strip()
            if caller_name:
                if len(variable):
                    variable += ','
                caller_name = caller_name.replace(",", r"\,")
                variable += 'effective_caller_id_name=\'' + caller_name + '\''
            if caller_number:
                if len(variable):
                    variable += ','
                variable += 'effective_caller_id_number=\'' + caller_number + '\''
            if fs_server.wait_time != 60:
                if len(variable):
                    variable += ','
                variable += 'ignore_early_media=true' + ','
                variable += 'originate_timeout=' + str(fs_server.wait_time)
        if len(variable):
            variable += ','
        variable += 'odoo_connector=true'
        channel = '%s/%s' % (user.freeswitch_chan_type, user.resource)
        if user.dial_suffix:
            channel += '/%s' % user.dial_suffix

        try:
            # originate <csv global vars>user/2005 1005 DP_TYPE DP_NAME
            #    'Caller ID name showed to aleg' 90125
            dial_string = (('<' + variable + '>') if variable else '') + \
                channel + ' ' + fs_number + ' ' + fs_server.context + ' ' + \
                '\'' + self.get_name_from_phone_number(fs_number) + '\' ' + \
                fs_number
            # raise orm.except_orm(_('Error :'), dial_string)
            fs_manager.api('originate', dial_string.encode('utf-8'))
        except Exception, e:
            _logger.error(
                "Error in the Originate request to FreeSWITCH server %s",
                fs_server.ip_address)
            _logger.error(
                "Here are the details of the error: '%s'", unicode(e))
            raise UserError(
                _("Click to dial with FreeSWITCH failed.\nHere is the error: "
                    "'%s'")
                % unicode(e))
        finally:
            fs_manager.disconnect()

        res['dialed_number'] = fs_number
        return res
