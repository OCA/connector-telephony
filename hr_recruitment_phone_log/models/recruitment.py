# -*- coding: utf-8 -*-
# (c) 2016 Trever L. Adams
# (c) 2016 credativ ltd. - Ondřej Kuzník
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api


class CrmPhonecall(models.Model):
    _inherit = "crm.phonecall"

    hr_applicant_id = fields.Many2one(
        'hr.applicant', string='Applicant', ondelete='cascade')


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    phonecall_ids = fields.One2many('crm.phonecall', 'hr_applicant_id',
                                    string='Phone Calls')
    phonecall_count = fields.Integer(
        compute='_compute_count_phonecalls', string='Number of Phonecalls',
        readonly=True)

    @api.multi
    @api.depends('phonecall_ids')
    def _compute_count_phonecalls(self):
        cpo = self.env['crm.phonecall']
        for applicant in self:
            try:
                applicant.phonecall_count = cpo.search_count(
                    [('hr_applicant_id', '=', applicant.id)])
            except:
                applicant.phonecall_count = 0
