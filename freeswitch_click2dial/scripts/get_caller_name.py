#!/usr/bin/python
# -*- encoding: utf-8 -*-
"""
 Name lookup in OpenERP for incoming and outgoing calls with an
 FreeSWITCH system

 This script is designed to be used as an WSGI script on the same server
 as OpenERP/Odoo.

 Relevant documentation"
 https://wiki.freeswitch.org/wiki/Mod_cidlookup
 https://freeswitch.org/confluence/display/FREESWITCH/mod_cidlookup

 Apache Configuration:
 Listen 8080
 <VirtualHost *:8080>
     WSGIScriptAlias /wscgi-bin/ /var/www/wscgi-bin/

     ServerAdmin webmaster@localhost
     # ...
 </VirtualHost>


 FreeSWITCH mod_cidlookup configuration:
 <configuration name="cidlookup.conf" description="cidlookup Configuration">
   <settings>
     <param name="url" value="https://openerp.localdomain/wscgi-bin/get_caller_name.py?name=${caller_id_name}&number=${caller_id_number}&notify=1004,1007"/>
     <param name="cache" value="false"/>
   </settings>
 </configuration>

 If you want geoloc, add &geoloc=true to the end (it is going to be slow).
 Notify should be the internal number of the called parties. This should be
 comma (,) delimited, not :_: delimited. It is up to you to format the
 extensions list appropriately. The persons who are at extensions in the
 notify list will receive a poppup if so configured and if they are logged in.
 The notify list actually shouldn't be in the cidlookup.conf, but should be
 used when doing notify (in an on answer hook for example).

 From the dialplan, do something like this <action application="set"
 data="effective_caller_id_name=${cidlookup(${caller_id_number})}"/>.
 If you are not using FreeTDM modules for the incoming line, doing
 <action application="pre_answer"/> before the cidlookup is a VERY good idea.

 If you are wishing to set the callee name, <action application="export"
 data="callee_id_name=${cidlookup($1)}" />

 Of course, you should adapt this example to the FreeSWITCH server you are
 using. This is especially true of the options variable in the application
 function. The user (by number id, not name) that is used to connect to
 OpenERP/Odoo must have "Phone CallerID" access rights. That may also require
 "Technical Features" rights.

"""

__author__ = "Trever Adams <trever.adams@gmail.com>"
__date__ = "May 2016"
__version__ = "0.5"

#  Copyright (C) 2014-2015 Trever L. Adams <trever.adams@gmail.com>
#  Copyright (C) 2010-2014 Alexis de Lattre <alexis.delattre@akretion.com>
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

import sys
sys.path.append('.')
import xmlrpclib
from cgi import parse_qs, escape
import unicodedata


# Name that will be displayed if there is no match
# and no geolocalisation
not_found_name = "Not in OpenERP"

# Set to 1 for debugging output
verbose = 0


def stdout_write(string):
    '''Wrapper on sys.stdout.write'''
    if verbose == 1:
        sys.stdout.write(string)
        sys.stdout.flush()
    return True


def stderr_write(string):
    '''Wrapper on sys.stderr.write'''
    if verbose == 1:
        sys.stderr.write(string)
        sys.stderr.flush()
    return True


def geolocate_phone_number(number, my_country_code, lang):
    import phonenumbers
    from phonenumbers import geocoder
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


def main(name, phone_number, options):
    # print 'options = %s' % options

    # If we already have a "True" caller ID name
    # i.e. not just digits, but a real name, then we don't try to
    # connect to OpenERP or geoloc, we just keep it
    if (
            name and
            not name.isdigit() and
            name.lower()
            not in ['freeswitch', 'unknown', 'anonymous', 'unavailable']):
        stdout_write('Incoming CallerID name is %s\n' % name)
        stdout_write('As it is a real name, we do not change it\n')
        return name

    if not isinstance(phone_number, str):
        stdout_write('Phone number is empty\n')
        exit(0)
    # Match for particular cases and anonymous phone calls
    # To test anonymous call in France, dial 3651 + number
    if not phone_number.isdigit():
        stdout_write(
            'Phone number (%s) is not a digit\n' % phone_number)
        exit(0)

    stdout_write('Phone number = %s\n' % phone_number)

    res = name
    # Yes, this script can be used without "-s openerp_server" !
    if options["server"]:
        if options["ssl"]:
            stdout_write(
                'Starting XML-RPC secure request on OpenERP %s:%s\n'
                % (options["server"], str(options["port"])))
            protocol = 'https'
        else:
            stdout_write(
                'Starting clear XML-RPC request on OpenERP %s:%s\n'
                % (options["server"], str(options["port"])))
            protocol = 'http'

        sock = xmlrpclib.ServerProxy(
            '%s://%s:%s/xmlrpc/object'
            % (protocol, options["server"], str(options["port"])))

        try:
            if options["notify"]:
                res = sock.execute(
                    options["database"], options["user"], options["password"],
                    'phone.common', 'incall_notify_by_extension',
                    phone_number, options["notify"])
                stdout_write('Calling incall_notify_by_extension\n')
            else:
                res = sock.execute(
                    options["database"], options["user"], options["password"],
                    'phone.common', 'get_name_from_phone_number',
                    phone_number)
                stdout_write('Calling get_name_from_phone_number\n')
            stdout_write('End of XML-RPC request on OpenERP\n')
            if not res:
                stdout_write('Phone number not found in OpenERP\n')
        except:
            stdout_write('Could not connect to OpenERP %s\n'
                         % options["database"])
            res = False
        # To simulate a long execution of the XML-RPC request
        # import time
        # time.sleep(5)

    # Function to limit the size of the name
    if res:
        if len(res) > options["max_size"]:
            res = res[0:options["max_size"]]
    elif options["geoloc"]:
        # if the number is not found in OpenERP, we try to geolocate
        stdout_write(
            'Trying to geolocate with country %s and lang %s\n'
            % (options["country"], options["lang"]))
        res = geolocate_phone_number(
            phone_number, options["country"], options["lang"])
    else:
        # if the number is not found in OpenERP and geoloc is off,
        # we put 'not_found_name' as Name
        res = not_found_name

    # All SIP phones should support UTF-8...
    # but in case you have analog phones over TDM
    # or buggy phones, you should use the command line option --ascii
    if options["ascii"]:
        res = convert_to_ascii(res)

    stdout_write('Name = %s\n' % res)
    return res


def application(environ, start_response):
    output = ""
    name = False
    options = {}
    options["server"] = "127.0.0.1"
    options["port"] = 8069
    options["database"] = "test"
    options["user"] = 1
    options["password"] = "admin"
    options["geoloc"] = True
    options["country"] = "US"
    options["lang"] = "en"
    options["ssl"] = False
    options["ascii"] = True
    options["max_size"] = 40
    parameters = parse_qs(environ.get('QUERY_STRING', ''))
    if 'number' in parameters:
        number = escape(parameters['number'][0])
    if 'name' in parameters:
        name = escape(parameters['name'][0])
    if 'notify' in parameters:
        options["notify"] = []
        for item in parameters['notify'][0].split(','):
            options["notify"].append(escape(item))
        stdout_write(
            'Trying to notify %s\n' % options["notify"])
    else:
        options["notify"] = False
    if 'geoloc' in parameters:
        options["geoloc"] = True
    else:
        options["geoloc"] = False
    output += main(name if name else False, number, options)

    status = '200 OK'
    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    return [output]
