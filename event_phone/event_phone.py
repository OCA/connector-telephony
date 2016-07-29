# -*- coding: utf-8 -*-
# © 2012-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models
from openerp.addons.base_phone.fields import Phone


class EventRegistration(models.Model):
    _inherit = 'event.registration'
    _phone_name_sequence = 100

    phone = Phone(partner_field='partner_id')
