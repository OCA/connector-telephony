#! /usr/bin/python
# -*- encoding: utf-8 -*-
"""
 CallerID name lookup in OpenERP for Asterisk IPBX

 When executed from the dialplan on an incoming phone call, it will lookup in
 OpenERP's partner addresses, and, if it finds the phone number, it will get the
 corresponding name of the person and use this name as CallerID name for the incoming call.

 Requires the "asterisk_click2dial" module 
 available from https://code.launchpad.net/openerp-asterisk-connector
 for OpenERP version >= 5.0

 This script is designed to be used as an AGI on an Asterisk IPBX...
 BUT I advise you to use a wrapper around this script to control the
 execution time. Why ? Because if the script takes too much time to
 execute or get stucks (in the XML-RPC request for example), then the
 incoming phone call will also get stucks and you will miss a call !
 The simplest solution I found is to use the "timeout" shell command to
 call this script, for example :

 # timeout 1s get_cid_name.py <OPTIONS>

 See my sample wrapper "get_cid_name_timeout.sh"

 Asterisk dialplan example :

 [from-extern]
 exten => _0141981242,1,AGI(/usr/local/bin/get_cid_name_timeout.sh)
 exten => _0141981242,n,Dial(SIP/10, 30)
 exten => _0141981242,n,Answer()
 exten => _0141981242,n,Voicemail(10@default,u)
 exten => _0141981242,n,Hangup()

 It's probably a good idea to create a user in OpenERP dedicated to this task.
 This user only needs to be part of the group "Asterisk CallerID", which has
 read access on the 'res.partner.address' object, nothing more.

 Note that this script can be used without OpenERP, with just the geolocalisation
 feature : for that, don't use option --server ; only use --geoloc
"""

__author__ = "Alexis de Lattre <alexis.delattre@akretion.com>"
__date__ = "December 2010"
__version__ = "0.2"

#  Copyright (C) 2010-2012 Alexis de Lattre <alexis.delattre@akretion.com>
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

import xmlrpclib
import sys
from optparse import OptionParser


# CID Name that will be displayed if there is no match in res.partner.address
# and no geolocalisation
default_cid_name = "Not in OpenERP"

# Define command line options
option_server = {'names': ('-s', '--server'), 'dest': 'server', 'type': 'string', 'help': 'DNS or IP address of the OpenERP server. Default = none (will not try to connect to OpenERP)', 'action': 'store', 'default': False}
option_port = {'names': ('-p', '--port'), 'dest': 'port', 'type': 'int', 'help': "Port of OpenERP's XML-RPC interface. Default = 8069", 'action': 'store', 'default': 8069}
option_ssl = {'names': ('-e', '--ssl'), 'dest': 'ssl', 'help': "Use XML-RPC secure i.e. with SSL instead of clear XML-RPC. Default = no, use clear XML-RPC", 'action': 'store_true', 'default': False}
option_database = {'names': ('-d', '--database'), 'dest': 'database', 'type': 'string', 'help': "OpenERP database name. Default = 'openerp'", 'action': 'store', 'default': 'openerp'}
option_user = {'names': ('-u', '--user-id'), 'dest': 'user', 'type': 'int', 'help': "OpenERP user ID to use when connecting to OpenERP. Default = 2", 'action': 'store', 'default': 2}
option_password = {'names': ('-w', '--password'), 'dest': 'password', 'type': 'string', 'help': "Password of the OpenERP user. Default = 'demo'", 'action': 'store', 'default': 'demo'}
option_ascii = {'names': ('-a', '--ascii'), 'dest': 'ascii', 'help': "Convert name from UTF-8 to ASCII. Default = no, keep UTF-8", 'action': 'store_true', 'default': False}
option_geoloc = {'names': ('-g', '--geoloc'), 'dest': 'geoloc', 'help': "Try to geolocate phone numbers unknown to OpenERP. This features requires the 'phonenumbers' Python lib. To install it, run 'sudo pip install phonenumbers' Default = no", 'action': 'store_true', 'default': False}
option_geoloc_lang = {'names': ('-l', '--geoloc-lang'), 'dest': 'lang', 'help': "Language in which the name of the country and city name will be displayed by the geolocalisation database. Use the 2 letters ISO code of the language. Default = 'en'", 'action': 'store', 'default': "en"}
option_geoloc_country = {'names': ('-c', '--geoloc-country'), 'dest': 'country', 'help': "2 letters ISO code for your country e.g. 'FR' for France. This will be used by the geolocalisation system to parse the phone number of the calling party. Default = 'FR'", 'action': 'store', 'default': "FR"}

options = [option_server, option_port, option_ssl, option_database, option_user, option_password, option_ascii, option_geoloc, option_geoloc_lang, option_geoloc_country]

def stdout_write(string):
    '''Wrapper on sys.stdout.write'''
    sys.stdout.write(string.encode(sys.stdout.encoding or 'utf-8', 'replace'))
    sys.stdout.flush()
    # When we output a command, we get an answer "200 result=1" on stdin
    # Purge stdin to avoid these Asterisk error messages :
    # utils.c ast_carefulwrite: write() returned error: Broken pipe
    input_line = sys.stdin.readline()
    return True

def stderr_write(string):
    '''Wrapper on sys.stderr.write'''
    sys.stderr.write(string.encode(sys.stdout.encoding or 'utf-8', 'replace'))
    sys.stdout.flush()
    return True

def geolocate_phone_number(number, my_country_code, lang):
    import phonenumbers
    import phonenumbers.geocoder
    res = ''
    phonenum = phonenumbers.parse(number, my_country_code.upper())
    city = phonenumbers.area_description_for_number(phonenum, lang.lower())
    #country = phonenumbers.country_name_for_number(phonenum, lang.lower())
    country_code = phonenumbers.region_code_for_number(phonenum)
    if country_code == my_country_code.upper():
    # We don't display the country name when it's my own country
        if city:
            res = city
    else:
        # Convert country code to country name
        country = phonenumbers.geocoder._region_display_name(country_code, lang.lower())
        if country and city:
            res = country + ' ' + city
        elif country and not city:
            res = country
    return res

def reformat_phone_number_before_query_openerp(number):
    '''We match only on the end of the phone number'''
    if len(number) >= 9:
        return number[-9:len(number)] # Take 9 last numbers
    else:
        return number

def convert_to_ascii(my_unicode):
    '''Convert to ascii, with clever management of accents (é -> e, è -> e)'''
    import unicodedata
    if isinstance(my_unicode, unicode):
        my_unicode_with_ascii_chars_only = ''.join((char for char in unicodedata.normalize('NFD', my_unicode) if unicodedata.category(char) != 'Mn'))
        return str(my_unicode_with_ascii_chars_only)
    # If the argument is already of string type, we return it with the same value
    elif isinstance(my_unicode, str):
        return my_unicode
    else:
        return False

def main(options, arguments):
    #print 'options = %s' % options
    #print 'arguments = %s' % arguments

    # AGI passes parameters to the script on standard input
    stdinput = {}
    while 1:
        input_line = sys.stdin.readline()
        if not input_line:
            break
        line = input_line.strip()
        try:
            variable, value = line.split(':')
        except:
             break
        if variable[:4] != 'agi_': # All AGI parameters start with 'agi_'
            stderr_write("bad stdin variable : %s\n" % variable)
            continue
        variable = variable.strip()
        value = value.strip()
        if variable and value:
            stdinput[variable] = value
    stderr_write("full AGI environnement :\n")

    for variable in stdinput.keys():
        stderr_write("%s = %s\n" % (variable, stdinput.get(variable)))

    input_cid_number = stdinput.get('agi_callerid')
    stderr_write('stdout encoding = %s\n' % sys.stdout.encoding or 'utf-8')

    if not isinstance(input_cid_number, str):
        stdout_write('VERBOSE "CallerID number is empty"\n')
        exit(0)
    # Match for particular cases and anonymous phone calls
    # To test anonymous call in France, dial 3651 + number
    if not input_cid_number.isdigit():
        stdout_write('VERBOSE "CallerID number (%s) is not a digit"\n' % input_cid_number)
        exit(0)

    stdout_write('VERBOSE "CallerID number = %s"\n' % input_cid_number)

    res = False
    if options.server: # Yes, this script can be used without "-s openerp_server" !
        query_number = reformat_phone_number_before_query_openerp(input_cid_number)
        stderr_write("phone number sent to OpenERP = %s\n" % query_number)
        if options.ssl:
            stdout_write('VERBOSE "Starting XML-RPC secure request on OpenERP %s:%s"\n' % (options.server, str(options.port)))
            protocol = 'https'
        else:
            stdout_write('VERBOSE "Starting clear XML-RPC request on OpenERP %s:%s"\n' % (options.server, str(options.port)))
            protocol = 'http'

        sock = xmlrpclib.ServerProxy('%s://%s:%s/xmlrpc/object' % (protocol, options.server, str(options.port)))

        try:
            res = sock.execute(options.database, options.user, options.password, 'res.partner.address', 'get_name_from_phone_number', query_number)
            stdout_write('VERBOSE "End of XML-RPC request on OpenERP"\n')
            if not res:
                stdout_write('VERBOSE "Phone number not found in OpenERP"\n')
        except:
            stdout_write('VERBOSE "Could not connect to OpenERP"\n')
            res = False
        # To simulate a long execution of the XML-RPC request
        #import time
        #time.sleep(5)

    # Function to limit the size of the CID name to 40 chars
    if res:
        if len(res) > 40:
            res = res[0:40]
    elif options.geoloc:
        # if the number is not found in OpenERP, we try to geolocate
        stdout_write('VERBOSE "Trying to geolocate with country %s and lang %s"\n' % (options.country, options.lang))
        res = geolocate_phone_number(input_cid_number, options.country, options.lang)
    else:
        # if the number is not found in OpenERP and geoloc is off, we put 'default_cid_name' as CID Name
        res = default_cid_name

    # All SIP phones should support UTF-8... but in case you have analog phones over TDM
    # or buggy phones, you should use the command line option --ascii
    if options.ascii:
        res = convert_to_ascii(res)

    stdout_write('VERBOSE "CallerID Name = %s"\n' % res)
    stdout_write('SET CALLERID "%s"<%s>\n' % (res, input_cid_number))
    return True

if __name__ == '__main__':
    parser = OptionParser()
    for option in options:
        param = option['names']
        del option['names']
        parser.add_option(*param, **option)
    options, arguments = parser.parse_args()
    sys.argv[:] = arguments
    main(options, arguments)
