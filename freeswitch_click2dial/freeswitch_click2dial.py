# -*- coding: utf-8 -*-
##############################################################################
#
#    FreeSWITCH Click2dial module for OpenERP
#    Copyright (C) 2014-2016 Trever L. Adams
#    Copyright (C) 2010-2013 Alexis de Lattre <alexis@via.ecp.fr>
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

from openerp.osv import fields, orm
from openerp.tools.translate import _
import logging
# Lib for phone number reformating -> pip install phonenumbers
import phonenumbers
try:
    from freeswitchESL import ESL
except ImportError:
    import ESL
# import sys
import StringIO
import re
import json

_logger = logging.getLogger(__name__)


class freeswitch_server(orm.Model):
    '''FreeSWITCH server object, stores the parameters of the FreeSWITCH Servers'''
    _name = "freeswitch.server"
    _description = "FreeSWITCH Servers"
    _columns = {
        'name': fields.char('FreeSWITCH Server Name', size=50, required=True),
        'active': fields.boolean(
            'Active', help="The active field allows you to hide the "
            "FreeSWITCH server without deleting it."),
        'ip_address': fields.char(
            'FreeSWITCH IP address or DNS', size=50, required=True,
            help="IP address or DNS name of the FreeSWITCH server."),
        'port': fields.integer(
            'Port', required=True,
            help="TCP port on which the FreeSWITCH Event Socket listens. "
            "Defined in "
            "/etc/freeswitch/autoload_configs/event_socket.conf.xml on "
            "FreeSWITCH."),
        'out_prefix': fields.char(
            'Out Prefix', size=4, help="Prefix to dial to make outgoing "
            "calls. If you don't use a prefix to make outgoing calls, "
            "leave empty."),
        'password': fields.char(
            'Event Socket Password', size=30, required=True,
            help="Password that OpenERP will use to communicate with the "
            "FreeSWITCH Event Socket. Refer to "
            "/etc/freeswitch/autoload_configs/event_socket.conf.xml "
            "on your FreeSWITCH server."),
        'context': fields.char(
            'Dialplan Context', size=50, required=True,
            help="FreeSWITCH dialplan context from which the calls will be "
            "made; e.g. 'XML default'. Refer to /etc/freeswitch/dialplan/* "
            "on your FreeSWITCH server."),
        'wait_time': fields.integer(
            'Wait Time (sec)', required=True,
            help="Amount of time (in seconds) FreeSWITCH will try to reach "
            "the user's phone before hanging up."),
        'alert_info': fields.char(
            'Alert-Info SIP Header', size=255,
            help="Set Alert-Info header in SIP request to user's IP Phone "
            "for the click2dial feature. If empty, the Alert-Info header "
            "will not be added. You can use it to have a special ring tone "
            "for click2dial (a silent one !) or to activate auto-answer "
            "for example."),
        'company_id': fields.many2one(
            'res.company', 'Company',
            help="Company who uses the FreeSWITCH server."),
    }

    _defaults = {
        'active': True,
        'port': 8021,  # Default Event Socket port
        'context': 'XML default',
        'wait_time': 60,
        'company_id': lambda self, cr, uid, context:
        self.pool['res.company']._company_default_get(
            cr, uid, 'freeswitch.server', context=context),
    }

    def _check_validity(self, cr, uid, ids):
        for server in self.browse(cr, uid, ids):
            out_prefix = ('Out prefix', server.out_prefix)
            dialplan_context = ('Dialplan context', server.context)
            alert_info = ('Alert-Info SIP header', server.alert_info)
            password = ('Event Socket password', server.password)

            if out_prefix[1] and not out_prefix[1].isdigit():
                raise orm.except_orm(
                    _('Error:'),
                    _("Only use digits for the '%s' on the FreeSWITCH server "
                        "'%s'" % (out_prefix[0], server.name)))
            if server.wait_time < 1 or server.wait_time > 120:
                raise orm.except_orm(
                    _('Error:'),
                    _("You should set a 'Wait time' value between 1 and 120 "
                        "seconds for the FreeSWITCH server '%s'"
                        % server.name))
            if server.port > 65535 or server.port < 1:
                raise orm.except_orm(
                    _('Error:'),
                    _("You should set a TCP port between 1 and 65535 for the "
                        "FreeSWITCH server '%s'" % server.name))
            for check_str in [dialplan_context, alert_info, password]:
                if check_str[1]:
                    try:
                        check_str[1].encode('ascii')
                    except UnicodeEncodeError:
                        raise orm.except_orm(
                            _('Error:'),
                            _("The '%s' should only have ASCII caracters for "
                                "the FreeSWITCH server '%s'"
                                % (check_str[0], server.name)))
        return True

    _constraints = [(
        _check_validity,
        "Error message in raise",
        [
            'out_prefix', 'wait_time', 'port',
            'context', 'alert_info', 'password']
        )]

    def _reformat_number(
            self, cr, uid, erp_number, fs_server=None, context=None):
        '''
        This function is dedicated to the transformation of the number
        available in OpenERP to the number that FreeSWITCH should dial.
        You may have to inherit this function in another module specific
        for your company if you are not happy with the way I reformat
        the OpenERP numbers.
        '''
        assert(erp_number), 'Missing phone number'
        _logger.debug('Number before reformat = %s' % erp_number)
        if not fs_server:
            fs_server = self._get_freeswitch_server_from_user(
                cr, uid, context=context)

        # erp_number are supposed to be in E.164 format, so no need to
        # give a country code here
        parsed_num = phonenumbers.parse(erp_number, None)
        country_code = fs_server.company_id.country_id.code
        assert(country_code), 'Missing country on company'
        _logger.debug('Country code = %s' % country_code)
        to_dial_number = str(phonenumbers.format_out_of_country_calling_number(
            parsed_num, country_code.upper())).translate(None, ' -.()/')
        # Add 'out prefix' to all numbers
        if fs_server.out_prefix:
            _logger.debug('Out prefix = %s' % fs_server.out_prefix)
            to_dial_number = '%s%s' % (fs_server.out_prefix, to_dial_number)
        _logger.debug('Number to be sent to FreeSWITCH = %s' % to_dial_number)
        return to_dial_number

    def _get_freeswitch_server_from_user(self, cr, uid, context=None):
        '''Returns an freeswitch.server browse object'''
        # We check if the user has an FreeSWITCH server configured
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        if user.freeswitch_server_id.id:
            fs_server = user.freeswitch_server_id
        else:
            freeswitch_server_ids = self.search(
                cr, uid, [('company_id', '=', user.company_id.id)],
                context=context)
        # If the user doesn't have an freeswitch server,
        # we take the first one of the user's company
            if not freeswitch_server_ids:
                raise orm.except_orm(
                    _('Error:'),
                    _("No FreeSWITCH server configured for the company '%s'.")
                    % user.company_id.name)
            else:
                fs_server = self.browse(
                    cr, uid, freeswitch_server_ids[0], context=context)
        servers = self.pool.get('freeswitch.server')
        server_ids = servers.search(cr, uid, [('id', '=', fs_server.id)],
                                    context=context)
        fake_fs_server = servers.browse(cr, uid, server_ids, context=context)
        for rec in fake_fs_server:
            fs_server = rec
            break
        return fs_server

    def _connect_to_freeswitch(self, cr, uid, context=None):
        '''
        Open the connection to the FreeSWITCH Event Socket
        Returns an instance of the FreeSWITCH Event Socket

        '''
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)

        fs_server = self._get_freeswitch_server_from_user(
            cr, uid, context=context)
        # We check if the current user has a chan type
        if not user.freeswitch_chan_type:
            raise orm.except_orm(
                _('Error:'),
                _('No channel type configured for the current user.'))

        # We check if the current user has an internal number
        if not user.resource:
            raise orm.except_orm(
                _('Error:'),
                _('No resource name configured for the current user'))

        _logger.debug(
            "User's phone: %s/%s" % (user.freeswitch_chan_type, user.resource))
        _logger.debug(
            "FreeSWITCH server: %s:%d"
            % (fs_server.ip_address, fs_server.port))

        # Connect to the FreeSWITCH Event Socket
        try:
            fs_manager = ESL.ESLconnection(
                str(fs_server.ip_address),
                str(fs_server.port), str(fs_server.password))
        except Exception, e:
            _logger.error(
                "Error in the request to the FreeSWITCH Event Socket %s"
                % fs_server.ip_address)
            _logger.error("Here is the error message: %s" % e)
            raise orm.except_orm(
                _('Error:'),
                _("Problem in the request from OpenERP to FreeSWITCH. "
                  "Here is the error message: %s" % e))
            # return (False, False, False)

        return (user, fs_server, fs_manager)

    def test_es_connection(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Only 1 ID'
        fs_server = self.browse(cr, uid, ids[0], context=context)
        fs_manager = False
        try:
            fs_manager = ESL.ESLconnection(
                str(fs_server.ip_address),
                str(fs_server.port), str(fs_server.password))
        except Exception, e:
            raise orm.except_orm(
                _("Connection Test Failed!"),
                _("Here is the error message: %s" % e))
        finally:
            if fs_manager.connected() is not 1:
                raise orm.except_orm(
                    _("Connection Test Failed!"),
                    _("Check Host, Port and Password"))
            else:
                try:
                    if fs_manager:
                        fs_manager.disconnect()
                except Exception:
                    pass
                raise orm.except_orm(
                    _("Connection Test Successfull!"),
                    _("OpenERP can successfully login to the FreeSWITCH Event "
                      "Socket."))

    def _get_calling_number(self, cr, uid, context=None):

        user, fs_server, fs_manager = self._connect_to_freeswitch(
            cr, uid, context=context)
        calling_party_number = False
        try:
            is_fq_res = user.resource.rfind('@')
            if is_fq_res > 0:
                resource = user.resource[0:is_fq_res]
            else:
                resource = user.resource
            request = "channels like /" + re.sub(r'/', r':', resource) + \
                ("/" if user.freeswitch_chan_type == "FreeTDM" else "@") + \
                " as json"
            ret = fs_manager.api('show', str(request))
            f = json.load(StringIO.StringIO(ret.getBody()))
            if int(f['row_count']) > 0:
                for x in range(0, int(f['row_count'])):
                    if (is_fq_res and f['rows'][x]['presence_id'] !=
                       user.resource):
                            continue
                    if (f['rows'][x]['cid_num'] == user.internal_number or
                       len(f['rows'][x]['cid_num']) < 3):
                            calling_party_number = f['rows'][x]['dest']
                    else:
                        calling_party_number = f['rows'][x]['cid_num']
        except Exception, e:
            _logger.error(
                "Error in the Status request to FreeSWITCH server %s"
                % fs_server.ip_address)
            _logger.error(
                "Here are the details of the error: '%s'" % unicode(e))
            raise orm.except_orm(
                _('Error:'),
                _("Can't get calling number from FreeSWITCH.\nHere is the "
                    "error: '%s'" % unicode(e)))
        finally:
            fs_manager.disconnect()

        _logger.debug("Calling party number: '%s'" % calling_party_number)
        if isinstance(calling_party_number, int):
            return calling_party_number
        else:
            return False

    def get_record_from_my_channel(self, cr, uid, context=None):
        calling_number = self.pool['freeswitch.server']._get_calling_number(
            cr, uid, context=context)
        # calling_number = "0641981246"
        if calling_number:
            record = self.pool['phone.common'].get_record_from_phone_number(
                cr, uid, calling_number, context=context)
            if record:
                return record
            else:
                return calling_number
        else:
            return False


class res_users(orm.Model):
    _inherit = "res.users"

    _columns = {
        'internal_number': fields.char(
            'Internal Number', size=15,
            help="User's internal phone number."),
        'dial_suffix': fields.char(
            'User-specific Dial Suffix', size=15,
            help="User-specific dial suffix such as aa=2wb for SCCP "
            "auto answer."),
        'callerid': fields.char(
            'Caller ID', size=50,
            help="Caller ID used for the calls initiated by this user. "
            "This must be in the form of 'Name <NUMBER>'."),
        'cdraccount': fields.char(
            'CDR Account', size=50,
            help="Call Detail Record (CDR) account used for billing this "
            "user."),
        'freeswitch_chan_type': fields.selection([
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
            ], 'FreeSWITCH Channel Type',
            help="FreeSWITCH channel type, as used in the FreeSWITCH "
            "dialplan. If the user has a regular IP phone, the channel type "
            "is 'SIP'. Use Verto for verto.rtc connections only if you "
            "haven't added '${verto_contact ${dialed_user}@${dialed_domain}}' "
            "to the default dial string. Otherwise, use SIP. (This better "
            "allows for changes to the user directory and changes in type of "
            "phone without the need for further changes in OpenERP/Odoo.)"),
        'resource': fields.char(
            'Resource Name', size=64,
            help="Resource name for the channel type selected. For example, "
            "if you use 'user/phone1' in your FreeSWITCH dialplan to ring "
            "the SIP phone of this user, then the resource name for this user "
            "is 'phone1'.  For a SIP phone, the phone number is often used as "
            "resource name, but not always. FreeTDM will be the span followed "
            "by the port (i.e. 1/5)."),
        'alert_info': fields.char(
            'User-specific Alert-Info SIP Header', size=255,
            help="Set a user-specific Alert-Info header in SIP request to "
            "user's IP Phone for the click2dial feature. If empty, the "
            "Alert-Info header will not be added. You can use it to have a "
            "special ring tone for click2dial (a silent one !) or to "
            "activate auto-answer for example."),
        'variable': fields.char(
            'User-specific Variable', size=255,
            help="Set a user-specific 'Variable' field in the FreeSWITCH "
            "Event Socket 'originate' request for the click2dial "
            "feature. If you want to have several variable headers, separate "
            "them with '|'."),
        'freeswitch_server_id': fields.many2one(
            'freeswitch.server', 'FreeSWITCH Server',
            help="FreeSWITCH server on which the user's phone is connected. "
            "If you leave this field empty, it will use the first FreeSWITCH "
            "server of the user's company."),
        }

    _defaults = {
        'freeswitch_chan_type': 'user',
    }

    def _check_validity(self, cr, uid, ids):
        for user in self.browse(cr, uid, ids):
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
                        raise orm.except_orm(
                            _('Error:'),
                            _("The '%s' for the user '%s' should only have "
                                "ASCII characters")
                            % (check_string[0], user.name))
        return True

    _constraints = [(
        _check_validity,
        "Error message in raise",
        ['resource', 'internal_number', 'callerid']
        )]


class phone_common(orm.AbstractModel):
    _inherit = 'phone.common'

    def click2dial(self, cr, uid, erp_number, context=None):
        if not erp_number:
            orm.except_orm(
                _('Error:'),
                _('Missing phone number'))

        user, fs_server, fs_manager = \
            self.pool['freeswitch.server']._connect_to_freeswitch(
                cr, uid, context=context)
        fs_number = self.pool['freeswitch.server']._reformat_number(
            cr, uid, erp_number, fs_server, context=context)

        # The user should have a CallerID
        if not user.callerid:
            raise orm.except_orm(
                _('Error:'),
                _('No callerID configured for the current user'))

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
                variable += 'effective_caller_id_number=\'' + \
                    caller_number + '\''
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
                '\'' + self.get_name_from_phone_number(cr, uid, fs_number) + \
                '\' ' + fs_number
            # raise orm.except_orm(_('Error :'), dial_string)
            fs_manager.api('originate', dial_string.encode('utf-8'))
        except Exception, e:
            _logger.error(
                "Error in the Originate request to FreeSWITCH server %s"
                % fs_server.ip_address)
            _logger.error(
                "Here are the details of the error: '%s'" % unicode(e))
            raise orm.except_orm(
                _('Error:'),
                _("Click to dial with FreeSWITCH failed.\nHere is the error: "
                    "'%s'")
                % unicode(e))
        finally:
            fs_manager.disconnect()

        return {'dialed_number': fs_number}
