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
"""This manages all of the authentication and authorization service."""
from http import HTTPStatus
from typing import List

from flask import current_app
from flask_jwt_oidc import JwtManager
from requests import Session, exceptions
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


SYSTEM_ROLE = 'system'
STAFF_ROLE = 'staff'
COLIN_ROLE = 'colin'
PPR_ROLE = 'ppr'
STAFF_ROLE = 'staff'
BASIC_USER = 'basic'
PRO_DATA_USER = 'pro_data'
PUBLIC_USER = 'public_user'


#def authorized(identifier: str, jwt: JwtManager, action: List[str]) -> bool: # pylint: disable=too-many-return-statements
def authorized(identifier: str, jwt: JwtManager) -> bool: # pylint: disable=too-many-return-statements
    """Verify the user is authorized to submit the request by inspecting the web token."""

    if not jwt:
        return False

    if jwt.validate_roles([STAFF_ROLE]) \
            or jwt.validate_roles([SYSTEM_ROLE]):
        return True

    if jwt.validate_roles([PPR_ROLE]):

        # account id (identifier) is required if not staff.
        if identifier and identifier.strip() != '':
            return True

        # TODO: verify account ID here against JWT. Possibly verify action as well?

#        template_url = current_app.config.get('AUTH_SVC_URL')
#        auth_url = template_url.format(**vars())

#        token = jwt.get_token_auth_header()
#        headers = {'Authorization': 'Bearer ' + token}
#        try:
#            http = Session()
#            retries = Retry(total=5,
#                            backoff_factor=0.1,
#                            status_forcelist=[500, 502, 503, 504])
#            http.mount('http://', HTTPAdapter(max_retries=retries))
#            rv = http.get(url=auth_url, headers=headers)

#           if rv.status_code != HTTPStatus.OK \
#                    or not rv.json().get('roles'):
#                return False

#            if all(elem.lower() in rv.json().get('roles') for elem in action):
#                return True

#        except (exceptions.ConnectionError,  # pylint: disable=broad-except
#                exceptions.Timeout,
#                ValueError,
#                Exception) as err:
#            current_app.logger.error(f'template_url {template_url}, svc:{auth_url}')
#            current_app.logger.error(f'Authorization connection failure for {identifier}, using svc:{auth_url}', err)
#            return False

    return False


def authorized_token(  # pylint: disable=too-many-return-statements
        identifier: str, jwt: JwtManager, action: List[str]) -> bool:
    """Assert that the user is authorized to create transactions against the business identifier."""
    # if they are registry staff, they are always authorized
    if not action or not identifier or not jwt:
        return False

    if jwt.validate_roles([STAFF_ROLE]) \
            or jwt.validate_roles([SYSTEM_ROLE]) \
            or jwt.validate_roles([PPR_ROLE]):
        return True

    if jwt.has_one_of_roles([BASIC_USER, PRO_DATA_USER]):

        # if the action is create_comment, disallow - only staff are allowed
        if action == 'add_comment':
            return False

        template_url = current_app.config.get('AUTH_SVC_URL')
        auth_url = template_url.format(**vars())

        token = jwt.get_token_auth_header()
        headers = {'Authorization': 'Bearer ' + token}
        try:
            http = Session()
            retries = Retry(total=5,
                            backoff_factor=0.1,
                            status_forcelist=[500, 502, 503, 504])
            http.mount('http://', HTTPAdapter(max_retries=retries))
            rv = http.get(url=auth_url, headers=headers)

            if rv.status_code != HTTPStatus.OK \
                    or not rv.json().get('roles'):
                return False

            if all(elem.lower() in rv.json().get('roles') for elem in action):
                return True

        except (exceptions.ConnectionError,  # pylint: disable=broad-except
                exceptions.Timeout,
                ValueError,
                Exception) as err:
            current_app.logger.error(f'template_url {template_url}, svc:{auth_url}')
            current_app.logger.error(f'Authorization connection failure for {identifier}, using svc:{auth_url}', err)
            return False

    return False


def is_staff(jwt: JwtManager) -> bool:  # pylint: disable=too-many-return-statements
    """True if user has the BC Registries staff role."""

    if not jwt:
        return False

    if jwt.validate_roles([STAFF_ROLE]):
        return True

    return False
