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

"""Tests to verify the financing-statement amendments endpoint.

Test-Suite to ensure that the /financing-statement/registrationNum/amendments endpoint is working as expected.
"""
import copy
from http import HTTPStatus

from registry_schemas.example_data.ppr import AMENDMENT_STATEMENT, FINANCING_STATEMENT

from ppr_api.services.authz import STAFF_ROLE, COLIN_ROLE, PPR_ROLE
from tests.unit.services.utils import create_header_account, create_header


# prep sample post amendment statement data
SAMPLE_JSON = copy.deepcopy(AMENDMENT_STATEMENT)


def test_amendment_invalid_type_400(session, client, jwt):
    """Assert that create statement with an invalid type returns a 400 error."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseDebtor']['businessName'] = 'TEST BUS 2 DEBTOR'
    json_data['baseRegistrationNumber'] = 'TEST0001'
    json_data['changeType'] = 'XX'
    del json_data['courtOrderInformation']
    del json_data['createDateTime']
    del json_data['amendmentRegistrationNumber']
    del json_data['payment']
    del json_data['documentId']

    # test
    rv = client.post('/api/v1/financing-statements/TEST0001/amendments',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')
    # check
    print(rv.json)
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_amendment_valid_co_201(session, client, jwt):
    """Assert that a valid CO type amendment statement returns a 200 status."""
    # setup
    statement = copy.deepcopy(FINANCING_STATEMENT)
    statement['debtors'][0]['businessName'] = 'TEST BUS 2 DEBTOR'
    statement['type'] = 'SA'
    del statement['createDateTime']
    del statement['baseRegistrationNumber']
    del statement['payment']
    del statement['lifeInfinite']
    del statement['lienAmount']
    del statement['surrenderDate']
    del statement['documentId']

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
    json_data['changeType'] = 'CO'
    del json_data['createDateTime']
    del json_data['amendmentRegistrationNumber']
    del json_data['payment']
    del json_data['removeTrustIndenture']
    del json_data['addTrustIndenture']
    del json_data['deleteDebtors']
    del json_data['documentId']
    json_data['deleteDebtors'] = rv1.json['debtors']
    del json_data['deleteSecuredParties']
    json_data['deleteSecuredParties'] = rv1.json['securedParties']
    del json_data['deleteGeneralCollateral']
    json_data['deleteGeneralCollateral'] = rv1.json['generalCollateral']
    del json_data['deleteVehicleCollateral']
    json_data['deleteVehicleCollateral'] = rv1.json['vehicleCollateral']
#    print(json_data)

    # test
    rv = client.post('/api/v1/financing-statements/' + base_reg_num + '/amendments',
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                     content_type='application/json')

    # check
#    print(rv.json)
    assert rv.status_code == HTTPStatus.CREATED


def test_amendment_valid_am_201(session, client, jwt):
    """Assert that a valid AM type amendment statement returns a 200 status."""
    # setup
    statement = copy.deepcopy(FINANCING_STATEMENT)
    statement['debtors'][0]['businessName'] = 'TEST BUS 2 DEBTOR'
    statement['type'] = 'SA'
    del statement['createDateTime']
    del statement['baseRegistrationNumber']
    del statement['payment']
    del statement['lifeInfinite']
    del statement['lienAmount']
    del statement['surrenderDate']
    del statement['documentId']

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
    json_data['changeType'] = 'AM'
    del json_data['courtOrderInformation']
    del json_data['createDateTime']
    del json_data['amendmentRegistrationNumber']
    del json_data['payment']
    del json_data['removeTrustIndenture']
    del json_data['addTrustIndenture']
    del json_data['addSecuredParties']
    del json_data['deleteSecuredParties']
    del json_data['addDebtors']
    del json_data['deleteDebtors']
    del json_data['deleteGeneralCollateral']
    del json_data['addGeneralCollateral']
    del json_data['deleteVehicleCollateral']
    del json_data['documentId']
    json_data['deleteVehicleCollateral'] = rv1.json['vehicleCollateral']

    # test
    rv = client.post('/api/v1/financing-statements/' + base_reg_num + '/amendments',
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.CREATED


def test_amendment_create_invalid_regnum_404(session, client, jwt):
    """Assert that an amendment statement on an invalid registration number returns a 404 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['changeType'] = 'CO'
    json_data['baseRegistrationNumber'] = 'X12345X'
    del json_data['createDateTime']
    del json_data['amendmentRegistrationNumber']
    del json_data['payment']
    del json_data['documentId']

    # test
    rv = client.post('/api/v1/financing-statements/X12345X/amendments',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_amendment_nonstaff_missing_account_400(session, client, jwt):
    """Assert that an amendment statement request with a non-staff jwt and no account ID returns a 400 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseDebtor']['businessName'] = 'TEST BUS 2 DEBTOR'
    json_data['baseRegistrationNumber'] = 'TEST0001'
    json_data['changeType'] = 'CO'
    del json_data['createDateTime']
    del json_data['amendmentRegistrationNumber']
    del json_data['payment']
    del json_data['documentId']

    # test
    rv = client.post('/api/v1/financing-statements/TEST0001/amendments',
                     json=json_data,
                     headers=create_header(jwt, [COLIN_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_amendment_staff_missing_account_201(session, client, jwt):
    """Assert that an amendment statement request with a staff jwt and no account ID returns a 200 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseDebtor']['businessName'] = 'TEST BUS 2 DEBTOR'
    json_data['baseRegistrationNumber'] = 'TEST0001'
    json_data['changeType'] = 'CO'
    del json_data['createDateTime']
    del json_data['amendmentRegistrationNumber']
    del json_data['payment']
    del json_data['documentId']
    del json_data['courtOrderInformation']
    del json_data['removeTrustIndenture']
    del json_data['addTrustIndenture']
    del json_data['addSecuredParties']
    del json_data['deleteSecuredParties']
    del json_data['addDebtors']
    del json_data['deleteDebtors']
    del json_data['deleteGeneralCollateral']
    del json_data['addGeneralCollateral']
    del json_data['deleteVehicleCollateral']

    # test
    rv = client.post('/api/v1/financing-statements/TEST0001/amendments',
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.CREATED


def test_amendment_nonstaff_unauthorized_404(session, client, jwt):
    """Assert that an amendment statement request with a non-ppr role and account ID returns a 404 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseDebtor']['businessName'] = 'TEST BUS 2 DEBTOR'
    json_data['baseRegistrationNumber'] = 'TEST0001'
    json_data['changeType'] = 'CO'
    del json_data['createDateTime']
    del json_data['amendmentRegistrationNumber']
    del json_data['payment']
    del json_data['documentId']

    # test
    rv = client.post('/api/v1/financing-statements/TEST0001/amendments',
                     json=json_data,
                     headers=create_header_account(jwt, [COLIN_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_amendment_invalid_missing_basedebtor_400(session, client, jwt):
    """Assert that create statement with a missing base debtor returns a 400 error."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseRegistrationNumber'] = 'TEST0001'
    del json_data['createDateTime']
    del json_data['amendmentRegistrationNumber']
    del json_data['payment']
    del json_data['documentId']
    del json_data['baseDebtor']

    # test
    rv = client.post('/api/v1/financing-statements/TEST0001/amendments',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_amendment_invalid_historical_400(session, client, jwt):
    """Assert that an amendments statement on an already discharged registration returns a 400 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseRegistrationNumber'] = 'TEST0003'
    json_data['baseDebtor']['businessName'] = 'TEST BUS 2 DEBTOR'
    del json_data['createDateTime']
    del json_data['amendmentRegistrationNumber']
    del json_data['payment']
    del json_data['documentId']

    # test
    rv = client.post('/api/v1/financing-statements/TEST0003/amendments',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_amendment_invalid_debtor_400(session, client, jwt):
    """Assert that a amendment statement with an invalid base debtor name returns a 400 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON)
    json_data['baseRegistrationNumber'] = 'TEST0001'
    json_data['baseDebtor']['businessName'] = 'TEST BUS 3 DEBTOR'
    del json_data['createDateTime']
    del json_data['amendmentRegistrationNumber']
    del json_data['payment']
    del json_data['documentId']

    # test
    rv = client.post('/api/v1/financing-statements/TEST0001/amendments',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')

    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST
