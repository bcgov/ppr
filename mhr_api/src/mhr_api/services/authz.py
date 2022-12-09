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
STAFF_ROLE = 'ppr_staff'  # Share single role/account id with ppr for search, registration history.
COLIN_ROLE = 'colin'
MHR_ROLE = 'mhr'
BASIC_USER = 'basic'
PRO_DATA_USER = 'pro_data'
PUBLIC_USER = 'public_user'
USER_ORGS_PATH = 'users/orgs'
GOV_ACCOUNT_ROLE = 'gov_account_user'
BCOL_HELP = 'mhr_helpdesk'
ASSETS_HELP = 'helpdesk'  # Share single account id for search, registration history.
# MH keycloak roles for registrations/filings
REGISTER_MH = 'mhr_register'
REQUEST_TRANSPORT_PERMIT = 'mhr_transport'
REQUEST_EXEMPTION_RES = 'mhr_exemption_res'
REQUEST_EXEMPTION_NON_RES = 'mhr_exemption_non_res'
TRANSFER_SALE_BENEFICIARY = 'mhr_transfer_sale'
TRANSFER_DEATH_JT = 'mhr_transfer_death'
# MH groups from role combinations
QUALIFIED_USER_GROUP = 'mhr_qualified_user'
MANUFACTURER_GROUP = 'mhr_manufacturer'
GENERAL_USER_GROUP = 'mhr_general_user'
SEARCH_USER_GROUP = 'mhr_search_user'


def authorized(identifier: str, jwt: JwtManager) -> bool:
    """Verify the user is authorized to submit the request by inspecting the web token.

    The gateway has already verified the JWT with the OIDC service.
    """
    if not jwt:
        return False

    # Could call the auth api here to check the token roles (/api/v1/orgs/{account_id}/authorizations),
    # but JWTManager.validate_roles does the same thing.

    # All users including staff must have the PPR role.
    if not jwt.validate_roles([MHR_ROLE]):
        return False

    # Account ID (idenfifier) is required if not staff.
    if identifier and identifier.strip() != '':
        return True

    # Remove when all staff changes made.
    if jwt.validate_roles([STAFF_ROLE]):
        return True


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


def authorized_role(jwt: JwtManager, user_role: str) -> bool:
    """Verify the user is authorized to submit a request by inspecting the web token."""
    if jwt.validate_roles([STAFF_ROLE]) or jwt.validate_roles([user_role]):
        return True
    return False


def authorized_token(  # pylint: disable=too-many-return-statements
        identifier: str, jwt: JwtManager, action: List[str]) -> bool:
    """Assert that the user is authorized to submit API requests for a particular action."""
    if not action or not identifier or not jwt:
        return False

    # All users including staff must have the PPR role.
    if not jwt.validate_roles([MHR_ROLE]):
        return False

    if jwt.has_one_of_roles([BASIC_USER, PRO_DATA_USER]):

        template_url = current_app.config.get('AUTH_SVC_URL')
        auth_url = template_url.format(**vars())

        token = jwt.get_token_auth_header()
        headers = {'Authorization': 'Bearer ' + token}
        try:
            with Session() as http:
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


def user_orgs(token: str) -> dict:
    """Auth API call to get user organizations for the user identified by the token."""
    response = None
    if not token:
        return response

    service_url = current_app.config.get('AUTH_SVC_URL')
    api_url = service_url + '/' if service_url[-1] != '/' else service_url
    api_url += USER_ORGS_PATH

    try:
        headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        }
        # current_app.logger.debug('Auth get user orgs url=' + url)
        with Session() as http:
            retries = Retry(total=3,
                            backoff_factor=0.1,
                            status_forcelist=[500, 502, 503, 504])
            http.mount('http://', HTTPAdapter(max_retries=retries))
            ret_val = http.get(url=api_url, headers=headers)
            current_app.logger.debug('Auth get user orgs response status: ' + str(ret_val.status_code))
            # current_app.logger.debug('Auth get user orgs response data:')
            response = ret_val.json()
            # current_app.logger.debug(response)
    except (exceptions.ConnectionError,  # pylint: disable=broad-except
            exceptions.Timeout,
            ValueError,
            Exception) as err:
        current_app.logger.error(f'Authorization connection failure using svc:{api_url}', err)

    return response


def account_org(token: str, account_id: str) -> dict:
    """Auth API call to get the account organization info identified by the account id."""
    response = None
    if not token or not account_id:
        return response

    service_url = current_app.config.get('AUTH_SVC_URL')
    api_url = service_url + '/' if service_url[-1] != '/' else service_url
    api_url += f'orgs/{account_id}'

    try:
        headers = {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        }
        # current_app.logger.debug('Auth get user orgs url=' + url)
        with Session() as http:
            retries = Retry(total=3,
                            backoff_factor=0.1,
                            status_forcelist=[500, 502, 503, 504])
            http.mount('http://', HTTPAdapter(max_retries=retries))
            ret_val = http.get(url=api_url, headers=headers)
            current_app.logger.debug('Auth get user orgs response status: ' + str(ret_val.status_code))
            # current_app.logger.debug('Auth get account org response data:')
            response = ret_val.json()
            # current_app.logger.debug(response)
    except (exceptions.ConnectionError,  # pylint: disable=broad-except
            exceptions.Timeout,
            ValueError,
            Exception) as err:
        current_app.logger.error(f'Authorization connection failure using svc:{api_url}', err)

    return response


def is_staff(jwt: JwtManager) -> bool:  # pylint: disable=too-many-return-statements
    """Return True if the user has the BC Registries staff role."""
    if not jwt:
        return False
    if jwt.validate_roles([STAFF_ROLE]):
        return True

    return False


def is_bcol_help(account_id: str, jwt: JwtManager = None) -> bool:
    """Return True if the account id is a bcol help account id."""
    if jwt is not None and jwt.validate_roles([BCOL_HELP]):
        return True
    return account_id is not None and account_id == BCOL_HELP


def is_staff_account(account_id: str, jwt: JwtManager = None) -> bool:
    """Return True if the account id is a registries staff or has a staff role."""
    if jwt is not None and jwt.validate_roles([STAFF_ROLE]):
        return True
    return account_id is not None and account_id == STAFF_ROLE


def is_reg_staff_account(account_id: str, jwt: JwtManager = None) -> bool:
    """Return True if the account id is a staff registries account id."""
    return is_staff_account(account_id, jwt)


def is_sbc_office_account(token: str, account_id: str) -> bool:
    """Return True if the account id is an sbc office account id."""
    try:
        org_info = account_org(token, account_id)
        if org_info and 'branchName' in org_info:
            return 'Service BC' in org_info['branchName']
        return None
    except Exception as err:  # pylint: disable=broad-except # noqa F841;
        current_app.logger.error('is_sbc_office_account failed: ' + repr(err))
        return None


def is_gov_account(jwt: JwtManager) -> bool:
    """Return True if the user has the gov account user role."""
    if not jwt:
        return False
    if jwt.validate_roles([GOV_ACCOUNT_ROLE]):
        return True

    return False


def is_all_staff_account(account_id: str) -> bool:
    """Return True if the account id is any staff role."""
    return account_id is not None and account_id in (STAFF_ROLE, ASSETS_HELP)


def get_group(jwt: JwtManager) -> str:  # pylint: disable=too-many-return-statements
    """Obtain the user group/role by inspecting the web token."""
    if jwt.validate_roles([STAFF_ROLE]):
        return STAFF_ROLE
    if jwt.validate_roles([BCOL_HELP]):
        return BCOL_HELP
    if jwt.validate_roles([GOV_ACCOUNT_ROLE]):
        return GOV_ACCOUNT_ROLE
    if jwt.validate_roles([REGISTER_MH]) and jwt.validate_roles([TRANSFER_SALE_BENEFICIARY]) and \
            not jwt.validate_roles([REQUEST_EXEMPTION_RES]):
        return MANUFACTURER_GROUP
    if jwt.validate_roles([TRANSFER_DEATH_JT]) and jwt.validate_roles([TRANSFER_SALE_BENEFICIARY]) and \
            not jwt.validate_roles([REGISTER_MH]):
        return QUALIFIED_USER_GROUP
    if jwt.validate_roles([REQUEST_TRANSPORT_PERMIT]):
        return GENERAL_USER_GROUP
    return SEARCH_USER_GROUP
