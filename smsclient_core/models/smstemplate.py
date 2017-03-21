# coding: utf-8
# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
# Copyright (C) 2015 Valentin Chemiere <valentin.chemiere@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models, fields


class email_template(models.Model):
    _inherit = "mail.template"

    sms_template = fields.Boolean('SMS Template')
    mobile_to = fields.Char('To (Mobile)')
    gateway_id = fields.Many2one('sms.gateway', 'SMS Gateway')
