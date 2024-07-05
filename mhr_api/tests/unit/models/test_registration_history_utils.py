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
"""Test Suite to ensure the model home registration history functions are working as expected."""
import pytest

from flask import current_app

from mhr_api.models import MhrRegistration, registration_history_utils
from mhr_api.models.type_tables import MhrRegistrationStatusTypes, MhrStatusTypes, MhrOwnerStatusTypes


# testdata pattern is ({mhr_num}, {reg_view}, {status}, {reg_count}, {note_count})
TEST_DATA = [
    ('000908', False, MhrRegistrationStatusTypes.ACTIVE, 1, 0),
    ('000909', False, MhrRegistrationStatusTypes.ACTIVE, 3, 2),
    ('000912', False, MhrRegistrationStatusTypes.EXEMPT, 2, 1),
    ('000931', False, MhrRegistrationStatusTypes.ACTIVE, 2, 1),
    ('000932', False, MhrRegistrationStatusTypes.EXEMPT, 4, 3),
    ('000908', True, MhrRegistrationStatusTypes.ACTIVE, 1, 0),
    ('000909', True, MhrRegistrationStatusTypes.ACTIVE, 3, 0),
    ('000912', True, MhrRegistrationStatusTypes.EXEMPT, 2, 0),
    ('000931', True, MhrRegistrationStatusTypes.ACTIVE, 2, 0),
    ('000932', True, MhrRegistrationStatusTypes.EXEMPT, 4, 0)
]


@pytest.mark.parametrize('mhr_num,reg_view,reg_status,reg_count,note_count', TEST_DATA)
def test_get_home_history(session, mhr_num, reg_view, reg_status, reg_count, note_count):
    """Assert that fetching a MH registration history works as expected."""
    account_id = 'PS12345'
    reg: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_num, account_id, True)
    history_json = registration_history_utils.get_history_json(reg, reg_view)
    assert history_json
    assert history_json.get('mhrNumber') == mhr_num
    assert history_json.get('statusType') == reg_status
    assert history_json.get('registrations')
    assert len(history_json['registrations']) == reg_count
    if not reg_view:
        for reg in history_json.get('registrations'):
            assert 'ownLand' in reg
            assert reg.get('createDateTime')
            assert reg.get('registrationDescription')
            assert reg.get('documentId')
            assert reg.get('documentRegistrationNumber')
        assert history_json.get('descriptions')
        assert history_json.get('locations')
        assert history_json.get('owners')
        assert history_json['descriptions'][0].get('status') == MhrStatusTypes.ACTIVE
        assert history_json['locations'][0].get('status') == MhrStatusTypes.ACTIVE
        assert history_json['owners'][0].get('status') in (MhrOwnerStatusTypes.ACTIVE, MhrOwnerStatusTypes.EXEMPT)
        for description in history_json.get('descriptions'):
            assert description.get('createDateTime')
            assert description.get('registrationDescription')
            assert description.get('status')
            if description.get('status') != MhrStatusTypes.ACTIVE:
                assert 'endDateTime' in description
                assert 'endRegistrationDescription' in description
            else:
                assert 'endDateTime' not in description
                assert 'endRegistrationDescription' not in description
        for location in history_json.get('locations'):
            assert location.get('createDateTime')
            assert location.get('registrationDescription')
            assert location.get('status')
            if location.get('status') != MhrStatusTypes.ACTIVE:
                assert 'endDateTime' in location
                assert 'endRegistrationDescription' in location
            else:
                assert 'endDateTime' not in location
                assert 'endRegistrationDescription' not in location
        for owner in history_json.get('owners'):
            assert owner.get('createDateTime')
            assert owner.get('registrationDescription')
            assert owner.get('status')
            if owner.get('status') not in (MhrOwnerStatusTypes.ACTIVE, MhrOwnerStatusTypes.EXEMPT):
                assert 'endDateTime' in owner
                assert 'endRegistrationDescription' in owner
            else:
                assert 'endDateTime' not in owner
                assert 'endRegistrationDescription' not in owner
            assert owner.get('ownerId')
            assert owner.get('groupOwnerCount')
            assert owner.get('groupCount')
            assert owner.get('groupId')
        if note_count < 1:
            assert not history_json.get('notes')
        # else:
        #    assert history_json.get('notes')
        #    assert len(history_json['notes']) == note_count
        #    assert history_json['notes'][0].get('createDateTime')
        #   assert history_json['notes'][0].get('registrationDescription')
    else:
        assert not history_json.get('descriptions')
        assert not history_json.get('locations')
        assert not history_json.get('owners')
        # assert not history_json.get('notes')
