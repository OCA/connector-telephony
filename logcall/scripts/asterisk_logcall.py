#! /usr/bin/python
# -*- encoding: utf-8 -*-
#  Copyright (C) 2010-2015 Alexis de Lattre <alexis.delattre@akretion.com>
#  Copyright (C) 2016 credativ Ltd (<http://credativ.co.uk>).
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
 Log a call and recording within Asterisk

 This is intended to be called by a hangup handler:

 Please, note the start is seconds since EPOCH in UTC, it must be UTC.

 Example:
 [from-pstn-custom]
 ...
 exten => _X!,n,Set(CHANNEL(hangup_handler_push)=from-pstn-hdlr,s,1(args))

 [from-pstn-hdlr]
 exten => s,1,Verbose(0, from-pstn-hdlr called)
  same => n,Set(odoo_type=incoming)
  same => n,Set(odoo_src=${CDR(src)})
  same => n,Set(odoo_dst=${CDR(dst)})
  same => n,Set(odoo_duration=${CDR(duration)})
  same => n,Set(odoo_start=${CDR(start)})
  same => n,Set(odoo_filename=${CDR(recordingfile)})
  same => n,Set(odoo_uniqueid=${UNIQUEID})
  same => n,AGI(/usr/local/bin/asterisk_logcall.sh,${odoo_type},${odoo_src},${odoo_dst},${odoo_duration},${odoo_start},${odoo_filename},${odoo_uniqueid})
  same => n,Return()

 To test from the CLI:
./asterisk_logcall.sh << EOF
agi_arg_1: outgoing
agi_arg_2: 875
agi_arg_3: 01234567890
agi_arg_4: 345
agi_arg_5: 1234567890
agi_arg_6: out-875-unknown-20160216-154438-1455637478.61.wav
agi_arg_7: 1455637478.61
agi_arg_8: Description may include things like hangup cause, transfer, automated notes
EOF

"""

__author__ = "Craig Gowing <craig.gowing@credativ.co.uk> & Alexis de Lattre <alexis.delattre@akretion.com>"
__date__ = "February 2016"
__version__ = "0.2"

import xmlrpclib
import sys
from optparse import OptionParser

# Define command line options
options = [
    {'names': ('-s', '--server'), 'dest': 'server', 'type': 'string',
        'action': 'store', 'default': False,
        'help': 'DNS or IP address of the OpenERP server. Default = none '
        '(will not try to connect to OpenERP)'},
    {'names': ('-p', '--port'), 'dest': 'port', 'type': 'int',
        'action': 'store', 'default': 8069,
        'help': "Port of OpenERP's XML-RPC interface. Default = 8069"},
    {'names': ('-e', '--ssl'), 'dest': 'ssl',
        'help': "Use SSL connections instead of clear connections. "
        "Default = no, use clear XML-RPC or JSON-RPC",
        'action': 'store_true', 'default': False},
    {'names': ('-j', '--jsonrpc'), 'dest': 'jsonrpc',
        'help': "Use JSON-RPC instead of the default protocol XML-RPC. "
        "Default = no, use XML-RPC",
        'action': 'store_true', 'default': False},
    {'names': ('-d', '--database'), 'dest': 'database', 'type': 'string',
        'action': 'store', 'default': 'openerp',
        'help': "OpenERP database name. Default = 'openerp'"},
    {'names': ('-u', '--user-id'), 'dest': 'userid', 'type': 'int',
        'action': 'store', 'default': 2,
        'help': "OpenERP user ID to use when connecting to OpenERP in "
        "XML-RPC. Default = 2"},
    {'names': ('-t', '--username'), 'dest': 'username', 'type': 'string',
        'action': 'store', 'default': 'demo',
        'help': "OpenERP username to use when connecting to OpenERP in "
        "JSON-RPC. Default = demo"},
    {'names': ('-w', '--password'), 'dest': 'password', 'type': 'string',
        'action': 'store', 'default': 'demo',
        'help': "Password of the OpenERP user. Default = 'demo'"},
]

def stdout_write(string):
    '''Wrapper on sys.stdout.write'''
    sys.stdout.write(string.encode(sys.stdout.encoding or 'utf-8', 'replace'))
    sys.stdout.flush()
    # When we output a command, we get an answer "200 result=1" on stdin
    # Purge stdin to avoid these Asterisk error messages :
    # utils.c ast_carefulwrite: write() returned error: Broken pipe
    sys.stdin.readline()
    return True


def stderr_write(string):
    '''Wrapper on sys.stderr.write'''
    sys.stderr.write(string.encode(sys.stdout.encoding or 'utf-8', 'replace'))
    sys.stdout.flush()
    return True

def main(options, arguments):

    # AGI passes parameters to the script on standard input
    stdinput = {}
    while 1:
        input_line = sys.stdin.readline()
        if not input_line:
            break
        line = input_line.strip()
        try:
            variable, value = line.split(':', 1)
        except:
            break
        if variable[:4] != 'agi_':  # All AGI parameters start with 'agi_'
            stderr_write("bad stdin variable : %s\n" % variable)
            continue
        variable = variable.strip()
        value = value.strip()
        if variable and value:
            stdinput[variable] = value
    stderr_write("full AGI environnement :\n")

    for variable in stdinput.keys():
        stderr_write("%s = %s\n" % (variable, stdinput.get(variable)))

    odoo_type = stdinput.get('agi_arg_1', '')
    odoo_src = stdinput.get('agi_arg_2', '')
    odoo_dst = stdinput.get('agi_arg_3', '')
    odoo_duration = stdinput.get('agi_arg_4', '')
    odoo_start = stdinput.get('agi_arg_5', '')
    odoo_filename = stdinput.get('agi_arg_6', '')
    odoo_uniqueid = stdinput.get('agi_arg_7', '')
    odoo_description = stdinput.get('agi_arg_8', '')

    method = 'log_call_and_recording'

    res = False
    # Yes, this script can be used without "-s openerp_server" !
    if options.server and options.jsonrpc:
        import odoorpc
        proto = options.ssl and 'jsonrpc+ssl' or 'jsonrpc'
        stdout_write(
            'VERBOSE "Starting %s request on OpenERP %s:%d database '
            '%s username %s"\n' % (
                proto.upper(), options.server, options.port, options.database,
                options.username))
        try:
            odoo = odoorpc.ODOO(options.server, proto, options.port)
            odoo.login(options.database, options.username, options.password)
            res = odoo.execute(
                'phone.common', 'log_call_and_recording', odoo_type, odoo_src, odoo_dst, odoo_duration, odoo_start, odoo_filename, odoo_uniqueid, odoo_description)
            stdout_write('VERBOSE "Called method %s, returned %s"\n' % (method, res))
        except:
            stdout_write(
                'VERBOSE "Could not connect to OpenERP in JSON-RPC"\n')
    elif options.server:
        proto = options.ssl and 'https' or 'http'
        stdout_write(
            'VERBOSE "Starting %s XML-RPC request on OpenERP %s:%d '
            'database %s user ID %d"\n' % (
                proto, options.server, options.port, options.database,
                options.userid))
        sock = xmlrpclib.ServerProxy(
            '%s://%s:%d/xmlrpc/object'
            % (proto, options.server, options.port))
        try:
            res = sock.execute(
                options.database, options.userid, options.password,
                'phone.common', 'log_call_and_recording', odoo_type, odoo_src, odoo_dst, odoo_duration, odoo_start, odoo_filename, odoo_uniqueid, odoo_description)
            stdout_write('VERBOSE "Called method %s, returned %s"\n' % (method, res))
        except:
            stdout_write('VERBOSE "Could not connect to OpenERP in XML-RPC"\n')

    return True

if __name__ == '__main__':
    usage = "Usage: asterisk_logcall.py [options] login1 login2 login3 ..."
    epilog = "Script written by Craig Gowing based on work by Alexis de Lattre. "
    "Published under the GNU AGPL licence."
    description = "This is an AGI script that sends a query to OpenERP. "
    parser = OptionParser(usage=usage, epilog=epilog, description=description)
    for option in options:
        param = option['names']
        del option['names']
        parser.add_option(*param, **option)
    options, arguments = parser.parse_args()
    sys.argv[:] = arguments
    main(options, arguments)
