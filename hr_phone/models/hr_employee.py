# -*- coding: utf-8 -*-
# © 2012-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.addons.base_phone.fields import Phone


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _phone_name_sequence = 30

    work_phone = Phone(country_field='country_id')
    mobile_phone = Phone(country_field='country_id')
