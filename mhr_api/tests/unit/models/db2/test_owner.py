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

"""Tests to assure the legacy DB2 Owner Model.

Test-Suite to ensure that the legacy DB2 Owner Model is working as expected.
"""

import pytest

from flask import current_app

from mhr_api.models import Db2Owner, Db2Owngroup
from mhr_api.models.type_tables import MhrPartyTypes


# testdata pattern is ({exists}, {manuhome_id}, {owner_id}, {type})
TEST_DATA = [
    (True, 1, 1, 'I'),
    (True, 104076, 1, 'B'),
    (False, 0, 0, None)
]
# testdata pattern is ({owner_type}, {name}, {suffix}, {party_type})
TEST_DATA_PARTY_TYPE = [
   ('I', 'HAMM                     DAVID          MICHAEL', '', MhrPartyTypes.OWNER_IND),
   ('B', 'TEST', '', MhrPartyTypes.OWNER_BUS),
   ('B', 'TEST', 'EXECUTOR TEST', MhrPartyTypes.EXECUTOR),
   ('B', 'TEST', 'EXECUTRIX TEST', MhrPartyTypes.EXECUTOR),
   ('B', 'TEST', 'TRUSTEE TEST', MhrPartyTypes.TRUSTEE),
   ('B', 'TEST', 'ADMINISTRATOR TEST', MhrPartyTypes.ADMINISTRATOR)
]


@pytest.mark.parametrize('exists,manuhome_id,owner_id,type', TEST_DATA)
def test_find_by_manuhome_id(session, exists, manuhome_id, owner_id, type):
    """Assert that find owners by manuhome id contains all expected elements."""
    owners: Db2Owner = Db2Owner.find_by_manuhome_id_registration(manuhome_id)
    if exists:
        assert owners
        for owner in owners:
            assert owner.manuhome_id == manuhome_id
            assert owner.group_id > 0
            assert owner.owner_id == owner_id
            assert owner.owner_type == type
            assert owner.sequence_number is not None
            assert owner.verified_flag is not None
            # assert owner.compressed_name is not None
            assert owner.phone_number is not None
            assert owner.postal_code is not None
            assert owner.name is not None
            assert owner.suffix is not None
            assert owner.legacy_address is not None
            reg_json = owner.registration_json
            current_app.logger.debug(reg_json)
            if owner.status == Db2Owngroup.StatusTypes.PREVIOUS:
                assert not reg_json
            else:
                if owner.owner_type == Db2Owner.OwnerTypes.INDIVIDUAL:
                    assert reg_json.get('individualName')
                else:
                    assert reg_json.get('organizationName')
                assert reg_json.get('address')
                assert reg_json['address']['street']
                assert reg_json['address']['city']
                assert reg_json['address']['region']
                assert reg_json['address']['country']
                assert reg_json.get('type')
                assert reg_json.get('status') in ('ACTIVE', 'EXEMPT', 'PREVIOUS')
    else:
        assert not owners


@pytest.mark.parametrize('owner_type,name,suffix,party_type', TEST_DATA_PARTY_TYPE)
def test_party_type(session, owner_type, name, suffix, party_type):
    owner: Db2Owner = Db2Owner(name=name,
                               owner_type=owner_type,
                               suffix=suffix,
                               status='3',
                               postal_code='',
                               phone_number='',
                               legacy_address='')
    assert owner.get_party_type() == party_type
    owner_json = owner.registration_json
    assert owner_json.get('partyType') == party_type
    owner_json = owner.new_registration_json
    assert owner_json.get('partyType') == party_type


def test_owner_json(session):
    """Assert that the owner renders to a json format correctly."""
    owner = Db2Owner(manuhome_id=1,
                     group_id=1,
                     owner_id=1,
                     sequence_number=1,
                     owner_type='I',
                     verified_flag='N',
                     phone_number='6041234567',
                     postal_code='V0C 1R0',
                     name='HAMM                     DAVID          MICHAEL',
                     suffix='suffix',
                     legacy_address='P.O. BOX 1905                           FORT NELSON, BC')

    test_json = {
        'manuhomeId': owner.manuhome_id,
        'groupId': owner.group_id,
        'ownerId': owner.owner_id,
        'sequenceNumber': owner.sequence_number,
        'ownerType': owner.owner_type,
        'verifiedFlag': owner.verified_flag,
        'phoneNumber': owner.phone_number,
        'postalCode': owner.postal_code,
        'name': owner.name,
        'suffix': owner.suffix,
        'legacyAddress': owner.legacy_address
    }
    assert owner.json == test_json
