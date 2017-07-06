# -*- coding: utf-8 -*-
# Copyright 2017 Eficent - Miquel Raich
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def map_asterisk_type_pjsip_sip(cr):
    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('asterisk_chan_type'),
        'asterisk_chan_type',
        [('PJSIP', 'SIP')],
        table='res_users', write='sql')


@openupgrade.migrate()
def migrate(env, version):
    map_asterisk_type_pjsip_sip(env.cr)
