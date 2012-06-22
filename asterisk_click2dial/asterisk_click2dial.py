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
        'alert_info': fields.char('Alert-Info SIP header', size=255, help="Set Alert-Info header in SIP request to user's IP Phone for the click2dial feature. If empty, the Alert-Info header will not be added. You can use it to have a special ring tone for click2dial (a silent one !) or to activate auto-answer for example. If you want to have several variable headers, separate them with '|'."),
        'company_id': fields.many2one('res.company', 'Company', help="Company who uses the Asterisk server."),
    }

    _defaults = {
        'active': True,
        'port': 5038,  # Default AMI port
        'out_prefix': '0',
        'national_prefix': '0',
        'international_prefix': '00',
        'extension_priority': 1,
        'wait_time': 15,
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


    def _reformat_number(self, cr, uid, erp_number, ast_server, context=None):
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

        # treat (0) as a special condition as we dont want an extra 0 to be inserted in the number
        # FIXME all 0s after the country prefix should be stripped off
        tmp_number = tmp_number.replace('(0)','')

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


    def _convert_number_to_international_format(self, cr, uid, number, ast_server, context=None):
        '''Convert the number presented by the phone network to a number
        in international format e.g. +33141981242'''
        if number and number.isdigit() and len(number) > 5:
            if ast_server.international_prefix and number[0:len(ast_server.international_prefix)] == ast_server.international_prefix:
                number = number[len(ast_server.international_prefix):]
                number = '+' + number
            elif ast_server.national_prefix and number[0:len(ast_server.national_prefix)] == ast_server.national_prefix:
                number = number[len(ast_server.national_prefix):]
                number = '+' + ast_server.country_prefix + number
        return number


    def _get_asterisk_server_from_user(self, cr, uid, user, context=None):
        '''Returns an asterisk.server browse object'''
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
        return ast_server


    def _parse_asterisk_answer(self, cr, uid, sock, end_string='\r\n\r\n', context=None):
        '''Parse the answer of the Asterisk Manager Interface'''
        answer = ''
        data = ''
        while end_string not in data:
            data = sock.recv(1024)
            if data:
                answer += data
        # remove end_string from answer
        if answer[-len(end_string):] == end_string:
            answer = answer[:-len(end_string)]
        return answer


    def _connect_to_asterisk(self, cr, uid, method='dial', options=None, context=None):
        '''
        Open the socket to the Asterisk Manager Interface (AMI)
        and send instructions to Dial to Asterisk. That's the important function !

        '''
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)

        # Note : if I write 'Error' without ' :', it won't get translated...
        # I don't understand why !

        ast_server = self._get_asterisk_server_from_user(cr, uid, user, context=context)
        # We check if the current user has a chan type
        if not user.asterisk_chan_type:
            raise osv.except_osv(_('Error :'), _('No channel type configured for the current user.'))

        # We check if the current user has an internal number
        if not user.internal_number:
            raise osv.except_osv(_('Error :'), _('No internal phone number configured for the current user'))


        _logger.debug("User's phone : %s/%s" % (user.asterisk_chan_type, user.internal_number))
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
                    _logger.debug("Successful authentification to Asterisk :\n%s" % login_answer)
                else:
                    raise osv.except_osv(_('Error :'), _("Authentification to Asterisk failed :\n%s" % login_answer))

                if method == 'dial':
                    # Convert the phone number in the format that will be sent to Asterisk
                    erp_number = options.get('erp_number')
                    if not erp_number:
                        raise osv.except_osv(_('Error :'), "Hara kiri : you must call the function with erp_number in the options")
                    ast_number = self._reformat_number(cr, uid, erp_number, ast_server, context=context)

                    # The user should have a CallerID
                    if not user.callerid:
                        raise osv.except_osv(_('Error :'), _('No callerID configured for the current user'))

                    # Dial with Asterisk
                    originate_act = 'Action: originate\r\n' + \
                        'Channel: ' + user.asterisk_chan_type + '/' + user.internal_number + ( ('/' + user.dial_suffix) if user.dial_suffix else '') + '\r\n' + \
                        'Priority: ' + str(ast_server.extension_priority) + '\r\n' + \
                        'Timeout: ' + str(ast_server.wait_time*1000) + '\r\n' + \
                        'CallerId: ' + user.callerid + '\r\n' + \
                        'Exten: ' + ast_number + '\r\n' + \
                        'Context: ' + ast_server.context + '\r\n'
                    if ast_server.alert_info and user.asterisk_chan_type == 'SIP':
                        for server_alertinfo in ast_server.alert_info.split('|'):
                            originate_act += 'Variable: SIPAddHeader=Alert-Info: ' + server_alertinfo.strip() + '\r\n'
                    if user.alert_info and user.asterisk_chan_type == 'SIP':
                        for user_alertinfo in user.alert_info.split('|'):
                            originate_act += 'Variable: SIPAddHeader=Alert-Info: ' + user_alertinfo.strip() + '\r\n'
                    if user.variable:
                        for user_variable in user.variable.split('|'):
                            originate_act += 'Variable: ' + user_variable.strip() + '\r\n'

                    originate_act += '\r\n'
                    sock.send(originate_act.encode('ascii'))
                    originate_answer = self._parse_asterisk_answer(cr, uid, sock, context=context)
                    if 'Response: Success' in originate_answer:
                        _logger.debug('Successfull originate command : %s' % originate_answer)
                    else:
                        raise osv.except_osv(_('Error :'), _("Click to dial with Asterisk failed :\n%s" % originate_answer))

                elif method == "get_calling_number":
                    status_act = 'Action: Status\r\n\r\n' # TODO : add ActionID
                    sock.send(status_act.encode('ascii'))
                    status_answer = self._parse_asterisk_answer(cr, uid, sock, end_string='Event: StatusComplete', context=context)

                    if 'Response: Success' in status_answer:
                        _logger.debug('Successfull Status command :\n%s' % status_answer)
                    else:
                        raise osv.except_osv(_('Error :'), _("Status command to Asterisk failed :\n%s" % status_answer))

                    # Parse answer
                    calling_party_number = False
                    status_answer_split = status_answer.split('\r\n\r\n')
                    for event in status_answer_split:
                        string_match = 'BridgedChannel: ' + user.asterisk_chan_type + '/' + user.internal_number
                        if not string_match in event:
                            continue
                        event_split = event.split('\r\n')
                        for event_line in event_split:
                            if not 'CallerIDNum' in event_line:
                                continue
                            line_detail = event_line.split(': ')
                            if len(line_detail) <> 2:
                                raise osv.except_osv('Error :', "Hara kiri... this is not possible")
                            calling_party_number = line_detail[1]

                # Logout of Asterisk
                sock.send(('Action: Logoff\r\n\r\n').encode('ascii'))
                logout_answer = self._parse_asterisk_answer(cr, uid, sock, context=context)
                if 'Response: Goodbye' in logout_answer:
                    _logger.debug('Successfull logout from Asterisk :\n%s' % logout_answer)
                else:
                    _logger.warning('Logout from Asterisk failed :\n%s' % logout_answer)
            # we catch only network problems here
            except socket.error:
                _logger.warning("Unable to connect to the Asterisk server '%s' IP '%s:%d'" % (ast_server.name, ast_server.ip_address, ast_server.port))
                raise osv.except_osv(_('Error :'), _("The connection from OpenERP to the Asterisk server failed. Please check the configuration on OpenERP and on Asterisk."))
            finally:
                sock.close()
        if method == 'dial':
            _logger.info("Asterisk Click2Dial from %s/%s to %s" % (user.asterisk_chan_type, user.internal_number, ast_number))
            return True

        elif method == "get_calling_number":
            _logger.debug("Calling party number: %s" % calling_party_number)
            return calling_party_number

        else:
            return False

asterisk_server()


# Parameters specific for each user
class res_users(osv.osv):
    _inherit = "res.users"

    _columns = {
        'internal_number': fields.char('Internal number', size=15,
            help="User's internal phone number."),
        'dial_suffix': fields.char('User-specific dial suffix', size=15,
            help="User-specific dial suffix such as aa=2wb for SCCP auto answer."),
        'callerid': fields.char('Caller ID', size=50,
            help="Caller ID used for the calls initiated by this user."),
        # You'd probably think : Asterisk should reuse the callerID of sip.conf !
        # But it cannot, cf http://lists.digium.com/pipermail/asterisk-users/2012-January/269787.html
        'asterisk_chan_type': fields.selection([
            ('SIP', 'SIP'),
            ('IAX2', 'IAX2'),
            ('DAHDI', 'DAHDI'),
            ('Zap', 'Zap'),
            ('Skinny', 'Skinny'),
            ('MGCP', 'MGCP'),
            ('mISDN', 'mISDN'),
            ('H323', 'H323'),
            ('SCCP', 'SCCP'),
            ], 'Asterisk channel type',
            help="Asterisk channel type, as used in the Asterisk dialplan. If the user has a regular IP phone, the channel type is 'SIP'."),
        'alert_info': fields.char('User-specific Alert-Info SIP header', size=255, help="Set a user-specific Alert-Info header in SIP request to user's IP Phone for the click2dial feature. If empty, the Alert-Info header will not be added. You can use it to have a special ring tone for click2dial (a silent one !) or to activate auto-answer for example. If you want to have several variable headers, separate them with '|'."),
        'variable': fields.char('User-specific Variable', size=255, help="Set a user-specific 'Variable' field in the Asterisk Manager Interface 'originate' request for the click2dial feature. If you want to have several variable headers, separate them with '|'."),
        'asterisk_server_id': fields.many2one('asterisk.server', 'Asterisk server',
            help="Asterisk server on which the user's phone is connected. If you leave this field empty, it will use the first Asterisk server of the user's company."),
               }

    _defaults = {
        'asterisk_chan_type': 'SIP',
    }

    def _check_validity(self, cr, uid, ids):
        for user in self.browse(cr, uid, ids):
            for check_string in [('Internal number', user.internal_number), ('Caller ID', user.callerid)]:
                if check_string[1]:
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
    _inherit = "res.partner.address"


    def dial(self, cr, uid, ids, phone_field='phone', context=None):
        '''Read the number to dial and call _connect_to_asterisk the right way'''
        erp_number = self.read(cr, uid, ids, [phone_field], context=context)[0][phone_field]
        # Check if the number to dial is not empty
        if not erp_number:
            raise osv.except_osv(_('Error :'), _('There is no phone number !'))
        options = {'erp_number': erp_number}
        return self.pool.get('asterisk.server')._connect_to_asterisk(cr, uid, method='dial', options=options, context=context)


    def action_dial_phone(self, cr, uid, ids, context=None):
        '''Function called by the button 'Dial' next to the 'phone' field
        in the partner address view'''
        return self.dial(cr, uid, ids, phone_field='phone', context=context)


    def action_dial_mobile(self, cr, uid, ids, context=None):
        '''Function called by the button 'Dial' next to the 'mobile' field
        in the partner address view'''
        return self.dial(cr, uid, ids, phone_field='mobile', context=context)


    def get_name_from_phone_number(self, cr, uid, number, context=None):
        '''Function to get name from phone number. Usefull for use from Asterisk
        to add CallerID name to incoming calls.
        The "scripts/" subdirectory of this module has an AGI script that you can
        install on your Asterisk IPBX : the script will be called from the Asterisk
        dialplan via the AGI() function and it will use this function via an XML-RPC
        request.
        '''
        res = self.get_partner_from_phone_number(cr, uid, number, context=context)
        if res:
            return res[2]
        else:
            return False


    def get_partner_from_phone_number(self, cr, uid, number, context=None):
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
                    return (entry.id, entry.partner_id.id, entry.name)
            if entry.mobile:
                if re.sub(r'\D', '', entry.mobile).endswith(number):
                    _logger.debug(u"Answer get_name_from_phone_number with name = %s" % entry.name)
                    return (entry.id, entry.partner_id.id, entry.name)

        _logger.debug(u"No match for phone number %s" % number)
        return False

res_partner_address()


class wizard_open_calling_partner(osv.osv_memory):
    _name = "wizard.open.calling.partner"
    _description = "Open calling partner"

    _columns = {
        'calling_number': fields.char('Calling number', size=30, readonly=True, help="Phone number of calling party that has been obtained from Asterisk."),
        'partner_address_id': fields.many2one('res.partner.address', 'Contact name', readonly=True, help="Partner contact related to the calling number"),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True, help="Partner related to the calling number"),
        'to_update_partner_address_id': fields.many2one('res.partner.address', 'Contact to update', help="Partner contact on which the phone or mobile number will be written"),
        'current_phone': fields.related('to_update_partner_address_id', 'phone', type='char', relation='res.partner.address', string='Current phone', readonly=True),
        'current_mobile': fields.related('to_update_partner_address_id', 'mobile', type='char', relation='res.partner.address', string='Current mobile', readonly=True),
            }


    def default_get(self, cr, uid, fields, context=None):
        '''Thanks to the default_get method, we are able to query Asterisk and
        get the corresponding partner when we launch the wizard'''
        res = {}
        calling_number = self.pool.get('asterisk.server')._connect_to_asterisk(cr, uid, method='get_calling_number', context=context)
        #To test the code without Asterisk server
        #calling_number = "0141981242"
        if calling_number:
            res['calling_number'] = calling_number
            # We match only on the end of the phone number
            if len(calling_number) >= 9:
                number_to_search = calling_number[-9:len(calling_number)]
            else:
                number_to_search = calling_number
            partner = self.pool.get('res.partner.address').get_partner_from_phone_number(cr, uid, number_to_search, context=context)
            if partner:
                res['partner_address_id'] = partner[0]
                res['partner_id'] = partner[1]
            else:
                res['partner_id'] = False
                res['partner_address_id'] = False
        else:
            _logger.debug("Could not get the calling number from Asterisk.")
            raise osv.except_osv(_('Error :'), _("Could not get the calling number from Asterisk. Are you currently on the phone ? If yes, check your setup and look at the OpenERP debug logs."))

        return res


    def open_filtered_object(self, cr, uid, ids, oerp_object, context=None):
        '''Returns the action that opens the list view of the 'oerp_object'
        given as argument filtered on the partner'''
        # This module only depends on "base"
        # and I don't want to add a dependancy on "sale" or "account"
        # So I just check here that the model exists, to avoid a crash
        if not self.pool.get('ir.model').search(cr, uid, [('model', '=', oerp_object._name)], context=context):
            raise osv.except_osv(_('Error :'), _("The object '%s' is not found in your OpenERP database, probably because the related module is not installed." % oerp_object._description))

        partner = self.read(cr, uid, ids[0], ['partner_id'], context=context)['partner_id']
        if partner:
            action = {
                'name': oerp_object._description,
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': oerp_object._name,
                'type': 'ir.actions.act_window',
                'nodestroy': False, # close the pop-up wizard after action
                'target': 'current',
                'domain': [('partner_id', '=', partner[0])],
                }
            return action
        else:
            return False


    def open_sale_orders(self, cr, uid, ids, context=None):
        '''Function called by the related button of the wizard'''
        return self.open_filtered_object(cr, uid, ids, self.pool.get('sale.order'), context=context)


    def open_invoices(self, cr, uid, ids, context=None):
        '''Function called by the related button of the wizard'''
        return self.open_filtered_object(cr, uid, ids, self.pool.get('account.invoice'), context=context)


    def simple_open(self, cr, uid, ids, object_name='res.partner', context=None):
        if object_name == 'res.partner':
            field = 'partner_id'
            label = 'Partner'
        elif object_name == 'res.partner.address':
            field = 'partner_address_id'
            label = 'Contact'
        else:
            raise osv.except_osv(_('Error :'), "This object '%s' is not supported" % object_name)
        record_to_open = self.read(cr, uid, ids[0], [field], context=context)[field]
        if record_to_open:
            return {
                'name': label,
                'view_type': 'form',
                'view_mode': 'form,tree',
                'res_model': object_name,
                'type': 'ir.actions.act_window',
                'nodestroy': False, # close the pop-up wizard after action
                'target': 'current',
                'res_id': record_to_open[0],
                }
        else:
            return False


    def open_partner(self, cr, uid, ids, context=None):
        '''Function called by the related button of the wizard'''
        return self.simple_open(cr, uid, ids, object_name='res.partner', context=context)


    def open_partner_address(self, cr, uid, ids, context=None):
        '''Function called by the related button of the wizard'''
        return self.simple_open(cr, uid, ids, object_name='res.partner.address', context=context)


    def create_partner_address(self, cr, uid, ids, phone_type='phone', context=None):
        '''Function called by the related button of the wizard'''
        calling_number = self.read(cr, uid, ids[0], ['calling_number'], context=context)['calling_number']
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        ast_server = self.pool.get('asterisk.server')._get_asterisk_server_from_user(cr, uid, user, context=context)
        # Convert the number to the international format
        number_to_write = self.pool.get('asterisk.server')._convert_number_to_international_format(cr, uid, calling_number, ast_server, context=context)

        new_partner_address_id = self.pool.get('res.partner.address').create(cr, uid, {phone_type: number_to_write}, context=context)
        action = {
            'name': 'Create new contact',
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'res.partner.address',
            'type': 'ir.actions.act_window',
            'nodestroy': False,
            'target': 'current',
            'res_id': new_partner_address_id,
        }
        return action


    def create_partner_address_phone(self, cr, uid, ids, context=None):
        return self.create_partner_address(cr, uid, ids, phone_type='phone', context=context)


    def create_partner_address_mobile(self, cr, uid, ids, context=None):
        return self.create_partner_address(cr, uid, ids, phone_type='mobile', context=context)


    def update_partner_address(self, cr, uid, ids, phone_type='mobile', context=None):
        cur_wizard = self.browse(cr, uid, ids[0], context=context)
        if not cur_wizard.to_update_partner_address_id:
            raise osv.except_osv(_('Error :'), _("Select the contact to update."))
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        ast_server = self.pool.get('asterisk.server')._get_asterisk_server_from_user(cr, uid, user, context=context)
        number_to_write = self.pool.get('asterisk.server')._convert_number_to_international_format(cr, uid, cur_wizard.calling_number, ast_server, context=context)
        self.pool.get('res.partner.address').write(cr, uid, cur_wizard.to_update_partner_address_id.id, {phone_type: number_to_write}, context=context)
        action = {
            'name': 'Contact: ' + cur_wizard.to_update_partner_address_id.name,
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'res.partner.address',
            'type': 'ir.actions.act_window',
            'nodestroy': False,
            'target': 'current',
            'res_id': cur_wizard.to_update_partner_address_id.id
            }
        return action


    def update_partner_address_phone(self, cr, uid, ids, context=None):
        return self.update_partner_address(cr, uid, ids, phone_type='phone', context=context)


    def update_partner_address_mobile(self, cr, uid, ids, context=None):
        return self.update_partner_address(cr, uid, ids, phone_type='mobile', context=context)


    def onchange_to_update_partner_address(self, cr, uid, ids, to_update_partner_address_id, context=None):
        res = {}
        res['value'] = {}
        if to_update_partner_address_id:
            to_update_partner_address = self.pool.get('res.partner.address').browse(cr, uid, to_update_partner_address_id, context=context)
            res['value'].update({'current_phone': to_update_partner_address.phone,
                'current_mobile': to_update_partner_address.mobile})
        else:
            res['value'].update({'current_phone': False, 'current_mobile': False})
        return res

wizard_open_calling_partner()


# This module supports multi-company
class res_company(osv.osv):
    _inherit = "res.company"

    _columns = {
        'asterisk_server_ids': fields.one2many('asterisk.server', 'company_id', 'Asterisk servers', help="List of Asterisk servers.")
    }

res_company()
