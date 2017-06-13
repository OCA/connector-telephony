# -*- coding: utf-8 -*-
# (c) 2016 credativ ltd. - Ondřej Kuzník
# (c) 2016 Trever L. Adams
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api, _
from datetime import datetime, timedelta
from pytz import timezone, utc
import logging


logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    context_auto_log_calls = fields.Boolean(
        string='Automatically Log Incoming Calls', default=True)


class CrmPhonecall(models.Model):
    _inherit = "crm.phonecall"

    end_date = fields.Datetime(
        string='End Date', track_visibility='onchange', copy=False,
        default=lambda self: fields.Datetime.now())
    recording_id = fields.Many2one('ir.attachment', string='Call Recording',
                                   readonly=True)


class PhoneCommon(models.AbstractModel):
    _inherit = 'phone.common'

    @api.model
    def _get_ucp_url(self):
        pass

    @api.model
    def log_call_and_recording(self, odoo_type, odoo_src, odoo_dst,
                               odoo_duration, odoo_start, odoo_filename,
                               odoo_uniqueid, odoo_description):
        phonecall_obj = self.env['crm.phonecall']
        attach_obj = self.env['ir.attachment']
        attach_id = False
        search_field = False

        caller_user, caller_external = (odoo_type == 'incoming' and
                                        (odoo_dst, odoo_src) or
                                        (odoo_src, odoo_dst))

        call_name_prefix = (odoo_type == 'incoming' and "Call from %s" or
                            "Call to %s")

        users = self.env['res.users'].search(
            [('internal_number', '=', caller_user)])

        if not users or not users[0].context_auto_log_calls:
            return False

        tz = users[0].partner_id.tz

        tz = timezone(tz) if tz else utc
        odoo_start = datetime(1970, 1, 1, tzinfo=tz) + \
            timedelta(seconds=float(odoo_start))
        odoo_end = odoo_start + timedelta(seconds=float(odoo_duration))

        phonecall_data = {
            'partner_phone': caller_external,
            'name': call_name_prefix % (caller_external,),
            'opportunity_id': False,
            'partner_id': False,
            'hr_applicant_id': False,
            'end_date': odoo_end,
            'state': 'done',
            'date': odoo_start,
            'direction': 'inbound' if odoo_type == 'incoming' else 'outbound',
            'description': odoo_description
        }

        r = self.get_record_from_phone_number(caller_external)
        if not r:
            logger.warning("No partner found for number %s" % caller_external)
            return phonecall_obj
        elif r[0] == 'res.partner':
            phonecall_data['partner_id'] = r[1]
            search_field = 'partner_id'
            if r[2]:
                phonecall_data['name'] = call_name_prefix % (r[2],)
        elif r[0] == 'crm.lead':
            phonecall_data['opportunity_id'] = r[1]
            search_field = 'opportunity_id'
            if r[2]:
                phonecall_data['name'] = call_name_prefix % (r[2],)
        elif r[0] == 'hr.applicant':
            phonecall_data['hr_applicant_id'] = r[1]
            search_field = 'hr_applicant_id'
            if r[2]:
                phonecall_data['name'] = call_name_prefix % (r[2],)
        record = self.env[r[0]].browse(r[1])

        if users:
            phonecall_data['user_id'] = users[0].id

        jitter = self._get_jitter(users[0])
        jitter_start = datetime.strftime(odoo_start -
                                         timedelta(seconds=float(jitter)),
                                         '%Y-%m-%d %H:%M:%S')
        jitter_end = datetime.strftime(odoo_end +
                                       timedelta(seconds=float(jitter)),
                                       '%Y-%m-%d %H:%M:%S')

        phonecalls = phonecall_obj.search([
            ('date', '>=', jitter_start),
            ('end_date', '<=', jitter_end),
            (search_field, '=', r[1]),
            ('user_id', '=', users[0].id),
            ('direction', '=', phonecall_data['direction'])])

        if phonecalls:
            if (odoo_end.replace(tzinfo=None) <
               datetime.strptime(phonecalls[0]['end_date'],
               '%Y-%m-%d %H:%M:%S')):
                    odoo_end = \
                        phonecalls[0]['end_date'].strptime('%Y-%m-%d %H:%M:%S')
            if (odoo_start.replace(tzinfo=None) >
               datetime.strptime(phonecalls[0]['date'],
               '%Y-%m-%d %H:%M:%S')):
                    odoo_start = \
                        phonecalls[0]['date'].strptime('%Y-%m-%d %H:%M:%S')
            if phonecalls[0]['description']:
                if phonecalls[0]['description'].find(odoo_description) != -1:
                    odoo_description = phonecalls[0]['description'] + '\n' + \
                        odoo_description
                else:
                    odoo_description = phonecalls[0]['description']
            if phonecalls[0]['recording_id']:
                attach_id = phonecalls[0]['recording_id']
            phonecall_id = phonecalls[0]
            phonecalls[0].write({'end_date': odoo_end, 'date': odoo_start,
                                 'description': odoo_description,
                                 'recording_id':
                                 (attach_id.id if attach_id else False)})
        else:
            phonecall_id = phonecall_obj.create(phonecall_data)

        if odoo_filename and not attach_id:
            base_url = self._get_ucp_url(users[0])
            fixed_uuid = odoo_uniqueid.replace('.', '_')
            ir_attachment_data = {
                'res_model': 'crm.phonecall',
                'res_id': phonecall_id.id,
                'name': phonecall_data['name'],
                'type': 'url',
                'mimetype': 'audio/wav',
                'url': base_url.format(caller_user=caller_user,
                                       user_resource=users[0].resource,
                                       odoo_type=odoo_type,
                                       odoo_src=odoo_src,
                                       odoo_dst=odoo_dst,
                                       odoo_duration=odoo_duration,
                                       odoo_start=odoo_start,
                                       odoo_uniqueid=fixed_uuid,
                                       odoo_filename=odoo_filename),
                'datas_fname': odoo_filename,
            }
            attach_id = attach_obj.create(ir_attachment_data)
            phonecall_id.write({'recording_id': attach_id.id})

            message_format = _("Recorded %s call (%%sm)." % odoo_type)
            record.message_post(
                body=message_format % (int(odoo_duration) / 60,),
                message_type='comment',
                attachment_ids=attach_id._ids)

        return phonecall_id.id
