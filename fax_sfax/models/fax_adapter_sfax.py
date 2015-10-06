# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Dave Lasley <dave@laslabs.com>
#    Copyright: 2015 LasLabs, Inc.
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
from openerp import models, fields, api
from .pkcs7 import PKCS7Encoder
from Crypto.Cipher import AES
import requests
import base64
import time
import urllib
import logging


_logger = logging.getLogger(__name__)


class FaxAdapterSfax(models.Model):
    _name = 'fax.adapter.sfax'
    _inherit = 'fax.adapter'
    _description = 'It provides bindings for SFax auth & methods'
    API_ERROR_ID = -1

    @api.one
    def _compute_token(self, ):
        ''' Get security token from SFax '''
        try:
            timestr = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            params = {
                'AppId': self.app_id,
                'AppKey': self.encrypt_key,
                'GenDT': timestr,
                'Client': self.client_ip,
            }
            raw = urllib.urlencode(params) + '&'

            mode = AES.MODE_CBC
            encode_obj = PKCS7Encoder()
            encrypt_obj = AES.new(
                self.encrypt_key, mode, self.vector.encode('ascii')
            )
            padding = encode_obj.encode(raw)
            cipher = encrypt_obj.encrypt(padding)
            enc_cipher = base64.b64encode(cipher)
            self.token = urllib.quote(enc_cipher)

        except Exception as e:
            _logger.warn(
                'Was not able to create security token. Exception: %s', e
            )
            self.token = False

    company_id = fields.Many2one('res.company')
    username = fields.Text(
        required=True,
        help='SFax Username / Security Context for API connection',
    )
    encrypt_key = fields.Text(
        required=True,
        help='SFax PassKey for API connection',
    )
    vector = fields.Text(
        required=True,
        help='SFax Vector for API connection',
    )
    client_ip = fields.Char(
        required=True,
        help='Client IP for API connection',
    )
    app_id = fields.Char(
        required=True,
        help='App ID for this API connection',
    )
    uri = fields.Char(
        required=True,
        default='https://api.sfaxme.com/api',
        help='URI for API (usually don\'t want to change this)',
    )
    token = fields.Text(
        readonly=True,
    )

    def call_api(self, action, uri_params, post_data=None, files={}):
        '''
        Call SFax api action (/api/:action e.g /api/sendfax)
        :param  action: str Action to perform (uri part)
        :param  uri_params: dict Params to pass as GET params
        :param  post_data: dict Data to pass as POST
        :param  files: dict of file tuples to upload. Keyed by name
        :return response: mixed
        '''
        uri = '%(uri)s/%(action)s' % {
            'uri': self.uri,
            'action': action,
        }
        if post_data is not None:
            resp = requests.post(
                uri,
                params=uri_params,
                data=post_data,
                files=files,
            )
        else:
            resp = requests.get(
                uri,
                params=uri_params
            )
        return resp.json()

    def __get_file_tuple(self, field_name, basename, fp, content_type):
        '''
        Prepare a file for upload through requests
        :param  field_name:  str
        :param  basename:    str
        :param  fp:  File like object (open, StringIO, etc)
        :param  content_type: str    main and subtype (application/pdf)
        :return tuple:
        '''
        return (field_name, (basename, fp, content_type, {'Expires': '0'}))
