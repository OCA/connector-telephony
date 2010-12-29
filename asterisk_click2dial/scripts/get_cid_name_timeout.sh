#! /bin/sh
# Written by Alexis de Lattre <alexis.delattre@akretion.com>

# Example of wrapper for get_cid_name.py which makes sure that the
# script doesn't take too much time to execute

# Limiting the execution time of get_cid_name.py is important because
# the script is designed to be executed at the beginning of each
# incoming phone call... and if the script get stucks, the phone call
# will also get stucks and you will miss a call !

# For Debian Lenny, you need to install the package "timeout"
# For Ubuntu and Debian >= Squeeze, the "timeout" command is shipped in
# the "coreutils" package

# The first argument of the "timeout" command is the maximum execution time
# In this example, we chose 1 second
timeout 1s /usr/local/bin/get_cid_name.py -s openerp.mycompany.com -d erp_prod -u 12 -w "mypasswd"
