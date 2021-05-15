# Copyright 2012-2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class HrEmployeePrivate(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee', 'phone.validation.mixin']
    _phone_name_sequence = 30
    _phone_name_fields = ['mobile_phone']
    # work_phone is now a computed field that take the value address_id.phone
    # Don't put emergency_phone in _phone_name_fields because it is not a phone
    # number of the employee

    @api.onchange('mobile_phone')
    def mobile_phone_change(self):
        if self.mobile_phone:
            self.mobile_phone = self.phone_format(self.mobile_phone)

    @api.onchange('emergency_phone')
    def emergency_phone_change(self):
        if self.emergency_phone:
            self.emergency_phone = self.phone_format(self.emergency_phone)
