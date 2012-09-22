#! /bin/sh
# Written by Alexis de Lattre <alexis.delattre@akretion.com>

# Example of wrapper for get_cid_name.py which makes sure that the
# script doesn't take too much time to execute

# Limiting the execution time of get_cid_name.py is important because
# the script is designed to be executed at the beginning of each
# incoming phone call... and if the script get stucks, the phone call
# will also get stucks and you will miss the call !

# For Debian Lenny and Ubuntu Lucid, you need to install the package "timeout"
# For Ubuntu >= Maverick and Debian >= Squeeze, the "timeout" command is shipped
# in the "coreutils" package

# The first argument of the "timeout" command is the maximum execution time
# In this example, we chose 2 seconds. Note that geolocalisation takes about
# 1 second on an small machine ; so if you enable the --geoloc option,
# don't put a 1 sec timeout !

# To test this script manually (i.e. outside of Asterisk), run :
# echo "agi_callerid:0141981242"|get_cid_name_timeout.sh
# where 0141981242 is a phone number that could be presented by the calling party

timeout 2s /usr/local/bin/get_cid_name.py --server openerp.mycompany.com --database erp_prod --user-id 12 --password "thepasswd" --geoloc --geoloc-country "FR" --geoloc-lang "fr"
