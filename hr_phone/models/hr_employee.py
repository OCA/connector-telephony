# -*- coding: utf-8 -*-
# Copyright 2012-2018 Akretion France
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherit = ['hr.employee', 'phone.validation.mixin']
    _phone_name_sequence = 30
    _phone_name_fields = ['work_phone', 'mobile_phone']

    @api.onchange('work_phone')
    def work_phone_change(self):
        if self.work_phone:
            self.work_phone = self.phone_format(self.work_phone)

    @api.onchange('mobile_phone')
    def mobile_phone_change(self):
        if self.mobile_phone:
            self.mobile_phone = self.phone_format(self.mobile_phone)
