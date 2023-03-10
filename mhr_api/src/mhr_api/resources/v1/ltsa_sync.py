# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""API endpoint to synchronize legacy database LTSA legal descriptions.

If a legacy registration location contains a pid and it does not exist in the modernized database,
make an ltsa api call to fetch the legal description and store it for search results as the
legacy database does not store it. This api limits the update to 500 pids at a time.
"""
from http import HTTPStatus

# import requests
from flask import Blueprint, current_app, request, jsonify
from flask_cors import cross_origin

from mhr_api.exceptions import DatabaseException
from mhr_api.models import utils as model_utils, LtsaDescription
from mhr_api.models.db2 import utils as db2_utils
from mhr_api.resources import utils as resource_utils
from mhr_api.services import ltsa


bp = Blueprint('LTSA_SYNC1', __name__,  # pylint: disable=invalid-name
               url_prefix='/api/v1/ltsa-sync')


@bp.route('', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*')
def post_ltsa_sync():
    """Resource to synchronize legacy ltsa legal descriptions with the modernized application."""
    try:
        current_app.logger.info('LTSA sync legacy legal description sync starting.')
        # Authenticate with request api key
        if not resource_utils.valid_api_key(request):
            return resource_utils.unauthorized_error_response('LTSA synchronization.')

        if not model_utils.is_legacy():
            return resource_utils.bad_request_response('Nothing to do: no longer in legacy transition.')

        pid_list = db2_utils.get_pid_list()
        if not pid_list:
            current_app.logger.info('LTSA sync no pids to update.')
            response_json = {
                'errorCount': 0,
                'successCount': 0,
                'errorPids': [],
                'successPids': []
            }
            return response_json, HTTPStatus.OK
        error_pids = []
        success_pids = []
        for pid in pid_list:
            try:
                ltsa_desc: LtsaDescription = ltsa.save_description(pid.get('pidNumber'))
                if ltsa_desc and ltsa_desc.ltsa_description:
                    success_pids.append(pid)
                else:
                    error_pids.append(pid)
            except Exception:   # noqa: B902; return nicer default error
                error_pids.append(pid)
        current_app.logger.debug(f'LTSA sync completed: success count {len(success_pids)}.')
        current_app.logger.debug(f'LTSA sync error count {len(error_pids)}.')

        # Now update the legacy record status to exclude in future calls.
        try:
            if success_pids:
                db2_utils.update_pid_list(success_pids, db2_utils.UPDATE_PID_STATUS_SUCCESS)
            if error_pids:
                db2_utils.update_pid_list(error_pids, db2_utils.UPDATE_PID_STATUS_ERROR)
        except Exception as update_exception:   # noqa: B902; return nicer default error
            current_app.logger.error('LTSA sync update status failed: ' + str(update_exception))
        response_json = {
            'errorCount': len(error_pids),
            'successCount': len(success_pids),
            'errorPids': error_pids,
            'successPids': success_pids
        }
        return jsonify(response_json), HTTPStatus.OK
    except DatabaseException as db_exception:
        return resource_utils.db_exception_response(db_exception, None, 'POST legacy ltsa sync')
    except Exception as default_exception:   # noqa: B902; return nicer default error
        return resource_utils.default_exception_response(default_exception)
