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

from mhr_api.models import Db2Owner, Db2Owngroup, MhrRegistration, utils as model_utils
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
DB2_IND_NAME_MIDDLE = 'DANYLUK                  LEONARD        MICHAEL'
DB2_IND_NAME = 'KING                     MARDI'
DB2_IND_NAME_MAX = 'M.BELLERIVE-MAXIMILLIAN-JCHARLES-OLIVIERGUILLAUME-JEAN-CLAUDE-VAN-DAMN'
ADMIN_1 = 'ADMINISTRATOR OF THE ESTATE OF ROBERT PETER RATHJE, DECEASED'
DB2_ADMIN_1 = 'PETER, ADMINISTRATOR OF THE ESTATE OF ROBERT PETER RATHJE, DECEASED'
EXEC_1 = 'EXECUTOR OF THE WILL OF ROBYN VERA MARJORIE SWARD, DECEASED'
DB2_EXEC_1 = 'ALLAN, EXECUTOR OF THE WILL OF ROBYN VERA MARJORIE SWARD, DECEASED'
TRUSTEE_1 = 'TRUSTEE OF THE ESTATE OF ROBERT DOUGLAS REID, A BANKRUPT'
DB2_TRUSTEE_1 = 'ADRIANUS, TRUSTEE OF THE ESTATE OF ROBERT DOUGLAS REID, A BANKRUPT'
# testdata pattern is ({party_type}, {last}, {first}, {middle}, {db2_name}, {suffix}, {description}, {db2_suffix})
TEST_DATA_INDIVIDUAL_NAME = [
    (MhrPartyTypes.OWNER_IND.value, 'DANYLUK', 'LEONARD', 'MICHAEL', DB2_IND_NAME_MIDDLE, '', 'IGNORE', ''),
    (MhrPartyTypes.OWNER_IND.value, 'DANYLUK', 'LEONARD', 'MICHAEL', DB2_IND_NAME_MIDDLE, 'JR.', 'IGNORE', 'JR.'),
    (MhrPartyTypes.OWNER_IND.value, 'DANYLUK', 'LEONARD', 'MICHAEL JEAN', DB2_IND_NAME_MIDDLE, '', '', 'JEAN'),
    (MhrPartyTypes.OWNER_IND.value, 'DANYLUK', 'LEONARD', 'MICHAEL JEAN CLAUDE', DB2_IND_NAME_MIDDLE, 'JR.', 'IGNORE',
     'JEAN CLAUDE, JR.'),
    (MhrPartyTypes.OWNER_IND.value,'KING', 'MARDI', None, DB2_IND_NAME, '', 'IGNORE', ''),
    (MhrPartyTypes.OWNER_IND.value,'KING', 'MARDI', None, DB2_IND_NAME, 'SR.', '', 'SR.'),
    (MhrPartyTypes.OWNER_IND.value,'M.BELLERIVE-MAXIMILLIAN-J', 'CHARLES-OLIVIER', 'GUILLAUME-JEAN-CLAUDE-VAN-DAMN',
     DB2_IND_NAME_MAX, '', '', ''),
    (MhrPartyTypes.ADMINISTRATOR.value, 'DANYLUK', 'LEONARD', 'MICHAEL PETER', DB2_IND_NAME_MIDDLE, '', ADMIN_1, DB2_ADMIN_1),
    (MhrPartyTypes.ADMINISTRATOR.value, 'DANYLUK', 'LEONARD', 'MICHAEL', DB2_IND_NAME_MIDDLE, '', ADMIN_1, ADMIN_1),
    (MhrPartyTypes.EXECUTOR.value, 'DANYLUK', 'LEONARD', 'MICHAEL ALLAN', DB2_IND_NAME_MIDDLE, '', EXEC_1, DB2_EXEC_1),
    (MhrPartyTypes.EXECUTOR.value, 'DANYLUK', 'LEONARD', 'MICHAEL', DB2_IND_NAME_MIDDLE, '', EXEC_1, EXEC_1),
    (MhrPartyTypes.TRUSTEE.value, 'DANYLUK', 'LEONARD', 'MICHAEL ADRIANUS', DB2_IND_NAME_MIDDLE, '', TRUSTEE_1, DB2_TRUSTEE_1),
    (MhrPartyTypes.TRUSTEE.value, 'DANYLUK', 'LEONARD', 'MICHAEL', DB2_IND_NAME_MIDDLE, '', TRUSTEE_1, TRUSTEE_1)
]


@pytest.mark.parametrize('exists,manuhome_id,owner_id,type', TEST_DATA)
def test_find_by_manuhome_id(session, exists, manuhome_id, owner_id, type):
    """Assert that find owners by manuhome id contains all expected elements."""
    if model_utils.is_legacy():
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
    if model_utils.is_legacy():
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
        if owner_json.get('partyType') in (MhrPartyTypes.OWNER_BUS, MhrPartyTypes.OWNER_IND):
            assert not owner_json.get('description')
        else:
            assert owner_json.get('description')


@pytest.mark.parametrize('party_type,description,suffix', TEST_DATA_PARTY_TYPE_CREATE)
def test_party_type_create(session, party_type, description, suffix):
    if model_utils.is_legacy():
        json_data = copy.deepcopy(OWNER_ORG)
        json_data['partyType'] = party_type
        json_data['description'] = description
        reg: MhrRegistration = MhrRegistration(id=1)
        owner: Db2Owner = Db2Owner.create_from_registration(reg, json_data, 1, 1)
        assert owner.get_party_type() == party_type
        assert owner.suffix == suffix
        owner_json = owner.registration_json
        assert owner_json.get('description')
        owner_json = owner.new_registration_json
        assert owner_json.get('description')


def test_owner_json(session):
    """Assert that the owner renders to a json format correctly."""
    if model_utils.is_legacy():
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
                         suffix='JR.',
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


@pytest.mark.parametrize('party_type,last,first,middle,db2_name,suffix,description,db2_suffix',
                         TEST_DATA_INDIVIDUAL_NAME)
def test_save_individual_name(session, party_type, last, first, middle, db2_name, suffix, description, db2_suffix):
    """Assert that saving a legacy individual name works as expected."""
    name = {
        'last': last,
        'first': first
    }
    if middle:
        name['middle'] = middle
    owner = {
        'partyType': party_type,
        'suffix': suffix,
        'description': description,
        'individualName': name
    }
    save_name = Db2Owner.to_legacy_individual_name(owner)
    assert len(save_name) == 70
    # current_app.logger.info(save_name)
    assert save_name == db2_name.ljust(70, ' ')
    save_suffix = Db2Owner.to_legacy_suffix(owner)
    assert db2_suffix == save_suffix


@pytest.mark.parametrize('party_type,last,first,middle,db2_name,suffix,description,db2_suffix',
                         TEST_DATA_INDIVIDUAL_NAME)
def test_individual_name_json(session, party_type, last, first, middle, db2_name, suffix, description, db2_suffix):
    """Assert that loading a legacy individual name as JSON works as expected."""
    owner: Db2Owner = Db2Owner(manuhome_id=1,
                              group_id=1,
                              owner_id=1,
                              sequence_number=1,
                              status='3',
                              type='SOLE',
                              owner_type='I',
                              verified_flag='N',
                              phone_number='6041234567',
                              postal_code='V0C 1R0',
                              name=db2_name,
                              suffix=db2_suffix,
                              legacy_address='P.O. BOX 1905                           FORT NELSON, BC')
    owner_json = owner.json
    assert owner_json.get('partyType') == party_type
    ind_name = owner_json.get('individualName')
    assert ind_name.get('first') == first
    assert ind_name.get('last') == last
    assert ind_name.get('middle') == middle
    if suffix:
        assert owner_json.get('suffix') == suffix
    else:
        assert not owner_json.get('suffix')
    if description and owner_json.get('partyType') not in (MhrPartyTypes.OWNER_BUS, MhrPartyTypes.OWNER_IND):
        assert owner_json.get('description') == description
    else:
        assert not owner_json.get('description')
