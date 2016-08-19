#! /bin/sh

PATH=/usr/local/sbin:/usr/local/bin:/var/lib/asterisk/agi-bin:/sbin:/bin:/usr/sbin:/usr/bin:/usr/share/asterisk/agi-bin:.

timeout 10s asterisk_logcall.py --server localhost --database 9.0-test --user-id 1 --password "admin"
