# Copyright (C) 2019 Open Source Integrators
# <https://www.opensourceintegrators.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

VOICENT_CONTACT_COLUMNS = [('Assigned To', 'Assigned To'),
                           ('Business', 'Business'),
                           ('Category', 'Category'),
                           ('Contact Status', 'Contact Status'),
                           ('Email', 'Email'),
                           ('First Name', 'First Name (Required)'),
                           ('Last Name', 'Last Name'),
                           ('Lead Source', 'Lead Source'),
                           ('Other', 'Other'),
                           ('Phone', 'Phone (Required)')]

VOICENT_REPLY = [('availableagents', 'Available Agents'),
                 ('callback', 'Callback'),
                 ('campid', 'Campaign ID'),
                 ('campname', 'Campaign Name'),
                 ('campsize', 'Campaign Size'),
                 ('connected', 'Connected'),
                 ('dnc', 'Contact DNC'),
                 ('nophone', 'Contact No Phone'),
                 ('disc', 'Disc. Number'),
                 ('dropped', 'Dropped'),
                 ('failed', 'Failed'),
                 ('fax', 'Fax'),
                 ('info', 'Info'),
                 ('in', 'Interested'),
                 ('lines', 'Lines'),
                 ('linebusy', 'Line Busy'),
                 ('live', 'Live Answer'),
                 ('machine', 'Machine Answer'),
                 ('made', 'Made'),
                 ('maxlines', 'Max Lines'),
                 ('noact', 'No Activity'),
                 ('noanswer', 'No Answer'),
                 ('notin', 'Not Interested'),
                 ('notes', 'Notes'),
                 ('optout', 'Opt Out'),
                 ('serverr', 'Service Error'),
                 ('status', 'Status'),
                 ('totalagents', 'Total Agents'),
                 ('wit', 'Wit')]

MSGTYPE = [('audio', 'Audio'),
           ('ivr', 'IVR'),
           ('survey', 'Survey'),
           ('template', 'Template'),
           ('tts', 'Text-To-Speech')]


class BackendVoicentCallLine(models.Model):
    _name = 'backend.voicent.call.line'
    _description = 'Voicent Backend Call Line'

    name = fields.Char(string='Name', required=True)
    sequence = fields.Integer(string='Sequence', default=0)
    applies_on = fields.Selection(string='Applies on', selection=[])
    msgtype = fields.Selection(MSGTYPE, string='Message Type', required=True)
    msginfo = fields.Char(string='Message Info')
    backend_id = fields.Many2one(
        string='Backend',
        comodel_name='backend.voicent',
        ondelete='set null')
    reply_ids = fields.One2many('backend.voicent.call.line.reply', 'line_id',
                                string="Replies")
    contact_ids = fields.One2many('backend.voicent.call.line.contact',
                                  'line_id',
                                  string="Contact Info")


class BackendVoicentCallLineContact(models.Model):
    _name = 'backend.voicent.call.line.contact'
    _description = 'Columns of the CSV file to provide the contact list'
    _order = 'sequence'

    name = fields.Selection(VOICENT_CONTACT_COLUMNS, string='Voicent Field',
                            required=True)
    other = fields.Char(string='Other')
    sequence = fields.Integer(string='Sequence', default=0)
    field_domain = fields.Char(string='Odoo Field',
                               required=True)
    default_value = fields.Char(string='Default Value', required=True)
    line_id = fields.Many2one(
        string='Call Line',
        comodel_name='backend.voicent.call.line',
        ondelete='set null')


class BackendVoicentCallLineReply(models.Model):
    _name = 'backend.voicent.call.line.reply'
    _description = 'Reply to a Voicent Call'

    name = fields.Char(string='Name', required=True)
    line_id = fields.Many2one(
        string='Call Line',
        comodel_name='backend.voicent.call.line',
        ondelete='set null')
    reply_field = fields.Selection(VOICENT_REPLY, string="Voicent Reply Field",
                                   required=True)
    reply_value = fields.Char(string="Voicent Reply Value", required=True)
    action_id = fields.Many2one('ir.actions.server', string="Server Action",
                                required=True,
                                help="""If the Voicent reply field is equal to
                                the Voicent reply value, the server action is
                                executed.""")
