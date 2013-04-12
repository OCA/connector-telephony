# -*- encoding: utf-8 -*-
##############################################################################
#
#    Asterisk Click2dial module for OpenERP
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

from openerp.osv import osv, fields
# Lib required to print logs
import logging
# Lib to translate error messages
from openerp.tools.translate import _
# Lib for phone number reformating -> pip install phonenumbers
import phonenumbers
# Lib py-asterisk from http://code.google.com/p/py-asterisk/
# We need a version which has this commit : http://code.google.com/p/py-asterisk/source/detail?r=8d0e1c941cce727c702582f3c9fcd49beb4eeaa4
# so a version after Nov 20th, 2012
from Asterisk import Manager

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
        'login': fields.char('AMI login', size=30, required=True, help="Login that OpenERP will use to communicate with the Asterisk Manager Interface. Refer to /etc/asterisk/manager.conf on your Asterisk server."),
        'password': fields.char('AMI password', size=30, required=True, help="Password that Asterisk will use to communicate with the Asterisk Manager Interface. Refer to /etc/asterisk/manager.conf on your Asterisk server."),
        'context': fields.char('Dialplan context', size=50, required=True, help="Asterisk dialplan context from which the calls will be made. Refer to /etc/asterisk/extensions.conf on your Asterisk server."),
        'wait_time': fields.integer('Wait time (sec)', required=True, help="Amount of time (in seconds) Asterisk will try to reach the user's phone before hanging up."),
        'extension_priority': fields.integer('Extension priority', required=True, help="Priority of the extension in the Asterisk dialplan. Refer to /etc/asterisk/extensions.conf on your Asterisk server."),
        'alert_info': fields.char('Alert-Info SIP header', size=255, help="Set Alert-Info header in SIP request to user's IP Phone for the click2dial feature. If empty, the Alert-Info header will not be added. You can use it to have a special ring tone for click2dial (a silent one !) or to activate auto-answer for example."),
        'number_of_digits_to_match_from_end': fields.integer('Number of digits to match from end', help='In several situations, the Asterisk-OpenERP connector will have to find a Partner in OpenERP from a phone number presented by the calling party. As the phone numbers presented by your phone operator may not always be displayed in a standard format, the best method to find the related Partner in OpenERP is to try to match the end of the phone numbers of the Partners in OpenERP with the N last digits of the phone number presented by the calling party. N is the value you should enter in this field.'),
        'company_id': fields.many2one('res.company', 'Company', help="Company who uses the Asterisk server."),
    }

    def _get_prefix_from_country(self, cr, uid, context=None):
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
        country_code = user.company_id and user.company_id.partner_id and user.company_id.partner_id.country_id and user.company_id.partner_id.country_id.code or False
        default_country_prefix = False
        if country_code:
            default_country_prefix = phonenumbers.country_code_for_region(country_code)
        return default_country_prefix

    _defaults = {
        'active': True,
        'port': 5038,  # Default AMI port
        'out_prefix': '0',
        'national_prefix': '0',
        'international_prefix': '00',
        'country_prefix': _get_prefix_from_country,
        'extension_priority': 1,
        'wait_time': 15,
        'number_of_digits_to_match_from_end': 9,
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
                raise osv.except_osv(_('Error :'), _("You should set a TCP port between 1 and 65535 for the Asterisk server '%s'" % server.name))
            if server.number_of_digits_to_match_from_end > 20 or server.number_of_digits_to_match_from_end < 1:
                raise osv.except_osv(_('Error :'), _("You should set a 'Number of digits to match from end' between 1 and 20 for the Asterisk server '%s'" % server.name))
            for check_string in [dialplan_context, alert_info, login, password]:
                if check_string[1]:
                    try:
                        string = check_string[1].encode('ascii')
                    except UnicodeEncodeError:
                        raise osv.except_osv(_('Error :'), _("The '%s' should only have ASCII caracters for the Asterisk server '%s'" % (check_string[0], server.name)))
        return True


    _constraints = [
        (_check_validity, "Error message in raise", ['out_prefix', 'country_prefix', 'national_prefix', 'international_prefix', 'wait_time', 'extension_priority', 'port', 'context', 'alert_info', 'login', 'password', 'number_of_digits_to_match_from_end']),
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

        # Before starting to use prefix, we convert empty prefix whose value
        # is False to an empty string
        country_prefix = ast_server.country_prefix or ''
        national_prefix = ast_server.national_prefix or ''
        international_prefix = ast_server.international_prefix or ''
        out_prefix = ast_server.out_prefix or ''

        # Maybe one day we will use
        # phonenumbers.format_out_of_country_calling_number(phonenumbers.parse('<phone_number_e164', None), 'FR')
        # The country code seems to be OK with the ones of OpenERP
        # But it returns sometimes numbers with '-'... we have to investigate this first
        # International format
        if tmp_number[0] != '+':
            raise # This should never happen
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

        # Add 'out prefix' to all numbers
        tmp_number = out_prefix + tmp_number
        _logger.debug('Out prefix = %s - Number to be sent to Asterisk = %s' % (out_prefix, tmp_number))
        return tmp_number


    # TODO : one day, we will use phonenumbers.format_out_of_country_calling_number() ?
    # if yes, then we can trash the fields international_prefix, national_prefix
    # country_prefix and this kind of code
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


    def _get_asterisk_server_from_user(self, cr, uid, context=None):
        '''Returns an asterisk.server browse object'''
        # We check if the user has an Asterisk server configured
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)
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


    def _connect_to_asterisk(self, cr, uid, context=None):
        '''
        Open the connection to the asterisk manager
        Returns an instance of the Asterisk Manager

        '''
        user = self.pool['res.users'].browse(cr, uid, uid, context=context)

        # Note : if I write 'Error' without ' :', it won't get translated...
        # I don't understand why !

        ast_server = self._get_asterisk_server_from_user(cr, uid, context=context)
        # We check if the current user has a chan type
        if not user.asterisk_chan_type:
            raise osv.except_osv(_('Error :'), _('No channel type configured for the current user.'))

        # We check if the current user has an internal number
        if not user.resource:
            raise osv.except_osv(_('Error :'), _('No resource name configured for the current user'))


        _logger.debug("User's phone : %s/%s" % (user.asterisk_chan_type, user.resource))
        _logger.debug("Asterisk server = %s:%d" % (ast_server.ip_address, ast_server.port))

        # Connect to the Asterisk Manager Interface
        try:
            ast_manager = Manager.Manager((ast_server.ip_address, ast_server.port), ast_server.login, ast_server.password)
        except Exception, e:
            _logger.error("Error in the Originate request to Asterisk server %s" % ast_server.ip_address)
            _logger.error("Here is the detail of the error : %s" % e.strerror)
            raise osv.except_osv(_('Error :'), _("Problem in the request from OpenERP to Asterisk. Here is the detail of the error: %s." % e.strerror))
            return False

        return (user, ast_server, ast_manager)

    def _dial_with_asterisk(self, cr, uid, erp_number, context=None):
        #print "_dial_with_asterisk erp_number=", erp_number
        if not erp_number:
            raise osv.except_osv(_('Error :'), "Hara kiri : you must call the function with erp_number")

        user, ast_server, ast_manager = self._connect_to_asterisk(cr, uid, context=context)
        ast_number = self._reformat_number(cr, uid, erp_number, ast_server, context=context)

        # The user should have a CallerID
        if not user.callerid:
            raise osv.except_osv(_('Error :'), _('No callerID configured for the current user'))

        variable = []
        if user.asterisk_chan_type == 'SIP':
            # We can only have one alert-info header in a SIP request
            if user.alert_info:
                variable.append('SIPAddHeader=Alert-Info: ' + user.alert_info)
            elif ast_server.alert_info:
                variable.append('SIPAddHeader=Alert-Info: ' + ast_server.alert_info)
            if user.variable:
                for user_variable in user.variable.split('|'):
                    variable.append(user_variable.strip())

        try:
            ast_manager.Originate(
                user.asterisk_chan_type + '/' + user.resource + ( ('/' + user.dial_suffix) if user.dial_suffix else ''),
                context = ast_server.context,
                extension = ast_number,
                priority = str(ast_server.extension_priority),
                timeout = str(ast_server.wait_time*1000),
                caller_id = user.callerid,
                variable = variable)
        except Exception, e:
            _logger.error("Error in the Originate request to Asterisk server %s" % ast_server.ip_address)
            _logger.error("Here is the detail of the error : '%s'" % unicode(e))
            raise osv.except_osv(_('Error :'), _("Click to dial with Asterisk failed.\nHere is the error: '%s'" % unicode(e)))

        finally:
            ast_manager.Logoff()

        return True

    def _get_calling_number(self, cr, uid, context=None):

        user, ast_server, ast_manager = self._connect_to_asterisk(cr, uid, context=context)
        calling_party_number = False
        try:
            list_chan = ast_manager.Status()
            #from pprint import pprint
            #pprint(list_chan)
            _logger.debug("Result of Status AMI request: %s", list_chan)
            for chan in list_chan.values():
                sip_account = user.asterisk_chan_type + '/' + user.resource
                if chan.get('ChannelState') == '4' and chan.get('ConnectedLineNum') == user.internal_number: # 4 = Ring
                    _logger.debug("Found a matching Event in 'Ring' state")
                    calling_party_number = chan.get('CallerIDNum')
                    break
                if chan.get('ChannelState') == '6' and sip_account in chan.get('BridgedChannel'): # 6 = Up
                    _logger.debug("Found a matching Event in 'Up' state")
                    calling_party_number = chan.get('CallerIDNum')
                    break
        except Exception, e:
            _logger.error("Error in the Status request to Asterisk server %s" % ast_server.ip_address)
            _logger.error("Here is the detail of the error : '%s'" % unicode(e))
            raise osv.except_osv(_('Error :'), _("Can't get calling number from  Asterisk.\nHere is the error: '%s'" % unicode(e)))

        finally:
            ast_manager.Logoff()

        _logger.debug("The calling party number is '%s'" % calling_party_number)

        return calling_party_number



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
            ('Local', 'Local'),
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
        'resource': fields.char('Resource name', size=64,
            help="Resource name for the channel type selected. For example, if you use 'Dial(SIP/phone1)' in your Asterisk dialplan to ring the SIP phone of this user, then the resource name for this user is 'phone1'.  For a SIP phone, the phone number is often used as resource name, but not always."),
        'alert_info': fields.char('User-specific Alert-Info SIP header', size=255, help="Set a user-specific Alert-Info header in SIP request to user's IP Phone for the click2dial feature. If empty, the Alert-Info header will not be added. You can use it to have a special ring tone for click2dial (a silent one !) or to activate auto-answer for example."),
        'variable': fields.char('User-specific Variable', size=255, help="Set a user-specific 'Variable' field in the Asterisk Manager Interface 'originate' request for the click2dial feature. If you want to have several variable headers, separate them with '|'."),
        'asterisk_server_id': fields.many2one('asterisk.server', 'Asterisk server',
            help="Asterisk server on which the user's phone is connected. If you leave this field empty, it will use the first Asterisk server of the user's company."),
               }

    _defaults = {
        'asterisk_chan_type': 'SIP',
    }

    def _check_validity(self, cr, uid, ids):
        for user in self.browse(cr, uid, ids):
            for check_string in [('Resource name', user.resource), ('Internal number', user.internal_number), ('Caller ID', user.callerid)]:
                if check_string[1]:
                    try:
                        plom = check_string[1].encode('ascii')
                    except UnicodeEncodeError:
                        raise osv.except_osv(_('Error :'), _("The '%s' for the user '%s' should only have ASCII caracters" % (check_string[0], user.name)))
        return True

    _constraints = [
        (_check_validity, "Error message in raise", ['resource', 'internal_number', 'callerid']),
    ]



class res_partner(osv.osv):
    _inherit = "res.partner"


    def _format_phonenumber_to_e164(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for partner in self.read(cr, uid, ids, ['phone', 'mobile', 'fax'], context=context):
            result[partner['id']] = {}
            for fromfield, tofield in [('phone', 'phone_e164'), ('mobile', 'mobile_e164'), ('fax', 'fax_e164')]:
                if not partner.get(fromfield):
                    res = False
                else:
                    try:
                        res = phonenumbers.format_number(phonenumbers.parse(partner.get(fromfield), None), phonenumbers.PhoneNumberFormat.E164)
                    except Exception, e:
                        _logger.error("Cannot reformat the phone number '%s' to E.164 format. Error message: %s" % (partner.get(fromfield), e))
                        _logger.error("You should fix this number and run the wizard 'Reformat all phone numbers' from the menu Settings > Configuration > Asterisk")
                    # If I raise an exception here, it won't be possible to install
                    # the module on a DB with bad phone numbers
                        #raise osv.except_osv(_('Error :'), _("Cannot reformat the phone number '%s' to E.164 format. Error message: %s" % (partner.get(fromfield), e)))
                        res = False
                result[partner['id']][tofield] = res
        #print "RESULT _format_phonenumber_to_e164", result
        return result


    _columns = {
        'phone_e164': fields.function(_format_phonenumber_to_e164, type='char', size=64, string='Phone in E.164 format', readonly=True, multi="e164", store={
            'res.partner': (lambda self, cr, uid, ids, c={}: ids, ['phone'], 10),
            }),
        'mobile_e164': fields.function(_format_phonenumber_to_e164, type='char', size=64, string='Mobile in E.164 format', readonly=True, multi="e164", store={
            'res.partner': (lambda self, cr, uid, ids, c={}: ids, ['mobile'], 10),
            }),
        'fax_e164': fields.function(_format_phonenumber_to_e164, type='char', size=64, string='Fax in E.164 format', readonly=True, multi="e164", store={
            'res.partner': (lambda self, cr, uid, ids, c={}: ids, ['fax'], 10),
            }),
        }

    def _reformat_phonenumbers(self, cr, uid, vals, context=None):
        """Reformat phone numbers in international format i.e. +33141981242"""
        phonefields = ['phone', 'fax', 'mobile']
        if any([vals.get(field) for field in phonefields]):
            user = self.pool['res.users'].browse(cr, uid, uid, context=context)
            # country_id on res.company is a fields.function that looks at
            # company_id.partner_id.addres(default).country_id
            if user.company_id.country_id:
                user_countrycode = user.company_id.country_id.code
            else:
                # We need to raise an exception here because, if we pass None as second arg of phonenumbers.parse(), it will raise an exception when you try to enter a phone number in national format... so it's better to raise the exception here
                raise osv.except_osv(_('Error :'), _("You should set a country on the company '%s'" % user.company_id.name))
            #print "user_countrycode=", user_countrycode
            for field in phonefields:
                if vals.get(field):
                    try:
                        res_parse = phonenumbers.parse(vals.get(field), user_countrycode)
                    except Exception, e:
                        raise osv.except_osv(_('Error :'), _("Cannot reformat the phone number '%s' to international format. Error message: %s" % (vals.get(field), e)))
                    #print "res_parse=", res_parse
                    vals[field] = phonenumbers.format_number(res_parse, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        return vals


    def create(self, cr, uid, vals, context=None):
        vals_reformated = self._reformat_phonenumbers(cr, uid, vals, context=context)
        return super(res_partner, self).create(cr, uid, vals_reformated, context=context)


    def write(self, cr, uid, ids, vals, context=None):
        vals_reformated = self._reformat_phonenumbers(cr, uid, vals, context=context)
        return super(res_partner, self).write(cr, uid, ids, vals_reformated, context=context)


    def dial(self, cr, uid, ids, phone_field=['phone', 'phone_e164'], context=None):
        '''Read the number to dial and call _connect_to_asterisk the right way'''
        erp_number_read = self.read(cr, uid, ids[0], phone_field, context=context)
        erp_number_e164 = erp_number_read[phone_field[1]]
        erp_number_display = erp_number_read[phone_field[0]]
        # Check if the number to dial is not empty
        if not erp_number_display:
            raise osv.except_osv(_('Error :'), _('There is no phone number !'))
        elif erp_number_display and not erp_number_e164:
            raise osv.except_osv(_('Error :'), _("The phone number isn't stored in the standard E.164 format. Try to run the wizard 'Reformat all phone numbers' from the menu Settings > Configuration > Asterisk."))
        return self.pool['asterisk.server']._dial_with_asterisk(cr, uid, erp_number_e164, context=context)


    def action_dial_phone(self, cr, uid, ids, context=None):
        '''Function called by the button 'Dial' next to the 'phone' field
        in the partner view'''
        return self.dial(cr, uid, ids, phone_field=['phone', 'phone_e164'], context=context)


    def action_dial_mobile(self, cr, uid, ids, context=None):
        '''Function called by the button 'Dial' next to the 'mobile' field
        in the partner view'''
        return self.dial(cr, uid, ids, phone_field=['mobile', 'mobile_e164'], context=context)


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


    def get_partner_from_phone_number(self, cr, uid, presented_number, context=None):
        # We check that "number" is really a number
        _logger.debug(u"Call get_name_from_phone_number with number = %s" % presented_number)
        if not isinstance(presented_number, (str, unicode)):
            _logger.warning(u"Number '%s' should be a 'str' or 'unicode' but it is a '%s'" % (presented_number, type(presented_number)))
            return False
        if not presented_number.isdigit():
            _logger.warning(u"Number '%s' should only contain digits." % presented_number)
            return False

        ast_server = self.pool['asterisk.server']._get_asterisk_server_from_user(cr, uid, context=context)
        nr_digits_to_match_from_end = ast_server.number_of_digits_to_match_from_end
        if len(presented_number) >= nr_digits_to_match_from_end:
            end_number_to_match = presented_number[-nr_digits_to_match_from_end:len(presented_number)]
        else:
            end_number_to_match = presented_number

        _logger.debug("Will search phone and mobile numbers in res.partner ending with '%s'" % end_number_to_match)

        # We try to match a phone or mobile number with the same end
        pg_seach_number = str('%' + end_number_to_match)
        res_ids = self.search(cr, uid, ['|', ('phone_e164', 'ilike', pg_seach_number), ('mobile_e164', 'ilike', pg_seach_number)], context=context)
        # TODO : use is_number_match() of the phonenumber lib ?
        if len(res_ids) > 1:
            _logger.warning(u"There are several partners (IDS = %s) with a phone number ending with '%s'" % (str(res_ids), end_number_to_match))
        if res_ids:
            entry = self.read(cr, uid, res_ids[0], ['name', 'parent_id'], context=context)
            _logger.debug(u"Answer get_partner_from_phone_number with name = %s" % entry['name'])
            return (entry['id'], entry['parent_id'] and entry['parent_id'][0] or False, entry['name'])
        else:
            _logger.debug(u"No match for end of phone number '%s'" % end_number_to_match)
            return False


# This module supports multi-company
class res_company(osv.osv):
    _inherit = "res.company"

    _columns = {
        'asterisk_server_ids': fields.one2many('asterisk.server', 'company_id', 'Asterisk servers', help="List of Asterisk servers.")
    }

