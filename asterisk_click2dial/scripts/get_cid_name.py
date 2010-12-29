#! /usr/bin/python
# -*- encoding: utf-8 -*-
"""
 CallerID name lookup in OpenERP for Asterisk IPBX

 When executed from the dialplan on an incoming phone call, it will lookup in
 OpenERP's partner addresses, and, if it finds the phone number, it will get the
 corresponding name of the person and use this name as CallerID name for the incoming call.

 Requires the "asterisk_click2dial" module (available in the extra-addons)
 on OpenERP version >= 5

 This script is designed to be used as an AGI on an Asterisk IPBX...
 BUT I advise you to use a wrapper around this script to control the
 execution time. Why ? Because if the script takes too much time to
 execute or get stucks (in the XML-RPC request for example), then the
 incoming phone call will also get stucks and you will miss a call !
 The most simple solution I found is to use the "timeout" shell command to
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
"""

__author__ = "Alexis de Lattre <alexis.delattre@akretion.com>"
__date__ = "December 2010"
__version__ = "0.1"

#  Copyright (C) 2010 Alexis de Lattre <alexis.delattre@akretion.com>
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
default_cid_name = "Not in OpenERP"

# Define command line options
option_server = {'names': ('-s', '--server'), 'dest': 'server', 'type': 'string', 'help': 'DNS or IP address of the OpenERP server', 'action': 'store', 'default':'localhost'}
option_port = {'names': ('-p', '--port'), 'dest': 'port', 'type': 'int', 'help': "Port of OpenERP's XML-RPC interface", 'action': 'store', 'default': 8069}
option_database = {'names': ('-d', '--database'), 'dest': 'database', 'type': 'string', 'help': "OpenERP database name", 'action': 'store', 'default': 'openerp'}
option_user = {'names': ('-u', '--user-id'), 'dest': 'user', 'type': 'int', 'help': "OpenERP user ID to use when connecting to OpenERP", 'action': 'store', 'default': 2}
option_password = {'names': ('-w', '--password'), 'dest': 'password', 'type': 'string', 'help': "Password of the OpenERP user", 'action': 'store', 'default': 'demo'}

options = [option_server, option_port, option_database, option_user, option_password]


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
        input_line = sys.stdin.readline().strip()
        if input_line == '':
            break
        variable, value = input_line.split(':') # TODO à protéger !
        if variable[:4] != 'agi_': # All AGI parameters start with 'agi_'
            sys.stderr.write("Bad stdin variable : %s\n" % variable)
            continue
        variable = variable.strip()
        value = value.strip()
        if variable != '':
            stdinput[variable] = value
    sys.stderr.write("Full AGI environnement :\n")
    for variable in stdinput.keys():
        sys.stderr.write("%s = %s\n" % (variable, stdinput[variable]))

    input_cid_number = stdinput.get('agi_callerid', False)

    if not isinstance(input_cid_number, str):
        exit(0)
    # Match for particular cases and anonymous phone calls
    # To test anonymous call in France, dial 3651 + number
    if not input_cid_number.isdigit():
        sys.stdout.write('VERBOSE "CallerID number (%s) is not a digit"\n' % input_cid_number)
        sys.stdout.flush()
        exit(0)

    sys.stdout.write('VERBOSE "CallerID number = %s"\n' % input_cid_number)
    query_number = reformat_phone_number_before_query_openerp(input_cid_number)
    sys.stderr.write("phone number sent to OpenERP = %s\n" % query_number)

    sys.stdout.write('VERBOSE "Starting XML-RPC request on OpenERP %s:%s"\n' % (options.server, str(options.port)))
    sys.stdout.flush()

    sock = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/object' % (options.server, str(options.port)))

    res = sock.execute(options.database, options.user, options.password, 'res.partner.address', 'get_name_from_phone_number', query_number)
    # To simulate a long execution of the XML-RPC request
    #import time
    #time.sleep(5)

    sys.stdout.write('VERBOSE "End of XML-RPC request on OpenERP"\n')
    sys.stdout.flush()

    # Function to limit the size of the CID name to 40 chars
    if res:
        if len(res) > 40:
            res = res[0:40]
    else:
        # if the number is not found in OpenERP, we put 'default_cid_name' as CID Name
        res = default_cid_name

    # I am not sure how SIP and IP phones manage non-ASCII caracters, so I prefer
    # to replace all non-ASCII caracters in the name
    res_ascii = convert_to_ascii(res)

    sys.stdout.write('VERBOSE "CallerID Name = %s"\n' % res_ascii)
    sys.stdout.flush()
    sys.stdout.write('SET CALLERID "%s" <%s>\n' % (res_ascii, input_cid_number))
    sys.stdout.flush()

if __name__ == '__main__':
    parser = OptionParser()
    for option in options:
        param = option['names']
        del option['names']
        parser.add_option(*param, **option)
    options, arguments = parser.parse_args()
    sys.argv[:] = arguments
    main(options, arguments)
