# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""This manages all of the ltsa service integration for the application: PID lookup."""
import copy
import json

import requests
from flask import current_app


ORDER_URI = 'titledirect/search/api/orders'
ORDER_TEMPLATE = {
    'order': {
        'productType': 'parcelInfo',
        'fileReference': 'folio',
        'productOrderParameters': {
            'parcelIdentifier': ''
        }
    }
}


def pid_lookup(pid: str) -> dict:
    """LTSA parcel order lookup by PID."""
    response = None
    if not pid:
        return response
    service_url: str = current_app.config.get('GATEWAY_LTSA_URL')
    api_url: str = service_url + '/' if service_url[-1] != '/' else service_url
    api_url += ORDER_URI
    api_key: str = current_app.config.get('GATEWAY_API_KEY')
    try:
        formatted_pid = pid
        if len(formatted_pid) == 9:
            formatted_pid = pid[0:3] + '-' + pid[3:6] + '-' + pid[6:]
        data = copy.deepcopy(ORDER_TEMPLATE)
        data['order']['productOrderParameters']['parcelIdentifier'] = formatted_pid
        headers = {
            'x-apikey': api_key
        }
        # current_app.logger.debug('LTSA PID lookup url=' + api_url)
        response = requests.request(
            'post',
            api_url,
            params=None,
            json=data,
            headers=headers
        )
        if response:
            current_app.logger.info('LTSA api response=' + response.text)
        if not response.ok:
            return None
        return json.loads(response.text)
    except (requests.exceptions.ConnectionError,  # pylint: disable=broad-except
            requests.exceptions.Timeout,
            ValueError,
            Exception) as err:
        current_app.logger.error(f'LTSA PID lookup connection failure using svc:{api_url}', err)
