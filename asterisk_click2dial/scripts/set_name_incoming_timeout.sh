#! /bin/sh
# -*- encoding: utf-8 -*-
#
# Written by Alexis de Lattre <alexis.delattre@akretion.com>

# Example of wrapper for set_name_agi.py which makes sure that the
# script doesn't take too much time to execute

# Limiting the execution time of set_name_agi.py is important because
# the script is designed to be executed at the beginning of each
# incoming or outgoing phone call... and if the script get stucks, the
# phone call will also get stucks !

# For Ubuntu >= Maverick and Debian >= Squeeze, the "timeout" command is shipped
# in the "coreutils" package

# The first argument of the "timeout" command is the maximum execution time
# In this example, we chose 2 seconds. Note that geolocalisation takes about
# 1 second on an small machine ; so if you enable the --geoloc option,
# don't put a 1 sec timeout !
# NOTE : with recent version of the phonenumbers lib, the loading time
# is extremely high, about 3 seconds ! I don't know if it's a bug
# or if it will stay like that.

PATH=/usr/local/sbin:/usr/local/bin:/var/lib/asterisk/agi-bin:/sbin:/bin:/usr/sbin:/usr/bin:/usr/share/asterisk/agi-bin:.

timeout 2s set_name_agi.py --jsonrpc --ssl --server odoo.mycompany.com --database erp_prod --username "asterisk" --password "thepasswd"
