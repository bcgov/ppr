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

"""Tests to verify the financing-statement changes endpoint.

Test-Suite to ensure that the /financing-statement/registrationNum/changes endpoint is working as expected.
"""
import copy
from http import HTTPStatus

from registry_schemas.example_data.ppr import CHANGE_STATEMENT, FINANCING_STATEMENT

from ppr_api.services.authz import STAFF_ROLE, COLIN_ROLE, PPR_ROLE
from tests.unit.services.utils import create_header_account, create_header


# prep sample post change statement data
SAMPLE_JSON = copy.deepcopy(CHANGE_STATEMENT)


def test_change_create_invalid_type_400(session, client, jwt):
    """Assert that create statement with an invalid type returns a 400 error."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseRegistrationNumber'] = 'TEST0001'
    json_data['baseDebtor']['businessName'] = 'TEST BUS 2 DEBTOR'
    json_data['changeType'] = 'XX'
    del json_data['documentId']
    del json_data['createDateTime']
    del json_data['changeRegistrationNumber']
    del json_data['payment']
    del json_data['addSecuredParties']
    del json_data['deleteSecuredParties']
    del json_data['deleteDebtors']
    del json_data['addDebtors']
    del json_data['deleteVehicleCollateral']
    del json_data['deleteGeneralCollateral']
    del json_data['addGeneralCollateral']

    # test
    rv = client.post('/api/v1/financing-statements/TEST0001/changes',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_change_create_valid_su_201(session, client, jwt):
    """Assert that a valid SU type change statement returns a 200 status."""
    # setup
    statement = copy.deepcopy(FINANCING_STATEMENT)
    statement['debtors'][0]['businessName'] = 'TEST BUS 2 DEBTOR'
    statement['type'] = 'SA'
    del statement['createDateTime']
    del statement['baseRegistrationNumber']
    del statement['payment']
    del statement['documentId']
    del statement['lifeInfinite']
    del statement['lienAmount']
    del statement['surrenderDate']

    rv1 = client.post('/api/v1/financing-statements',
                      json=statement,
                      headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                      content_type='application/json')
    assert rv1.status_code == HTTPStatus.CREATED
    assert rv1.json['baseRegistrationNumber']
    base_reg_num = rv1.json['baseRegistrationNumber']

    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseRegistrationNumber'] = base_reg_num
    json_data['baseDebtor']['businessName'] = 'TEST BUS 2 DEBTOR'
    json_data['changeType'] = 'SU'
    del json_data['createDateTime']
    del json_data['changeRegistrationNumber']
    del json_data['payment']
    del json_data['documentId']
    del json_data['addSecuredParties']
    del json_data['deleteSecuredParties']
    del json_data['deleteDebtors']
    del json_data['addDebtors']
    del json_data['deleteGeneralCollateral']
    json_data['deleteGeneralCollateral'] = rv1.json['generalCollateral']
    del json_data['deleteVehicleCollateral']
    json_data['deleteVehicleCollateral'] = rv1.json['vehicleCollateral']

    # test
    rv = client.post('/api/v1/financing-statements/' + base_reg_num + '/changes',
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.CREATED


def test_change_create_valid_dt_201(session, client, jwt):
    """Assert that a valid DT type change statement returns a 200 status."""
    # setup
    statement = copy.deepcopy(FINANCING_STATEMENT)
    statement['debtors'][0]['businessName'] = 'TEST BUS 2 DEBTOR'
    statement['type'] = 'SA'
    del statement['createDateTime']
    del statement['baseRegistrationNumber']
    del statement['payment']
    del statement['documentId']
    del statement['lifeInfinite']
    del statement['lienAmount']
    del statement['surrenderDate']

    rv1 = client.post('/api/v1/financing-statements',
                      json=statement,
                      headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                      content_type='application/json')
    assert rv1.status_code == HTTPStatus.CREATED
    assert rv1.json['baseRegistrationNumber']
    base_reg_num = rv1.json['baseRegistrationNumber']

    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseRegistrationNumber'] = base_reg_num
    json_data['baseDebtor']['businessName'] = 'TEST BUS 2 DEBTOR'
    json_data['changeType'] = 'DT'
    del json_data['createDateTime']
    del json_data['changeRegistrationNumber']
    del json_data['payment']
    del json_data['documentId']
    del json_data['addSecuredParties']
    del json_data['deleteSecuredParties']
    del json_data['addVehicleCollateral']
    del json_data['deleteVehicleCollateral']
    del json_data['deleteGeneralCollateral']
    del json_data['addGeneralCollateral']
    del json_data['deleteDebtors']
    json_data['deleteDebtors'] = rv1.json['debtors']

    # test
    rv = client.post('/api/v1/financing-statements/' + base_reg_num + '/changes',
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.CREATED


def test_change_create_invalid_regnum_404(session, client, jwt):
    """Assert that an change statement on an invalid registration number returns a 404 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseRegistrationNumber'] = 'X12345X'
    json_data['baseDebtor']['businessName'] = 'TEST BUS 2 DEBTOR'
    json_data['changeType'] = 'AC'
    del json_data['createDateTime']
    del json_data['changeRegistrationNumber']
    del json_data['payment']
    del json_data['documentId']
    del json_data['addSecuredParties']
    del json_data['deleteSecuredParties']
    del json_data['deleteDebtors']
    del json_data['addDebtors']
    del json_data['deleteVehicleCollateral']
    del json_data['deleteGeneralCollateral']
    del json_data['addGeneralCollateral']

    # test
    rv = client.post('/api/v1/financing-statements/X12345X/changes',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_change_nonstaff_missing_account_400(session, client, jwt):
    """Assert that a change statement request with a non-staff jwt and no account ID returns a 400 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseRegistrationNumber'] = 'TEST0001'
    json_data['baseDebtor']['businessName'] = 'TEST BUS 2 DEBTOR'
    json_data['changeType'] = 'AC'
    del json_data['createDateTime']
    del json_data['changeRegistrationNumber']
    del json_data['payment']
    del json_data['documentId']
    del json_data['addSecuredParties']
    del json_data['deleteSecuredParties']
    del json_data['deleteDebtors']
    del json_data['addDebtors']
    del json_data['deleteVehicleCollateral']
    del json_data['deleteGeneralCollateral']
    del json_data['addGeneralCollateral']

    # test
    rv = client.post('/api/v1/financing-statements/TEST0001/changes',
                     json=json_data,
                     headers=create_header(jwt, [COLIN_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_change_staff_missing_account_201(session, client, jwt):
    """Assert that a change statement request with a staff jwt and no account ID returns a 200 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['changeType'] = 'AC'
    json_data['baseRegistrationNumber'] = 'TEST0001'
    json_data['baseDebtor']['businessName'] = 'TEST BUS 2 DEBTOR'
    del json_data['createDateTime']
    del json_data['changeRegistrationNumber']
    del json_data['payment']
    del json_data['documentId']
    del json_data['addSecuredParties']
    del json_data['deleteSecuredParties']
    del json_data['deleteDebtors']
    del json_data['addDebtors']
    del json_data['deleteVehicleCollateral']
    del json_data['deleteGeneralCollateral']
    del json_data['addGeneralCollateral']

    # test
    rv = client.post('/api/v1/financing-statements/TEST0001/changes',
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.CREATED


def test_change_nonstaff_unauthorized_401(session, client, jwt):
    """Assert that a change statement request with a non-ppr role and account ID returns a 404 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseRegistrationNumber'] = 'TEST0001'
    json_data['baseDebtor']['businessName'] = 'TEST BUS 2 DEBTOR'
    json_data['changeType'] = 'AC'
    del json_data['createDateTime']
    del json_data['changeRegistrationNumber']
    del json_data['payment']
    del json_data['documentId']
    del json_data['addSecuredParties']
    del json_data['deleteSecuredParties']
    del json_data['deleteDebtors']
    del json_data['addDebtors']
    del json_data['deleteVehicleCollateral']
    del json_data['deleteGeneralCollateral']
    del json_data['addGeneralCollateral']

    # test
    rv = client.post('/api/v1/financing-statements/TEST0001/changes',
                     json=json_data,
                     headers=create_header_account(jwt, [COLIN_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_change_invalid_missing_basedebtor_400(session, client, jwt):
    """Assert that create statement with a missing base debtor returns a 400 error."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseRegistrationNumber'] = 'TEST0001'
    del json_data['createDateTime']
    del json_data['changeRegistrationNumber']
    del json_data['payment']
    del json_data['documentId']
    del json_data['baseDebtor']

    # test
    rv = client.post('/api/v1/financing-statements/TEST0001/changes',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_change_invalid_historical_400(session, client, jwt):
    """Assert that a change statement on an already discharged registration returns a 400 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseRegistrationNumber'] = 'TEST0003'
    json_data['baseDebtor']['businessName'] = 'TEST BUS 2 DEBTOR'
    del json_data['createDateTime']
    del json_data['changeRegistrationNumber']
    del json_data['payment']
    del json_data['documentId']

    # test
    rv = client.post('/api/v1/financing-statements/TEST0003/changes',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_change_invalid_debtor_400(session, client, jwt):
    """Assert that a change statement with an invalid base debtor name returns a 400 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseRegistrationNumber'] = 'TEST0001'
    json_data['baseDebtor']['businessName'] = 'TEST BUS 3 DEBTOR'
    del json_data['createDateTime']
    del json_data['changeRegistrationNumber']
    del json_data['payment']
    del json_data['documentId']

    # test
    rv = client.post('/api/v1/financing-statements/TEST0001/changes',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST
