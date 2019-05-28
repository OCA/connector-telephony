# Copyright (C) 2019 Open Source Integrators
# <https://www.opensourceintegrators.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QueueJob(models.Model):
    """ Job status and result """
    _inherit = 'queue.job'

    state = fields.Selection(
        selection_add=[('waiting_voicent_status',
                        'Waiting Voicent Status')])
