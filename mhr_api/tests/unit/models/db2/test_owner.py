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
import copy

import pytest

from flask import current_app

from mhr_api.models import Db2Owner, Db2Owngroup, MhrRegistration
from mhr_api.models.type_tables import MhrPartyTypes


OWNER_ORG = {
    'organizationName': 'ORG NAME HERE.',
    'address': {
    'street': '3122B LYNNLARK PLACE',
    'city': 'VICTORIA',
    'region': 'BC',
    'postalCode': ' ',
    'country': 'CA'
    },
    'emailAddress': 'bsmith@abc-search.com',
    'phoneNumber': '6041234567',
    'phoneExtension': '546'
}
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
   ('B', 'TEST', 'BANKRUPTCY TRUSTEE TEST', MhrPartyTypes.TRUSTEE),
   # ('B', 'TEST', 'TRUST TEST', MhrPartyTypes.TRUST),
   ('B', 'TEST', 'ADMINISTRATOR TEST', MhrPartyTypes.ADMINISTRATOR)
]
# testdata pattern is ({party_type}, {description}, {suffix})
TEST_DATA_PARTY_TYPE_CREATE = [
   (MhrPartyTypes.ADMINISTRATOR, 'Administrator of estate of John Smith', 'ADMINISTRATOR OF ESTATE OF JOHN SMITH'),
   (MhrPartyTypes.EXECUTOR, 'estate of John Smith', 'EXECUTOR ESTATE OF JOHN SMITH'),
   # (MhrPartyTypes.TRUST, 'estate of John Smith', 'TRUST ESTATE OF JOHN SMITH'),
   (MhrPartyTypes.TRUSTEE, 'Trustee of estate of John Smith, a bankrupt', 'TRUSTEE OF ESTATE OF JOHN SMITH, A BANKRUPT'),
   (MhrPartyTypes.TRUSTEE, 'Trustee of estate of John Smith', 'BANKRUPT TRUSTEE OF ESTATE OF JOHN SMITH')
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


@pytest.mark.parametrize('party_type,description,suffix', TEST_DATA_PARTY_TYPE_CREATE)
def test_party_type_create(session, party_type, description, suffix):
    json_data = copy.deepcopy(OWNER_ORG)
    json_data['partyType'] = party_type
    json_data['description'] = description
    reg: MhrRegistration = MhrRegistration(id=1)
    owner: Db2Owner = Db2Owner.create_from_registration(reg, json_data, 1, 1)
    assert owner.get_party_type() == party_type
    assert owner.suffix == suffix


def test_owner_json(session):
    """Assert that the owner renders to a json format correctly."""
    owner = Db2Owner(manuhome_id=1,
                     group_id=1,
                     owner_id=1,
                     sequence_number=1,
                     status='3',
                     type='SOLE',
                     owner_type='I',
                     verified_flag='N',
                     phone_number='6041234567',
                     postal_code='V0C 1R0',
                     name='HAMM                     DAVID          MICHAEL',
                     suffix='suffix',
                     legacy_address='P.O. BOX 1905                           FORT NELSON, BC')

    test_json = {
        'individualName' : {
            'first': 'DAVID',
            'last': 'HAMM',
            'middle': 'MICHAEL'
        },
        'phoneNumber': owner.phone_number,
        'address': {
            'city': 'FORT NELSON',
            'country': 'CA',
            'postalCode': 'V0C 1R0',
            'region': 'BC',
            'street': 'P.O. BOX 1905'
        },
        'type': owner.type,
        'status': 'ACTIVE',
        'suffix': owner.suffix,
        'partyType': 'OWNER_IND'
    }
    assert owner.json == test_json
