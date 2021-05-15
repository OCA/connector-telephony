# Copyright 2012-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class EventRegistration(models.Model):
    _name = 'event.registration'
    _inherit = ['event.registration', 'phone.validation.mixin']
    _phone_name_sequence = 100
    _phone_name_fields = ['phone', 'mobile']

    @api.onchange('phone')
    def phone_change(self):
        if self.phone:
            self.phone = self.phone_format(self.phone)

    @api.onchange('mobile')
    def mobile_change(self):
        if self.mobile:
            self.mobile = self.phone_format(self.mobile)
