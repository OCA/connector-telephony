# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Dave Lasley <dave@laslabs.com>
#    Copyright: 2015 LasLabs Inc..
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import http


class DataException(Exception):
    error = None
    description = None
    status = 500
    headers = {}

    def __init__(self):
        super(DataException, self).__init__(self.error)

    def to_dict(self):
        return {
            'error': self.error,
            'error_description': self.description,
        }


class AuthenticationException(Exception):
    error = None
    description = None
    status = 400
    headers = {}

    def __init__(self):
        super(AuthenticationException, self).__init__(self.error)

    def to_dict(self):
        return {
            'error': self.error,
            'error_description': self.description,
        }


class InvalidTokenException(AuthenticationException):
    status = 403
    error = 'invalid_token'
    description = 'Invalid token provided in request'
    

class MultipleTransmissionException(DataException):
    error = 'multiple_transmission'
    description = 'Multiple transmissions found matching provided FaxID'


class NoTransmissionException(DataException):
    status = 404
    error = 'no_transmission'
    description = 'No transmission found matching provided FaxID'


class NoOperationException(DataException):
    error = 'noop_error'
    description = 'Server error, no operation was triggered'


class FaxSfaxCallback(http.Controller):

    def throw_error(self, exception):
        return self.response(
            exception.to_dict,
            exception.status,
            exception.headers,
        )

    @http.route('/fax/sfax/callback', type='json', auth='none')
    def do_callback(self, token, **kwargs):
        
        transmission_mdl = http.request.env['fax.payload.transmission']
        transmission_id = transmission_mdl.search([
            ('response_num', '=', kwargs['faxid'])
        ])
        
        if len(transmission_id) > 1:
            return self.throw_error(MultipleTransmissionException())
        
        if len(transmission_id) == 0:
            sfax_ids = http.request.env['fax.adapter.sfax'].search([])
        else:
            sfax_ids = transmission_id.adapter_id
            
        sfax_id = None
        for sfax in sfax_ids:
            if sfax._get_adapter().validate_token(token):
                sfax_id = sfax
                break
        
        if sfax_id is None:
            return self.throw_error(AuthenticationException())
        
        if kwargs.get('outfromfaxnumber'):
            return self.process_out_fax(sfax_id, transmission_id, kwargs)
        else:
            return self.process_in_fax(sfax_id, transmission_id, kwargs)
        
        return self.throw_error(NoOperationException())
        
    def process_in_fax(self, sfax_id, transmission_id, vals):
        
        transmission_vals = {
            'local_fax': vals.get('intofaxnumber'),
            'remote_fax': vals.get('infromfaxnumber'),
            'state': 'done' if vals['faxsuccess'] else 'transmit_except',
            'fax_date': field.Datetime.from_string(vals['faxdateiso']),
            'direction': 'in',
            'attempt_num': 1,
            'page_num': vals['faxpages'],
            'status_msg': 'OK',
            'response_num': vals['faxid'],
        }
        
        if len(transmission_id) == 0:
            #   @TODO: Download the payload from server
            sfax_id.write({
                'transmission_ids': [(0, 0, transmission_vals)],
            })
        else:
            transmission_id.write(transmission_vals)
    
    def process_out_fax(self, sfax_id, transmission_id, vals):
        
        transmission_vals = {
            'local_fax': vals.get('outfromfaxnumber'),
            'remote_fax': vals.get('outtofaxnumber'),
            'state': 'done' if vals['faxsuccess'] else 'transmit_except',
            'fax_date': field.Datetime.from_string(vals['faxdateiso']),
            'direction': 'out',
            'attempt_num': vals['outfaxattempts'],
            'page_num': vals['faxpages'],
            'status_msg': vals['outresultdescr'],
            'response_num': vals['faxid'],
        }
        
        if len(transmission_id) == 0:
            #   @TODO: Download the payload from server
            sfax_id.write({
                'transmission_ids': [(0, 0, transmission_vals)],
            })
        else:
            transmission_id.write(transmission_vals)
