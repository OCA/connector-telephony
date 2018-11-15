# -*- coding: utf-8 -*-
# Copyright (C) 2014-2018 Akretion France
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http


class BasePhoneController(http.Controller):
    @http.route('/base_phone/click2dial', type='json', auth='user')
    def click2dial(self, phone_number, click2dial_model, click2dial_id):
        res = http.request.env['phone.common'].with_context(
            click2dial_model=click2dial_model,
            click2dial_id=click2dial_id).click2dial(phone_number)
        return res
