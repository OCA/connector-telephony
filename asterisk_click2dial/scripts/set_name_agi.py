#! /usr/bin/python
# -*- coding: utf-8 -*-
#  © 2010-2018 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
 Name lookup in Odoo for incoming and outgoing calls with an
 Asterisk IPBX

 This script is designed to be used as an AGI on an Asterisk IPBX...
 BUT I advise you to use a wrapper around this script to control the
 execution time. Why ? Because if the script takes too much time to
 execute or get stucks (in the XML-RPC request for example), then the
 incoming phone call will also get stucks and you will miss a call !
 The simplest solution I found is to use the "timeout" shell command to
 call this script, for example :

 # timeout 2s get_name_agi.py <OPTIONS>

 See my 2 sample wrappers "set_name_incoming_timeout.sh" and
 "set_name_outgoing_timeout.sh"

 It's probably a good idea to create a user in Odoo dedicated to this task.
 This user only needs to be part of the group "Phone CallerID", which has
 read access on the 'res.partner' and other objects with phone numbers and
 names.

 Note that this script can be used without Odoo, with just the
 geolocalisation feature : for that, don't use option --server ;
 only use --geoloc

 This script can be used both on incoming and outgoing calls :

 1) INCOMING CALLS
 When executed from the dialplan on an incoming phone call, it will
 lookup in Odoo's partners and other objects with phone numbers
 (leads, employees, etc...), and, if it finds the phone number, it will
 get the corresponding name of the person and use this name as CallerID
 name for the incoming call.

 Requires the "base_phone" module
 available from https://github.com/OCA/connector-telephony

 Asterisk dialplan example :

 [from-extern]
 exten = _0141981242,1,AGI(/usr/local/bin/set_name_incoming_timeout.sh)
 same = n,Dial(SIP/10, 30)
 same = n,Answer
 same = n,Voicemail(10@default,u)
 same = n,Hangup

 2) OUTGOING CALLS
 When executed from the dialplan on an outgoing call, it will
 lookup in Odoo the name corresponding to the phone number
 that is called by the user and it will update the name of the
 callee on the screen of the phone of the caller.

 For that, it uses the CONNECTEDLINE dialplan function of Asterisk
 See the following page for more info:
 https://wiki.asterisk.org/wiki/display/AST/Manipulating+Party+ID+Information

 It is not possible to set the CONNECTEDLINE directly from an AGI script,
 (at least not with Asterisk 11) so the AGI script sets a variable
 "connectedlinename" that can then be read from the dialplan and passed
 as parameter to the CONNECTEDLINE function.

 Here is the code that I used on the pre-process subroutine
 "odoo-out-call" of the Outgoing Call of my Xivo server :

 [odoo-out-call]
 exten = s,1,AGI(/var/lib/asterisk/agi-bin/set_name_outgoing_timeout.sh)
 same = n,Set(CONNECTEDLINE(name,i)=${connectedlinename})
 same = n,Set(CONNECTEDLINE(name-pres,i)=allowed)
 same = n,Set(CONNECTEDLINE(num,i)=${XIVO_DSTNUM})
 same = n,Set(CONNECTEDLINE(num-pres)=allowed)
 same = n,Return()

 Of course, you should adapt this example to the Asterisk server you are using.

"""

import xmlrpclib
import sys
from optparse import OptionParser
from asterisk import agi as agilib  # pip install pyst2

__author__ = "Alexis de Lattre <alexis.delattre@akretion.com>"
__date__ = "February 2018"
__version__ = "0.6"

# Name that will be displayed if there is no match
# and no geolocalisation. Set it to False if you don't want
# to have a 'not_found_name' when nothing is found
not_found_name = False

# Define command line options
options = [
    {'names': ('-s', '--server'), 'dest': 'server', 'type': 'string',
        'action': 'store', 'default': False,
        'help': 'DNS or IP address of the Odoo server. Default = none '
        '(will not try to connect to Odoo)'},
    {'names': ('-p', '--port'), 'dest': 'port', 'type': 'int',
        'action': 'store', 'default': 8069,
        'help': "Port of Odoo's XML-RPC interface. Default = 8069"},
    {'names': ('-e', '--ssl'), 'dest': 'ssl',
        'help': "Use SSL connections instead of clear connections. "
        "Default = no, use clear XML-RPC or JSON-RPC",
        'action': 'store_true', 'default': False},
    {'names': ('-j', '--jsonrpc'), 'dest': 'jsonrpc',
        'help': "Use JSON-RPC instead of the default protocol XML-RPC. "
        "Default = no, use XML-RPC",
        'action': 'store_true', 'default': False},
    {'names': ('-d', '--database'), 'dest': 'database', 'type': 'string',
        'action': 'store', 'default': 'odoo',
        'help': "Odoo database name. Default = 'odoo'"},
    {'names': ('-u', '--user-id'), 'dest': 'userid', 'type': 'int',
        'action': 'store', 'default': 2,
        'help': "Odoo user ID to use when connecting to Odoo in "
        "XML-RPC. Default = 2"},
    {'names': ('-t', '--username'), 'dest': 'username', 'type': 'string',
        'action': 'store', 'default': 'demo',
        'help': "Odoo username to use when connecting to Odoo in "
        "JSON-RPC. Default = demo"},
    {'names': ('-w', '--password'), 'dest': 'password', 'type': 'string',
        'action': 'store', 'default': 'demo',
        'help': "Password of the Odoo user. Default = 'demo'"},
    {'names': ('-a', '--ascii'), 'dest': 'ascii',
        'action': 'store_true', 'default': False,
        'help': "Convert name from UTF-8 to ASCII. Default = no, keep UTF-8"},
    {'names': ('-n', '--notify'), 'dest': 'notify',
        'action': 'store_true', 'default': False,
        'help': "Notify Odoo users via a pop-up (requires the Odoo "
        "module 'base_phone_popup'). If you use this option, you must pass "
        "the logins of the Odoo users to notify as argument to the "
        "script. Default = no"},
    {'names': ('-g', '--geoloc'), 'dest': 'geoloc',
        'action': 'store_true', 'default': False,
        'help': "Try to geolocate phone numbers unknown to Odoo. This "
        "features requires the 'phonenumbers' Python lib. To install it, "
        "run 'sudo pip install phonenumbers' Default = no"},
    {'names': ('-l', '--geoloc-lang'), 'dest': 'lang', 'type': 'string',
        'action': 'store', 'default': "en",
        'help': "Language in which the name of the country and city name "
        "will be displayed by the geolocalisation database. Use the 2 "
        "letters ISO code of the language. Default = 'en'"},
    {'names': ('-c', '--geoloc-country'), 'dest': 'country', 'type': 'string',
        'action': 'store', 'default': "FR",
        'help': "2 letters ISO code for your country e.g. 'FR' for France. "
        "This will be used by the geolocalisation system to parse the phone "
        "number of the calling party. Default = 'FR'"},
    {'names': ('-o', '--outgoing'), 'dest': 'outgoing',
        'action': 'store_true', 'default': False,
        'help': "Update the Connected Line ID name on outgoing calls via a "
        "call to the Asterisk function CONNECTEDLINE(), instead of updating "
        "the Caller ID name on incoming calls. Default = no."},
    {'names': ('-i', '--outgoing-agi-variable'), 'dest': 'outgoing_agi_var',
        'type': 'string', 'action': 'store', 'default': "extension",
        'help': "Enter the name of the AGI variable (without the 'agi_' "
        "prefix) from which the script will get the phone number dialed by "
        "the user on outgoing calls. For example, with Xivo, you should "
        "specify 'dnid' as the AGI variable. Default = 'extension'"},
    {'names': ('-m', '--max-size'), 'dest': 'max_size', 'type': 'int',
        'action': 'store', 'default': 40,
        'help': "If the name has more characters this maximum size, cut it "
        "to this maximum size. Default = 40"},
]


def geolocate_phone_number(number, my_country_code, lang):
    import phonenumbers
    import phonenumbers.geocoder  # Takes an enormous amount of time...
    res = ''
    phonenum = phonenumbers.parse(number, my_country_code.upper())
    city = phonenumbers.geocoder.description_for_number(phonenum, lang.lower())
    country_code = phonenumbers.region_code_for_number(phonenum)
    # We don't display the country name when it's my own country
    if country_code == my_country_code.upper():
        if city:
            res = city
    else:
        # Convert country code to country name
        country = phonenumbers.geocoder._region_display_name(
            country_code, lang.lower())
        if country and city:
            res = country + ' ' + city
        elif country and not city:
            res = country
    return res


def convert_to_ascii(my_unicode):
    '''Convert to ascii, with clever management of accents (é -> e, è -> e)'''
    import unicodedata
    if isinstance(my_unicode, unicode):
        my_unicode_with_ascii_chars_only = ''.join((
            char for char in unicodedata.normalize('NFD', my_unicode)
            if unicodedata.category(char) != 'Mn'))
        return str(my_unicode_with_ascii_chars_only)
    # If the argument is already of string type, return it with the same value
    elif isinstance(my_unicode, str):
        return my_unicode
    else:
        return False


def main(options, arguments):
    # print 'options = %s' % options
    # print 'arguments = %s' % arguments

    agi = agilib.AGI()

    if options.outgoing:
        phone_number = agi.env['agi_%s' % options.outgoing_agi_var]
        agi.verbose("Dialed phone number is %s" % phone_number)
    else:
        # If we already have a "True" caller ID name
        # i.e. not just digits, but a real name, then we don't try to
        # connect to Odoo or geoloc, we just keep it
        if (
                agi.env.get('agi_calleridname') and
                not agi.env['agi_calleridname'].isdigit() and
                agi.env['agi_calleridname'].lower()
                not in ['asterisk', 'unknown', 'anonymous'] and
                not options.notify):
            agi.verbose(
                "Incoming CallerID name is %s"
                % agi.env['agi_calleridname'])
            agi.verbose("As it is a real name, we do not change it")
            return True

        phone_number = agi.env['agi_callerid']

    if not isinstance(phone_number, str):
        agi.verbose("Phone number is empty")
        exit(0)
    # Match for particular cases and anonymous phone calls
    # To test anonymous call in France, dial 3651 + number
    if not phone_number.isdigit():
        agi.verbose("Phone number (%s) is not a digit" % phone_number)
        exit(0)

    agi.verbose("Phone number = %s" % phone_number)

    if options.notify and not arguments:
        agi.verbose(
            "When using the notify option, you must give arguments "
            "to the script")
        exit(0)

    if options.notify:
        method = 'incall_notify_by_login'
    else:
        method = 'get_name_from_phone_number'

    res = False
    # Yes, this script can be used without "-s odoo_server" !
    if options.server and options.jsonrpc:
        import odoorpc
        proto = options.ssl and 'jsonrpc+ssl' or 'jsonrpc'
        agi.verbose(
            "Starting %s request on Odoo %s:%d database %s username %s" % (
                proto.upper(), options.server, options.port, options.database,
                options.username))
        try:
            odoo = odoorpc.ODOO(options.server, proto, options.port)
            odoo.login(options.database, options.username, options.password)
            if options.notify:
                res = odoo.execute(
                    'phone.common', method, phone_number, arguments)
            else:
                res = odoo.execute('phone.common', method, phone_number)
            agi.verbose("Called method %s" % method)
        except:
            agi.verbose("Could not connect to Odoo in JSON-RPC")
    elif options.server:
        proto = options.ssl and 'https' or 'http'
        agi.verbose(
            "Starting %s XML-RPC request on Odoo %s:%d "
            "database %s user ID %d" % (
                proto, options.server, options.port, options.database,
                options.userid))
        sock = xmlrpclib.ServerProxy(
            '%s://%s:%d/xmlrpc/object'
            % (proto, options.server, options.port))
        try:
            if options.notify:
                res = sock.execute(
                    options.database, options.userid, options.password,
                    'phone.common', method, phone_number, arguments)
            else:
                res = sock.execute(
                    options.database, options.userid, options.password,
                    'phone.common', method, phone_number)
            agi.verbose("Called method %s" % method)
        except:
            agi.verbose("Could not connect to Odoo in XML-RPC")
        # To simulate a long execution of the XML-RPC request
        # import time
        # time.sleep(5)

    # Function to limit the size of the name
    if res:
        if len(res) > options.max_size:
            res = res[0:options.max_size]
    elif options.geoloc:
        # if the number is not found in Odoo, we try to geolocate
        agi.verbose(
            "Trying to geolocate with country %s and lang %s"
            % (options.country, options.lang))
        res = geolocate_phone_number(
            phone_number, options.country, options.lang)
    else:
        # if the number is not found in Odoo and geoloc is off,
        # we put 'not_found_name' as Name
        agi.verbose("Phone number not found in Odoo")
        res = not_found_name

    # All SIP phones should support UTF-8...
    # but in case you have analog phones over TDM
    # or buggy phones, you should use the command line option --ascii
    if options.ascii:
        res = convert_to_ascii(res)

    agi.verbose("Name = %s" % res)
    if res:
        if options.outgoing:
            agi.set_variable('connectedlinename', res)
        else:
            agi.set_callerid('"%s"<%s>' % (res, phone_number))
    return True


if __name__ == '__main__':
    usage = "Usage: get_name_agi.py [options] login1 login2 login3 ..."
    epilog = "Script written by Alexis de Lattre. "
    "Published under the GNU AGPL licence."
    description = "This is an AGI script that sends a query to Odoo. "
    "It can also be used without Odoo to geolocate phone numbers "
    "of incoming calls."
    parser = OptionParser(usage=usage, epilog=epilog, description=description)
    for option in options:
        param = option['names']
        del option['names']
        parser.add_option(*param, **option)
    options, arguments = parser.parse_args()
    sys.argv[:] = arguments
    main(options, arguments)
