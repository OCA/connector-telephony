# -*- coding: utf-8 -*-
# Copyright 2016-2018 Akretion France
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    number_of_digits_to_match_from_end = fields.Integer(
        string='Number of Digits To Match From End',
        default=8,
        help="In several situations, Odoo will have to find a "
        "Partner/Lead/Employee/... from a phone number presented by the "
        "calling party. As the phone numbers presented by your phone "
        "operator may not always be displayed in a standard format, "
        "the best method to find the related Partner/Lead/Employee/... "
        "in Odoo is to try to match the end of the phone number in "
        "Odoo with the N last digits of the phone number presented "
        "by the calling party. N is the value you should enter in this "
        "field.")

    _sql_constraints = [(
        'number_of_digits_to_match_from_end_positive',
        'CHECK (number_of_digits_to_match_from_end > 0)',
        "The value of the field 'Number of Digits To Match From End' must "
        "be positive.")]
