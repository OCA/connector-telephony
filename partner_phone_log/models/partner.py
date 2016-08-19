# -*- coding: utf-8 -*-
# (c) 2016 credativ ltd. - Ondřej Kuzník
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    phonecall_ids = fields.One2many('crm.phonecall', 'partner_id')
