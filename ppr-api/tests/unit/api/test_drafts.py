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

"""Tests to verify the drafts endpoint.

Test-Suite to ensure that the /drafts endpoint is working as expected.
"""
import copy
from http import HTTPStatus

from registry_schemas.example_data.ppr import DRAFT_FINANCING_STATEMENT, DRAFT_CHANGE_STATEMENT, \
     DRAFT_AMENDMENT_STATEMENT

from ppr_api.services.authz import STAFF_ROLE, COLIN_ROLE, PPR_ROLE
from tests.unit.services.utils import create_header_account, create_header


# prep sample post, put draft statement data
SAMPLE_JSON_FINANCING = copy.deepcopy(DRAFT_FINANCING_STATEMENT)
SAMPLE_JSON_CHANGE = copy.deepcopy(DRAFT_CHANGE_STATEMENT)
SAMPLE_JSON_AMENDMENT = copy.deepcopy(DRAFT_AMENDMENT_STATEMENT)


def test_draft_create_invalid_type(session, client, jwt):
    """Assert that create draft  with an invalid type returns a 404 error."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_FINANCING)
    json_data['type'] = 'INVALID_TYPE'

    # test
    rv = client.post('/api/v1/drafts',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.INTERNAL_SERVER_ERROR


def test_draft_create_valid_financing_201(session, client, jwt):
    """Assert that a valid draft financing statement returns a 201 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_FINANCING)

    # test
    rv = client.post('/api/v1/drafts',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.CREATED
    assert rv.json['financingStatement']['documentId']

    # now delete draft
    document_id = rv.json['financingStatement']['documentId']
    rv2 = client.delete('/api/v1/drafts/' + document_id,
                        headers=create_header_account(jwt, [PPR_ROLE]))
    # check delete
    assert rv2.status_code == HTTPStatus.NO_CONTENT


def test_draft_create_valid_amendment_201(session, client, jwt):
    """Assert that a valid draft amendment statement returns a 201 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_AMENDMENT)

    # test
    rv = client.post('/api/v1/drafts',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.CREATED
    assert rv.json['amendmentStatement']['documentId']

    # now delete draft
    document_id = rv.json['amendmentStatement']['documentId']
    rv2 = client.delete('/api/v1/drafts/' + document_id,
                        headers=create_header_account(jwt, [PPR_ROLE]))
    # check delete
    assert rv2.status_code == HTTPStatus.NO_CONTENT


def test_draft_valid_change_201(session, client, jwt):
    """Assert that a valid draft change statement returns a 201 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_CHANGE)

    # test
    rv = client.post('/api/v1/drafts',
                     json=json_data,
                     headers=create_header_account(jwt, [PPR_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.CREATED
    assert rv.json['changeStatement']['documentId']

    # now delete draft
    document_id = rv.json['changeStatement']['documentId']
    rv2 = client.delete('/api/v1/drafts/' + document_id,
                        headers=create_header_account(jwt, [PPR_ROLE]))
    # check delete
    assert rv2.status_code == HTTPStatus.NO_CONTENT


def test_draft_get_list_200(session, client, jwt):
    """Assert that a get draft list for an account returns a 200 status."""
    # setup

    # test
    rv = client.get('/api/v1/drafts',
                    headers=create_header_account(jwt, [PPR_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.OK


def test_draft_valid_get_statement_200(session, client, jwt):
    """Assert that a valid get draft by document ID returns a 200 status."""
    # setup

    # test
    rv = client.get('/api/v1/drafts/D-T-FS01',
                    headers=create_header_account(jwt, [PPR_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.OK


def test_draft_invalid_get_statement_404(session, client, jwt):
    """Assert that a get draft by invalid document ID returns a 404 status."""
    # setup

    # test
    rv = client.get('/api/v1/drafts/D0012345',
                    headers=create_header_account(jwt, [PPR_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_draft_update_invalid_type_404(session, client, jwt):
    """Assert that an update draft financing statement request with an invalid type returns a 404."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_FINANCING)
    json_data['financingStatement']['type'] = 'XA'

    # test
    rv = client.put('/api/v1/drafts/D0034001',
                    json=json_data,
                    headers=create_header_account(jwt, [PPR_ROLE]),
                    content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_draft_update_valid_financing_200(session, client, jwt):
    """Assert that a valid draft financing statement update request returns a 200 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_FINANCING)

    # test
    rv = client.put('/api/v1/drafts/D-T-FS01',
                    json=json_data,
                    headers=create_header_account(jwt, [PPR_ROLE]),
                    content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.OK


def test_draft_update_valid_amendment_200(session, client, jwt):
    """Assert that a valid draft amendment statement update request returns a 200 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_AMENDMENT)

    # test
    rv = client.put('/api/v1/drafts/D-T-AM01',
                    json=json_data,
                    headers=create_header_account(jwt, [PPR_ROLE]),
                    content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.OK


def test_draft_update_valid_change_200(session, client, jwt):
    """Assert that a valid draft change statement update request returns a 200 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_CHANGE)

    # test
    rv = client.put('/api/v1/drafts/D-T-CH01',
                    json=json_data,
                    headers=create_header_account(jwt, [PPR_ROLE]),
                    content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.OK

# def test_draft_delete_204(session, client, jwt):
#    """Assert that a valid delete draft request returns a 204 status."""
    # setup

    # test
#    rv = client.delete(f'/api/v1/drafts/TEST-FSD1',
#                       headers=create_header_account(jwt, [PPR_ROLE]))
    # check
#    assert rv.status_code == HTTPStatus.NO_CONTENT


def test_draft_delete_404(session, client, jwt):
    """Assert that an invalid delete draft document ID returns a 404 status."""
    # setup

    # test
    rv = client.delete('/api/v1/drafts/X12345X',
                       headers=create_header_account(jwt, [PPR_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.NOT_FOUND


def test_draft_create_nonstaff_missing_account_400(session, client, jwt):
    """Assert that a non-staff draft request with no account ID returns a 400 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_FINANCING)

    # test
    rv = client.post('/api/v1/drafts',
                     json=json_data,
                     headers=create_header(jwt, [COLIN_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_draft_create_staff_missing_account_400(session, client, jwt):
    """Assert that a staff draft request with no account ID returns a 400 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_FINANCING)

    # test
    rv = client.post('/api/v1/drafts',
                     json=json_data,
                     headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_draft_create_nonstaff_unauthorized_401(session, client, jwt):
    """Assert that a non-ppr role draft request with an account ID returns a 404 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_FINANCING)

    # test
    rv = client.post('/api/v1/drafts',
                     json=json_data,
                     headers=create_header_account(jwt, [COLIN_ROLE]),
                     content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_draft_list_nonstaff_missing_account_400(session, client, jwt):
    """Assert that a non-staff draft list request with no account ID returns a 400 status."""
    # setup

    # test
    rv = client.get('/api/v1/drafts',
                    headers=create_header(jwt, [COLIN_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_draft_list_staff_missing_account_400(session, client, jwt):
    """Assert that a staff draft list request with no account ID returns a 400 status."""
    # setup

    # test
    rv = client.get('/api/v1/drafts',
                    headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_draft_list_nonstaff_unauthorized_401(session, client, jwt):
    """Assert that a non-ppr role draft list request with an account ID returns a 404 status."""
    # setup

    # test
    rv = client.get('/api/v1/drafts',
                    headers=create_header_account(jwt, [COLIN_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_draft_update_nonstaff_missing_account_400(session, client, jwt):
    """Assert that a non-staff update draft request with no account ID returns a 400 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_FINANCING)

    # test
    rv = client.put('/api/v1/drafts/TEST-FSD1',
                    json=json_data,
                    headers=create_header(jwt, [COLIN_ROLE]),
                    content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_draft_update_staff_missing_account_400(session, client, jwt):
    """Assert that a staff update draft request with no account ID returns a 400 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_FINANCING)

    # test
    rv = client.put('/api/v1/drafts/TEST-FSD1',
                    json=json_data,
                    headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]),
                    content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_draft_update_nonstaff_unauthorized_401(session, client, jwt):
    """Assert that a non-ppr role update draft request with an account ID returns a 404 status."""
    # setup
    json_data = copy.deepcopy(SAMPLE_JSON_FINANCING)

    # test
    rv = client.put('/api/v1/drafts/TEST-FSD1',
                    json=json_data,
                    headers=create_header_account(jwt, [COLIN_ROLE]),
                    content_type='application/json')
    # check
    assert rv.status_code == HTTPStatus.UNAUTHORIZED


def test_draft_get_nonstaff_missing_account_400(session, client, jwt):
    """Assert that a non-staff draft get request with no account ID returns a 400 status."""
    # setup

    # test
    rv = client.get('/api/v1/drafts/TEST-FSD1',
                    headers=create_header(jwt, [COLIN_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_draft_get_staff_missing_account_400(session, client, jwt):
    """Assert that a staff draft get request with no account ID returns a 201 status."""
    # setup

    # test
    rv = client.get('/api/v1/drafts/D-T-FS01',
                    headers=create_header(jwt, [PPR_ROLE, STAFF_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.BAD_REQUEST


def test_draft_get_nonstaff_unauthorized_401(session, client, jwt):
    """Assert that a non-ppr role draft get request with an account ID returns a 404 status."""
    # setup

    # test
    rv = client.get('/api/v1/drafts/TEST-FSD1',
                    headers=create_header_account(jwt, [COLIN_ROLE]))
    # check
    assert rv.status_code == HTTPStatus.UNAUTHORIZED
