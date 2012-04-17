# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk Click2dial module for OpenERP
#    Copyright (C) 2010-2012 Alexis de Lattre <alexis@via.ecp.fr>
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

from osv import osv, fields
# Lib required to open a socket (needed to communicate with Asterisk server)
import socket
# Lib required to print logs
import logging
# Lib to translate error messages
from tools.translate import _
# Lib for regexp
import re

_logger = logging.getLogger(__name__)

class asterisk_server(osv.osv):
    '''Asterisk server object, to store all the parameters of the Asterisk IPBXs'''
    _name = "asterisk.server"
    _description = "Asterisk Servers"
    _columns = {
        'name': fields.char('Asterisk server name', size=50, required=True, help="Asterisk server name."),
        'active': fields.boolean('Active', help="The active field allows you to hide the Asterisk server without deleting it."),
        'ip_address': fields.char('Asterisk IP addr. or DNS', size=50, required=True, help="IP address or DNS name of the Asterisk server."),
        'port': fields.integer('Port', required=True, help="TCP port on which the Asterisk Manager Interface listens. Defined in /etc/asterisk/manager.conf on Asterisk."),
        'out_prefix': fields.char('Out prefix', size=4, help="Prefix to dial to place outgoing calls. If you don't use a prefix to place outgoing calls, leave empty."),
        'national_prefix': fields.char('National prefix', size=4, help="Prefix for national phone calls (don't include the 'out prefix'). For e.g., in France, the phone numbers look like '01 41 98 12 42' : the National prefix is '0'."),
        'international_prefix': fields.char('International prefix', required=True, size=4, help="Prefix to add to make international phone calls (don't include the 'out prefix'). For e.g., in France, the International prefix is '00'."),
        'country_prefix': fields.char('My country prefix', required=True, size=4, help="Phone prefix of the country where the Asterisk server is located. For e.g. the phone prefix for France is '33'. If the phone number to dial starts with the 'My country prefix', OpenERP will remove the country prefix from the phone number and add the 'out prefix' followed by the 'national prefix'. If the phone number to dial doesn't start with the 'My country prefix', OpenERP will add the 'out prefix' followed by the 'international prefix'."),
        'national_format_allowed': fields.boolean('National format allowed ?', help="Do we allow to use click2dial on phone numbers written in national format, e.g. 01 41 98 12 42, or only in the international format, e.g. +33 1 41 98 12 42 ?"),
        'login': fields.char('AMI login', size=30, required=True, help="Login that OpenERP will use to communicate with the Asterisk Manager Interface. Refer to /etc/asterisk/manager.conf on your Asterisk server."),
        'password': fields.char('AMI password', size=30, required=True, help="Password that Asterisk will use to communicate with the Asterisk Manager Interface. Refer to /etc/asterisk/manager.conf on your Asterisk server."),
        'context': fields.char('Dialplan context', size=50, required=True, help="Asterisk dialplan context from which the calls will be made. Refer to /etc/asterisk/extensions.conf on your Asterisk server."),
        'wait_time': fields.integer('Wait time (sec)', required=True, help="Amount of time (in seconds) Asterisk will try to reach the user's phone before hanging up."),
        'extension_priority': fields.integer('Extension priority', required=True, help="Priority of the extension in the Asterisk dialplan. Refer to /etc/asterisk/extensions.conf on your Asterisk server."),
        'alert_info': fields.char('Alert-Info SIP header', size=40, help="Set Alert-Info header in SIP request to user's IP Phone. If empty, the Alert-Info header will not be added. You can use it to have a special ring tone for click2dial, for example you could choose a silent ring tone."),
        'company_id': fields.many2one('res.company', 'Company', help="Company who uses the Asterisk server."),
    }

    _defaults = {
        'active': lambda *a: 1,
        'port': lambda *a: 5038,  # Default AMI port
        'out_prefix': lambda *a: '0',
        'national_prefix': lambda *a: '0',
        'international_prefix': lambda *a: '00',
        'extension_priority': lambda *a: 1,
        'wait_time': lambda *a: 15,
    }

    def _check_validity(self, cr, uid, ids):
        for server in self.browse(cr, uid, ids):
            country_prefix = ('Country prefix', server.country_prefix)
            international_prefix = ('International prefix', server.international_prefix)
            out_prefix = ('Out prefix', server.out_prefix)
            national_prefix = ('National prefix', server.national_prefix)
            dialplan_context = ('Dialplan context', server.context)
            alert_info = ('Alert-Info SIP header', server.alert_info)
            login = ('AMI login', server.login)
            password = ('AMI password', server.password)

            for digit_prefix in [country_prefix, international_prefix, out_prefix, national_prefix]:
                if digit_prefix[1] and not digit_prefix[1].isdigit():
                    raise osv.except_osv(_('Error :'), _("Only use digits for the '%s' on the Asterisk server '%s'" % (digit_prefix[0], server.name)))
            if server.wait_time < 1 or server.wait_time > 120:
                raise osv.except_osv(_('Error :'), _("You should set a 'Wait time' value between 1 and 120 seconds for the Asterisk server '%s'" % server.name))
            if server.extension_priority < 1:
                raise osv.except_osv(_('Error :'), _("The 'extension priority' must be a positive value for the Asterisk server '%s'" % server.name))
            if server.port > 65535 or server.port < 1:
                raise osv.except_osv(_('Error :'), _("You should set a TCP port between 1 and 65535 for the Asterik server '%s'" % server.name))
            for check_string in [dialplan_context, alert_info, login, password]:
                if check_string[1]:
                    try:
                        string = check_string[1].encode('ascii')
                    except UnicodeEncodeError:
                        raise osv.except_osv(_('Error :'), _("The '%s' should only have ASCII caracters for the Asterisk server '%s'" % (check_string[0], server.name)))
        return True


    _constraints = [
        (_check_validity, "Error message in raise", ['out_prefix', 'country_prefix', 'national_prefix', 'international_prefix', 'wait_time', 'extension_priority', 'port', 'context', 'alert_info', 'login', 'password']),
    ]


    def reformat_number(self, cr, uid, ids, erp_number, ast_server, context=None):
        '''
        This function is dedicated to the transformation of the number
        available in OpenERP to the number that Asterisk should dial.
        You may have to inherit this function in another module specific
        for your company if you are not happy with the way I reformat
        the OpenERP numbers.
        '''

        error_title_msg = _("Invalid phone number")
        invalid_international_format_msg = _("The phone number is not written in valid international format. Example of valid international format : +33 1 41 98 12 42")
        invalid_national_format_msg = _("The phone number is not written in valid national format.")
        invalid_format_msg = _("The phone number is not written in valid format.")

        # Let's call the variable tmp_number now
        tmp_number = erp_number
        _logger.debug('Number before reformat = %s' % tmp_number)

        # Check if empty
        if not tmp_number:
            raise osv.except_osv(error_title_msg, invalid_format_msg)

        # First, we remove all stupid caracters and spaces
        for char_to_remove in [' ', '.', '(', ')', '[', ']', '-', '/']:
            tmp_number = tmp_number.replace(char_to_remove, '')

        # Before starting to use prefix, we convert empty prefix whose value
        # is False to an empty string
        country_prefix = (ast_server.country_prefix or '')
        national_prefix = (ast_server.national_prefix or '')
        international_prefix = (ast_server.international_prefix or '')
        out_prefix = (ast_server.out_prefix or '')

        # International format
        if tmp_number[0] == '+':
            # Remove the starting '+' of the number
            tmp_number = tmp_number.replace('+','')
            _logger.debug('Number after removal of special char = %s' % tmp_number)

            # At this stage, 'tmp_number' should only contain digits
            if not tmp_number.isdigit():
                raise osv.except_osv(error_title_msg, invalid_format_msg)

            _logger.debug('Country prefix = %s' % country_prefix)
            if country_prefix == tmp_number[0:len(country_prefix)]:
                # If the number is a national number,
                # remove 'my country prefix' and add 'national prefix'
                tmp_number = (national_prefix) + tmp_number[len(country_prefix):len(tmp_number)]
                _logger.debug('National prefix = %s - Number with national prefix = %s' % (national_prefix, tmp_number))

            else:
                # If the number is an international number,
                # add 'international prefix'
                tmp_number = international_prefix + tmp_number
                _logger.debug('International prefix = %s - Number with international prefix = %s' % (international_prefix, tmp_number))

        # National format, allowed
        elif ast_server.national_format_allowed:
            # No treatment required
            if not tmp_number.isdigit():
                raise osv.except_osv(error_title_msg, invalid_national_format_msg)

        # National format, disallowed
        elif not ast_server.national_format_allowed:
            raise osv.except_osv(error_title_msg, invalid_international_format_msg)

        # Add 'out prefix' to all numbers
        tmp_number = out_prefix + tmp_number
        _logger.debug('Out prefix = %s - Number to be sent to Asterisk = %s' % (out_prefix, tmp_number))
        return tmp_number


    def _parse_asterisk_answer(self, cr, uid, sock, context=None):
        '''Parse the answer of the Asterisk Manager Interface'''
        answer = ''
        data = ''
        while '\r\n\r\n' not in data:
            data = sock.recv(1024)
            if data:
                answer += data
        return answer
 

    def dial(self, cr, uid, ids, erp_number, context=None):
        '''
        Open the socket to the Asterisk Manager Interface (AMI)
        and send instructions to Dial to Asterisk. That's the important function !

        '''
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)

        # Check if the number to dial is not empty
        if not erp_number:
            raise osv.except_osv(_('Error :'), _('There is no phone number !'))
        # Note : if I write 'Error' without ' :', it won't get translated...
        # I don't understand why !

        # We check if the user has an Asterisk server configured
        if user.asterisk_server_id.id:
            ast_server = user.asterisk_server_id
        else:
            asterisk_server_ids = self.search(cr, uid, [('company_id', '=', user.company_id.id)], context=context)
        # If no asterisk server is configured on the user, we take the first one
            if not asterisk_server_ids:
                raise osv.except_osv(_('Error :'), _("No Asterisk server configured for the company '%s'.") % user.company_id.name)
            else:
                ast_server = self.browse(cr, uid, asterisk_server_ids[0], context=context)

        # We check if the current user has a chan type
        if not user.asterisk_chan_type:
            raise osv.except_osv(_('Error :'), _('No channel type configured for the current user.'))

        # We check if the current user has an internal number
        if not user.internal_number:
            raise osv.except_osv(_('Error :'), _('No internal phone number configured for the current user'))

        # The user should also have a CallerID
        if not user.callerid:
            raise osv.except_osv(_('Error :'), _('No callerID configured for the current user'))

        # Convert the phone number in the format that will be sent to Asterisk
        ast_number = self.reformat_number(cr, uid, ids, erp_number, ast_server, context=context)
        _logger.debug("User dialing : channel = %s/%s - Callerid = %s" % (user.asterisk_chan_type, user.internal_number, user.callerid))
        _logger.debug("Asterisk server = %s:%d" % (ast_server.ip_address, ast_server.port))

        # Connect to the Asterisk Manager Interface, using IPv6-ready code
        try:
            res = socket.getaddrinfo(str(ast_server.ip_address), ast_server.port, socket.AF_UNSPEC, socket.SOCK_STREAM)
        except:
            _logger.warning("Can't resolve the DNS of the Asterisk server '%s'" % ast_server.ip_address)
            raise osv.except_osv(_('Error :'), _("Can't resolve the DNS of the Asterisk server : '%s'" % ast_server.ip_address))
        for result in res:
            af, socktype, proto, canonname, sockaddr = result
            sock = socket.socket(af, socktype, proto)
            try:
                sock.connect(sockaddr)
                header_received = sock.recv(1024)
                _logger.debug('Header received from Asterisk : %s' % header_received)

                # Login to Asterisk
                login_act = 'Action: login\r\n' + \
                    'Events: off\r\n' + \
                    'Username: ' + ast_server.login + '\r\n' + \
                    'Secret: ' + ast_server.password + '\r\n\r\n'
                sock.send(login_act.encode('ascii'))
                login_answer = self._parse_asterisk_answer(cr, uid, sock, context=context)
                if 'Response: Success' in login_answer:
                    _logger.debug("Successful authentification to Asterisk : %s" % login_answer)
                else:
                    raise osv.except_osv(_('Error :'), _("Authentification to Asterisk failed :\n%s" % login_answer))

                # Dial with Asterisk
                originate_act = 'Action: originate\r\n' + \
                    'Channel: ' + user.asterisk_chan_type + '/' + user.internal_number + '\r\n' + \
                    'Priority: ' + str(ast_server.extension_priority) + '\r\n' + \
                    'Timeout: ' + str(ast_server.wait_time*1000) + '\r\n' + \
                    'CallerId: ' + user.callerid + '\r\n' + \
                    'Exten: ' + ast_number + '\r\n' + \
                    'Context: ' + ast_server.context + '\r\n'
                if ast_server.alert_info and user.asterisk_chan_type == 'SIP':
                    originate_act += 'Variable: SIPAddHeader=Alert-Info: ' + ast_server.alert_info + '\r\n'
                originate_act += '\r\n'
                sock.send(originate_act.encode('ascii'))
                originate_answer = self._parse_asterisk_answer(cr, uid, sock, context=context)
                if 'Response: Success' in originate_answer:
                    _logger.debug('Successfull originate command : %s' % originate_answer)
                else:
                    raise osv.except_osv(_('Error :'), _("Click to dial with Asterisk failed :\n%s" % originate_answer))

                # Logout of Asterisk
                sock.send(('Action: Logoff\r\n\r\n').encode('ascii'))
                logout_answer = self._parse_asterisk_answer(cr, uid, sock, context=context)
                if 'Response: Goodbye' in logout_answer:
                    _logger.debug('Successfull logout from Asterisk : %s' % logout_answer)
                else:
                    _logger.warning('Logout from Asterisk failed : %s' % logout_answer)
            # we catch only network problems here
            except socket.error:
                _logger.warning("Click2dial failed : unable to connect to Asterisk")
                raise osv.except_osv(_('Error :'), _("The connection from OpenERP to the Asterisk server failed. Please check the configuration on OpenERP and on Asterisk."))
            finally:
                sock.close()
            _logger.info("Asterisk Click2Dial from %s/%s to %s" % (user.asterisk_chan_type, user.internal_number, ast_number))

        return True

asterisk_server()


# Parameters specific for each user
class res_users(osv.osv):
    _name = "res.users"
    _inherit = "res.users"
    _columns = {
        'internal_number': fields.char('Internal number', size=15,
            help="User's internal phone number."),
        'callerid': fields.char('Caller ID', size=50,
            help="Caller ID used for the calls initiated by this user."),
        'asterisk_chan_type': fields.selection([
            ('SIP', 'SIP'),
            ('IAX2', 'IAX2'),
            ('DAHDI', 'DAHDI'),
            ('Zap', 'Zap'),
            ('Skinny', 'Skinny'),
            ('MGCP', 'MGCP'),
            ('mISDN', 'mISDN'),
            ('H323', 'H323'),
            ], 'Asterisk channel type',
            help="Asterisk channel type, as used in the Asterisk dialplan. If the user has a regular IP phone, the channel type is 'SIP'."),
        'asterisk_server_id': fields.many2one('asterisk.server', 'Asterisk server',
            help="Asterisk server on which the user's phone is connected. If you leave this field empty, it will use the first Asterisk server of the user's company."),
               }

    _defaults = {
        'asterisk_chan_type': lambda *a: 'SIP',
    }

    def _check_validity(self, cr, uid, ids):
        for user in self.browse(cr, uid, ids):
            for check_string in [('Internal number', user.internal_number), ('Caller ID', user.callerid)]:
                try:
                    plom = check_string[1].encode('ascii')
                except UnicodeEncodeError:
                    raise osv.except_osv(_('Error :'), _("The '%s' for the user '%s' should only have ASCII caracters" % (check_string[0], user.name)))
        return True

    _constraints = [
        (_check_validity, "Error message in raise", ['internal_number', 'callerid']),
    ]

res_users()


class res_partner_address(osv.osv):
    _name = "res.partner.address"
    _inherit = "res.partner.address"

    def action_dial_phone(self, cr, uid, ids, context=None):
        '''Function called by the button 'Dial' next to the 'phone' field
        in the partner address view'''
        erp_number = self.read(cr, uid, ids, ['phone'], context=context)[0]['phone']
        return self.pool.get('asterisk.server').dial(cr, uid, ids, erp_number, context=context)

    def action_dial_mobile(self, cr, uid, ids, context=None):
        '''Function called by the button 'Dial' next to the 'mobile' field
        in the partner address view'''
        erp_number = self.read(cr, uid, ids, ['mobile'], context=context)[0]['mobile']
        return self.pool.get('asterisk.server').dial(cr, uid, ids, erp_number, context=context)

    def get_name_from_phone_number(self, cr, uid, number, context=None):
        '''Function to get name from phone number. Usefull for use from Asterisk
        to add CallerID name to incoming calls.
        The "scripts/" subdirectory of this module has an AGI script that you can
        install on your Asterisk IPBX : the script will be called from the Asterisk
        dialplan via the AGI() function and it will use this function via an XML-RPC
        request.
        '''
        res = {}
        # We check that "number" is really a number
        if not isinstance(number, str):
            return False
        if not number.isdigit():
            return False

        _logger.debug(u"Call get_name_from_phone_number with number = %s" % number)
        # Get all the partner addresses :
        all_ids = self.search(cr, uid, [], context=context)
        # For each partner address, we check if the number matches on the "phone" or "mobile" fields
        for entry in self.browse(cr, uid, all_ids, context=context):
            if entry.phone:
                # We use a regexp on the phone field to remove non-digit caracters
                if re.sub(r'\D', '', entry.phone).endswith(number):
                    _logger.debug(u"Answer get_name_from_phone_number with name = %s" % entry.name)
                    return entry.name
            if entry.mobile:
                if re.sub(r'\D', '', entry.mobile).endswith(number):
                    _logger.debug(u"Answer get_name_from_phone_number with name = %s" % entry.name)
                    return entry.name

        _logger.debug(u"No match for phone number %s" % number)
        return False

res_partner_address()


# This module supports multi-company
class res_company(osv.osv):
    _name = "res.company"
    _inherit = "res.company"
    _columns = {
        'asterisk_server_ids': fields.one2many('asterisk.server', 'company_id', 'Asterisk servers', help="List of Asterisk servers.")
    }

res_company()
