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

"""Tests to assure the MhrServiceAgreement Model.

Test-Suite to ensure that the model for MHR service agreement documents is working as expected.
"""
import json
import copy

import pytest

from mhr_api.models import MhrServiceAgreement
from mhr_api.models.mhr_service_agreement import DEFAULT_AGREEMENT_TYPE
from mhr_api.models.utils import format_ts


# testdata pattern is ({id}, {has_results})
TEST_ID_DATA = [
    (1, True),
    (200000000, False)
]
# testdata pattern is ({version}, {has_results})
TEST_VERSION_DATA = [
    ('v1', True),
    ('v1000', False)
]
# testdata pattern is ({account_id}, {username}, {has_results})
TEST_ACCEPT_DATA = [
    ('3026', 'UT-test-qa', True),
    ('JUNK', 'JUNK', False)
]
# testdata pattern is ({id}, {version}, {current_version}, {agree_type}, {doc_url} )
TEST_CURRENT_DATA = [
    (1, 'v1', 'Y', DEFAULT_AGREEMENT_TYPE, 'default/v1/QS-Terms-of-Use.pdf')
]

TEST_JSON = {
    'agreementType': 'DEFAULT',
    'version': 'v1',
    'latestVersion': True,
    'createDateTime': '?'
}
TEST_ACCEPT_JSON = {
    'agreementType': 'DEFAULT',
    'version': 'v1',
    'latestVersion': True,
    'accepted': True,
    'acceptedDateTime': '2023-09-22T17:28:17+00:00'
}



@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_id(session, id, has_results):
    """Assert that finding service agreement info by ID contains all expected elements."""
    agreement: MhrServiceAgreement = MhrServiceAgreement.find_by_id(id)
    if has_results:
        assert agreement
        assert agreement.id == id
        assert agreement.agreement_type == DEFAULT_AGREEMENT_TYPE
        assert agreement.create_ts
        assert agreement.version
        assert agreement.current_version
        assert agreement.doc_storage_url
    else:
        assert not agreement


@pytest.mark.parametrize('version, has_results', TEST_VERSION_DATA)
def test_find_by_version(session, version, has_results):
    """Assert that finding service agreement info by version contains all expected elements."""
    agreement: MhrServiceAgreement = MhrServiceAgreement.find_by_version(version)
    if has_results:
        assert agreement
        assert agreement.id
        assert agreement.agreement_type == DEFAULT_AGREEMENT_TYPE
        assert agreement.create_ts
        assert agreement.version == version
        assert agreement.current_version
        assert agreement.doc_storage_url
    else:
        assert not agreement


@pytest.mark.parametrize('id, version, current_version, agree_type, doc_url', TEST_CURRENT_DATA)
def test_find_by_current(session, id, version, current_version, agree_type, doc_url):
    """Assert that finding service agreement info by current version contains all expected elements."""
    agreement: MhrServiceAgreement = MhrServiceAgreement.find_by_current()
    assert agreement
    assert agreement.id == id
    assert agreement.agreement_type == agree_type
    assert agreement.create_ts
    assert agreement.version == version
    assert agreement.current_version == current_version
    assert agreement.doc_storage_url == doc_url


@pytest.mark.parametrize('account_id, username, has_results', TEST_ACCEPT_DATA)
def test_update_profile(session, account_id, username, has_results):
    """Assert that updating the user profile with the service agreement information is as expected."""
    update_count: int = MhrServiceAgreement.update_user_profile(TEST_ACCEPT_JSON, account_id, username)
    if has_results:
        assert update_count > 0
    else:
        assert update_count == 0


@pytest.mark.parametrize('account_id, username, has_results', TEST_ACCEPT_DATA)
def test_get_profile(session, account_id, username, has_results):
    """Assert that fetching the agreement info from the user profile works as expected."""
    agreement_json: dict = MhrServiceAgreement.get_agreement_profile(account_id, username)
    if has_results:
        assert agreement_json
        assert 'acceptAgreementRequired' in agreement_json and not agreement_json.get('acceptAgreementRequired')
        assert agreement_json.get('accepted')
        assert agreement_json.get('version')
        assert agreement_json.get('acceptedDateTime')
    else:
        assert not agreement_json


def test_find_all_json(session):
    """Assert that finding all service agreements as json renders correctly."""
    agreements_json = MhrServiceAgreement.find_all_json()
    assert agreements_json
    for agreement in agreements_json:
        assert agreement.get('agreementType')
        assert agreement.get('version')
        assert agreement.get('createDateTime')
        assert agreement.get('latestVersion')
  

def test_service_agreement_json(session):
    """Assert that the service agreement model renders to a json format correctly."""
    agreement: MhrServiceAgreement = MhrServiceAgreement.find_by_current()
    agreement_json = copy.deepcopy(TEST_JSON)
    agreement_json['createDateTime'] = format_ts(agreement.create_ts)
    assert agreement.json == agreement_json
