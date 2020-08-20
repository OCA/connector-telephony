# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright (C) 2011 SYLEAM (<http://syleam.fr/>)
# Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
# Copyright (C) 2015 Valentin Chemiere <valentin.chemiere@akretion.com>
# Copyright (C) 2015 Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields

PRIORITY_LIST = [
    ('0', '0'),
    ('1', '1'),
    ('2', '2'),
    ('3', '3')
]

CLASSES_LIST = [
    ('0', 'Flash'),
    ('1', 'Phone display'),
    ('2', 'SIM'),
    ('3', 'Toolkit')
]


class SmsAbstract(models.AbstractModel):
    _name = 'sms.abstract'
    _description = 'SMS Abstract Model'
    mobile = fields.Char()
    gateway_id = fields.Many2one(
        comodel_name='sms.gateway',
        string='SMS Gateway'
    )
    code = fields.Char('Verification Code')
    classes = fields.Selection(
        selection=CLASSES_LIST, string='Class',
        default='1',
        help='The SMS class')
    deferred = fields.Integer(
        help='The time -in minute(s)- to wait before sending the message.')
    priority = fields.Selection(
        selection=PRIORITY_LIST, string='Priority', default='3',
        help='The priority of the message')
    coding = fields.Selection(selection=[
        ('1', '7 bit'),
        ('2', 'Unicode')
        ], string='Coding',
        help='The SMS coding: 1 for 7 bit (160 chracters max'
             'length) or 2 for unicode (70 characters max'
             'length)',
        default='1'
    )
    tag = fields.Char('Tag', help='an optional tag')
    nostop = fields.Boolean(
        default=True,
        help='Do not display STOP clause in the message, this requires that '
             'this is not an advertising message.')
    validity = fields.Integer(
        default=10,
        help="The maximum time - in minute(s) - before the message "
             "is dropped.")

    char_limit = fields.Integer(string='Character Limit', default=160)
    default_gateway = fields.Boolean()
    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env['res.company']._company_default_get(
            'sms.abstract'
        ),
    )
