# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk Click2dial module for OpenERP
#    Copyright (C) 2010 Alexis de Lattre <alexis@via.ecp.fr>
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
import netsvc
# Lib to translate error messages
from tools.translate import _
# Lib for regexp
import re


class asterisk_server(osv.osv):
    '''Asterisk server object, to store all the parameters of the Asterisk IPBXs'''
    _name = "asterisk.server"
    _description = "Asterisk Servers"
    _columns = {
        'name': fields.char('Asterisk server name', size=50, required=True, help="Asterisk server name."),
        'active': fields.boolean('Active', help="The active field allows you to hide the Asterisk server without deleting it."),
        'ip_address': fields.char('Asterisk IP addr. or DNS', size=50, required=True, help="IPv4 address or DNS name of the Asterisk server."),
        'port': fields.integer('Port', required=True, help="TCP port on which the Asterisk Manager Interface listens. Defined in /etc/asterisk/manager.conf on Asterisk."),
        'out_prefix': fields.char('Out prefix', size=4, help="Prefix to dial to place outgoing calls. If you don't use a prefix to place outgoing calls, leave empty."),
        'national_prefix': fields.char('National prefix', size=4, help="Prefix for national phone calls (don't include the 'out prefix'). For e.g., in France, the phone numbers look like '01 41 98 12 42' : the National prefix is '0'."),
        'international_prefix': fields.char('International prefix', size=4, help="Prefix to add to make international phone calls (don't include the 'out prefix'). For e.g., in France, the International prefix is '00'."),
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

    def _only_digits(self, cr, uid, ids, prefix, can_be_empty):
        for i in ids:
            prefix_to_check = self.read(cr, uid, i, [prefix])[prefix]
            if not prefix_to_check:
                if can_be_empty:
                    return True
                else:
                    return False
            else:
                if not prefix_to_check.isdigit():
                    return False
        return True

    def _only_digits_out_prefix(self, cr, uid, ids):
        return self._only_digits(cr, uid, ids, 'out_prefix', True)

    def _only_digits_country_prefix(self, cr, uid, ids):
        return self._only_digits(cr, uid, ids, 'country_prefix', False)

    def _only_digits_national_prefix(self, cr, uid, ids):
        return self._only_digits(cr, uid, ids, 'national_prefix', True)

    def _only_digits_international_prefix(self, cr, uid, ids):
        return self._only_digits(cr, uid, ids, 'international_prefix', False)

    def _check_wait_time(self, cr, uid, ids):
        for i in ids:
            wait_time_to_check = self.read(cr, uid, i, ['wait_time'])['wait_time']
            if wait_time_to_check < 1 or wait_time_to_check > 120:
                return False
        return True

    def _check_extension_priority(self, cr, uid, ids):
        for i in ids:
            extension_priority_to_check = self.read(cr, uid, i, ['extension_priority'])['extension_priority']
            if extension_priority_to_check < 1:
                return False
            return True

    def _check_port(self, cr, uid, ids):
        for i in ids:
            port_to_check = self.read(cr, uid, i, ['port'])['port']
            if port_to_check > 65535 or port_to_check < 1:
                return False
        return True

    _constraints = [
        (_only_digits_out_prefix, "Only use digits for the 'out prefix' or leave empty", ['out_prefix']),
        (_only_digits_country_prefix, "Only use digits for the 'country prefix'", ['country_prefix']),
        (_only_digits_national_prefix, "Only use digits for the 'national prefix' or leave empty", ['national_prefix']),
        (_only_digits_international_prefix, "Only use digits for 'international prefix'", ['international_prefix']),
        (_check_wait_time, "You should enter a 'Wait time' value between 1 and 120 seconds", ['wait_time']),
        (_check_extension_priority, "The 'extension priority' must be a positive value", ['extension_priority']),
        (_check_port, 'TCP ports range from 1 to 65535', ['port']),
    ]


    def reformat_number(self, cr, uid, ids, erp_number, ast_server, context):
        '''
        This function is dedicated to the transformation of the number
        available in OpenERP to the number that Asterisk should dial.
        You may have to inherit this function in another module specific
        for your company if you are not happy with the way I reformat
        the OpenERP numbers.
        '''

        logger = netsvc.Logger()
        error_title_msg = _("Invalid phone number")
        invalid_international_format_msg = _("The phone number is not written in valid international format. Example of valid international format : +33 1 41 98 12 42")
        invalid_national_format_msg = _("The phone number is not written in valid national format.")
        invalid_format_msg = _("The phone number is not written in valid format.")

        # Let's call the variable tmp_number now
        tmp_number = erp_number
        logger.notifyChannel('asterisk_click2dial', netsvc.LOG_DEBUG, 'Number before reformat = ' + tmp_number)

        # Check if empty
        if not tmp_number:
            raise osv.except_osv(error_title_msg, invalid_format_msg)

        # First, we remove all stupid caracters and spaces
        for i in [' ', '.', '(', ')', '[', ']', '-', '/']:
            tmp_number = tmp_number.replace(i, '')

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
            logger.notifyChannel('asterisk_click2dial', netsvc.LOG_DEBUG, 'Number after removal of special char = ' + tmp_number)

            # At this stage, 'tmp_number' should only contain digits
            if not tmp_number.isdigit():
                raise osv.except_osv(error_title_msg, invalid_format_msg)

            logger.notifyChannel('asterisk_click2dial', netsvc.LOG_DEBUG, 'Country prefix = ' + country_prefix)
            if country_prefix == tmp_number[0:len(country_prefix)]:
                # If the number is a national number,
                # remove 'my country prefix' and add 'national prefix'
                tmp_number = (national_prefix) + tmp_number[len(country_prefix):len(tmp_number)]
                logger.notifyChannel('asterisk_click2dial', netsvc.LOG_DEBUG, 'National prefix = ' + national_prefix + ' - Number with national prefix = ' + tmp_number)

            else:
                # If the number is an international number,
                # add 'international prefix'
                tmp_number = international_prefix + tmp_number
                logger.notifyChannel('asterisk_click2dial', netsvc.LOG_DEBUG, 'International prefix = ' + international_prefix + ' - Number with international prefix = ' + tmp_number)

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
        logger.notifyChannel('asterisk_click2dial', netsvc.LOG_DEBUG, 'Out prefix = ' + out_prefix + ' - Number to be sent to Asterisk = ' + tmp_number)
        return tmp_number

    def dial(self, cr, uid, ids, erp_number, context=None):
        '''
        Open the socket to the Asterisk Manager Interface (AMI)
        and send instructions to Dial to Asterisk. That's the important function !

        '''
        logger = netsvc.Logger()
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)

        # Check if the number to dial is not empty
        if not erp_number:
            raise osv.except_osv(_('Error :'), _('There is no phone number !'))
        # Note : if I write 'Error' without ' :', it won't get translated...
        # I don't understand why !

        # We check if the user has an Asterisk server configured
        if not user.asterisk_server_id.id:
            raise osv.except_osv(_('Error :'), _('No Asterisk server configured for the current user.'))
        else:
            ast_server = user.asterisk_server_id

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
        logger.notifyChannel('asterisk_click2dial', netsvc.LOG_DEBUG, 'User dialing : channel = ' + user.asterisk_chan_type + '/' + user.internal_number + ' - Callerid = ' + user.callerid)
        logger.notifyChannel('asterisk_click2dial', netsvc.LOG_DEBUG, 'Asterisk server = ' + ast_server.ip_address + ':' + str(ast_server.port))

        # Connect to the Asterisk Manager Interface
        try:
            ast_ip = socket.gethostbyname(str(ast_server.ip_address))
        except:
            logger.notifyChannel('asterisk_click2dial', netsvc.LOG_DEBUG, "Can't resolve the DNS of the Asterisk server : " + str(ast_server.ip_address))
            raise osv.except_osv(_('Error :'), _("Can't resolve the DNS of the Asterisk server : ") + str(ast_server.ip_address))
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ast_ip, ast_server.port))
            sock.send('Action: login\r\n')
            sock.send('Events: off\r\n')
            sock.send('Username: '+str(ast_server.login)+'\r\n')
            sock.send('Secret: '+str(ast_server.password)+'\r\n\r\n')
            sock.send('Action: originate\r\n')
            sock.send('Channel: ' + str(user.asterisk_chan_type) + '/' + str(user.internal_number)+'\r\n')
            sock.send('Timeout: '+str(ast_server.wait_time*1000)+'\r\n')
            sock.send('CallerId: '+str(user.callerid)+'\r\n')
            sock.send('Exten: '+str(ast_number)+'\r\n')
            sock.send('Context: '+str(ast_server.context)+'\r\n')
            if not ast_server.alert_info and user.asterisk_chan_type == 'SIP':
                sock.send('Variable: SIPAddHeader=Alert-Info: '+str(ast_server.alert_info)+'\r\n')
            sock.send('Priority: '+str(ast_server.extension_priority)+'\r\n\r\n')
            sock.send('Action: Logoff\r\n\r\n')
            sock.close()
        except:
            logger.notifyChannel('asterisk_click2dial', netsvc.LOG_WARNING, "Click2dial failed : unable to connect to Asterisk")
            raise osv.except_osv(_('Error :'), _("The connection from OpenERP to the Asterisk server failed. Please check the configuration on OpenERP and on Asterisk."))
        logger.notifyChannel('asterisk_click2dial', netsvc.LOG_INFO, "Asterisk Click2Dial from " + user.internal_number + ' to ' + ast_number)

asterisk_server()


# Parameters specific for each user
class res_users(osv.osv):
    _name = "res.users"
    _inherit = "res.users"
    _columns = {
        'internal_number': fields.char('Internal number', size=15, help="User's internal phone number."),
        'callerid': fields.char('Caller ID', size=50, help="Caller ID used for the calls initiated by this user."),
        'asterisk_chan_type': fields.selection([('SIP', 'SIP'), ('IAX2', 'IAX2'), ('DAHDI', 'DAHDI'), ('Zap', 'Zap'), ('Skinny', 'Skinny'), ('MGCP', 'MGCP'), ('mISDN', 'mISDN'), ('H323', 'H323')], 'Asterisk channel type', help="Asterisk channel type, as used in the Asterisk dialplan. If the user has a regular IP phone, the channel type is 'SIP'."),
        'asterisk_server_id': fields.many2one('asterisk.server', 'Asterisk server', help="Asterisk server on which the user's phone is connected."),
               }

    _defaults = {
        'asterisk_chan_type': lambda *a: 'SIP',
    }

res_users()


class res_partner_address(osv.osv):
    _name = "res.partner.address"
    _inherit = "res.partner.address"

    def action_dial_phone(self, cr, uid, ids, context):
        '''Function called by the button 'Dial' next to the 'phone' field
        in the partner address view'''
        erp_number = self.read(cr, uid, ids, ['phone'], context=context)[0]['phone']
        self.pool.get('asterisk.server').dial(cr, uid, ids, erp_number, context)

    def action_dial_mobile(self, cr, uid, ids, context):
        '''Function called by the button 'Dial' next to the 'mobile' field
        in the partner address view'''
        erp_number = self.read(cr, uid, ids, ['mobile'], context=context)[0]['mobile']
        self.pool.get('asterisk.server').dial(cr, uid, ids, erp_number, context)

    def get_name_from_phone_number(self, cr, uid, number, context=None):
        '''Function to get name from phone number. Usefull for use from Asterisk
        to add CallerID name to incoming calls
        To use this function from a python console/script :
        import xmlrpclib
        sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')
        sock.execute("openerp_database", user_id_num, "user_passwd", 'res.partner.address', 'get_name_from_phone_number', '141983212')
        '''
        res = {}
        logger = netsvc.Logger()
        # We check that "number" is really a number
        if not isinstance(number, str):
            return False
        if not number.isdigit():
            return False

        netsvc.Logger().notifyChannel('asterisk_click2dial', netsvc.LOG_DEBUG, u"Call get_name_from_phone_number with number = %s" % number)
        # Get all the partner addresses :
        all_ids = self.search(cr, uid, [], context=context)
        # For each partner address, we check if the number matches on the "phone" or "mobile" fields
        for entry in self.browse(cr, uid, all_ids, context=context):
            if entry.phone:
                # We use a regexp on the phone field to remove non-digit caracters
                if re.sub(r'\D', '', entry.phone).endswith(number):
                    logger.notifyChannel('asterisk_click2dial', netsvc.LOG_DEBUG, u"Answer get_name_from_phone_number with name = %s" % entry.name)
                    return entry.name
            if entry.mobile:
                if re.sub(r'\D', '', entry.mobile).endswith(number):
                    logger.notifyChannel('asterisk_click2dial', netsvc.LOG_DEBUG, u"Answer get_name_from_phone_number with name = %s" % entry.name)
                    return entry.name

        logger.notifyChannel('asterisk_click2dial', netsvc.LOG_DEBUG, u"No match for phone number %s" % number)
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
