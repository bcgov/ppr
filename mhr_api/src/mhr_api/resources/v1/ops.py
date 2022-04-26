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
"""Endpoints to check and manage the health of the service."""
from flask import Blueprint
from flask import current_app
from flask import jsonify
from sqlalchemy import text, exc

from mhr_api.models import db


bp = Blueprint('OPS1', __name__, url_prefix='/api/v1/ops')  # pylint: disable=invalid-name

SQL = text('select 1')


@bp.route('/healthz')
def healthz():
    """Status check to verify the service and required dependencies are still working.

    This could be thought of as a heartbeat for the service
    """
    try:
        db.session.execute(SQL)
    except exc.SQLAlchemyError as db_exception:
        current_app.logger.error('DB connection pool unhealthy:' + str(db_exception))
        return {'message': 'api is down'}, 500
    except Exception as default_exception:   # noqa: B902; log error
        current_app.logger.error('DB connection pool query failed:' + str(default_exception))
        return {'message': 'api is down'}, 500

    # made it here, so all checks passed
    return jsonify({'message': 'api is healthy'}), 200


@bp.route('/readyz')
def readyz():
    """Status check to verify the service is ready to respond."""
    return jsonify({'message': 'api is ready'}), 200
