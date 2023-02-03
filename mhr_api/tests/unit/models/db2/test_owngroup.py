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

"""Tests to assure the legacy DB2 Owngroup Model.

Test-Suite to ensure that the legacy DB2 Owngroup Model is working as expected.
"""
import copy

import pytest

from mhr_api.models import Db2Owngroup, MhrRegistration


SOLE_OWNER_GROUP = {
    'groupId': 1,
    'owners': [
        {
        'organizationName': 'TEST BUS.',
        'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': 'V8S 4I6',
            'country': 'CA'
        },
        'phoneNumber': '6041234567'
        }
    ],
    'type': 'SOLE'
}
JOINT_OWNER_GROUP = {
    'groupId': 1,
    'owners': [
        {
        'individualName': {
            'first': 'James',
            'last': 'Smith'
        },
        'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': 'V8S 4I6',
            'country': 'CA'
        },
        'phoneNumber': '6041234567'
        }, {
        'individualName': {
            'first': 'Jane',
            'last': 'Smith'
        },
        'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': 'V8S 4I6',
            'country': 'CA'
        },
        'phoneNumber': '6041234567'
        }
    ],
    'type': 'JOINT'
}
# testdata pattern is ({exists}, {manuhome_id}, {group_id}, {reg_doc_id}, {type})
TEST_DATA = [
    (True, 101917, 1, '60164729', 'SO'),
    (False, 0, 0, None, None)
]
# testdata pattern is ({interest}, {numerator}, {denominator})
TEST_DATA_INTEREST = [
    ('', 0, 0),
    ('1/2', 1, 2),
    ('UNDIVIED 9/10', 9, 10),
    ('UNDIVIDED 3/8', 3, 8),
    ('UNDIVIDED 1/2 INT.', 1, 2),
    ('A 55/100 INTEREST', 55, 100)
]
# testdata pattern is ({tenancy_type}, {legacy_type})
TEST_DATA_JSON = [
    ('COMMON', 'TC'),
    ('JOINT', 'JT')
]
# testdata pattern is ({type}, {legacy_type}, {data})
TEST_DATA_GROUP_TYPE = [
    ('SOLE', 'SO', SOLE_OWNER_GROUP),
    ('JOINT', 'JT', JOINT_OWNER_GROUP),
    ('COMMON', 'TC', SOLE_OWNER_GROUP),
    ('NA', 'TC', SOLE_OWNER_GROUP),
    ('NA', 'JT', JOINT_OWNER_GROUP)
]


@pytest.mark.parametrize('exists,manuhome_id,group_id,reg_doc_id,type', TEST_DATA)
def test_find_by_manuhome_id(session, exists, manuhome_id, group_id, reg_doc_id, type):
    """Assert that find an owner group by manuhome id and group id contains all expected elements."""
    owngroup: Db2Owngroup = Db2Owngroup.find_by_manuhome_id(manuhome_id, group_id)
    if exists:
        assert owngroup
        assert owngroup.manuhome_id == manuhome_id
        assert owngroup.group_id == group_id
        assert owngroup.reg_document_id == reg_doc_id
        assert owngroup.tenancy_type == type
        assert owngroup.can_document_id is not None
        assert owngroup.copy_id is not None
        assert owngroup.status is not None
        assert owngroup.sequence_number is not None
        assert owngroup.pending_flag is not None
        assert owngroup.lessee is not None
        assert owngroup.lessor is not None
        assert owngroup.interest is not None
        assert owngroup.interest_numerator is not None
        assert owngroup.tenancy_specified is not None

    else:
        assert not owngroup


@pytest.mark.parametrize('exists,manuhome_id,group_id,reg_doc_id,type', TEST_DATA)
def test_find_all_by_manuhome_id(session, exists, manuhome_id, group_id, reg_doc_id, type):
    """Assert that find all owner groups by manuhome id contains all expected elements."""
    groups = Db2Owngroup.find_all_by_manuhome_id(manuhome_id)
    if exists:
        assert groups
        for owngroup in groups:
            assert owngroup.manuhome_id == manuhome_id
            assert owngroup.group_id == group_id
            assert owngroup.reg_document_id == reg_doc_id
            assert owngroup.tenancy_type == type
            assert owngroup.can_document_id is not None
            assert owngroup.copy_id is not None
            assert owngroup.status is not None
            assert owngroup.sequence_number is not None
            assert owngroup.pending_flag is not None
            assert owngroup.lessee is not None
            assert owngroup.lessor is not None
            assert owngroup.interest is not None
            assert owngroup.interest_numerator is not None
            assert owngroup.tenancy_specified is not None
    else:
        assert not groups


@pytest.mark.parametrize('exists,manuhome_id,group_id,reg_doc_id,type', TEST_DATA)
def test_find_by_reg_doc_id(session, exists, manuhome_id, group_id, reg_doc_id, type):
    """Assert that find document by manuhome id contains all expected elements."""
    groups = Db2Owngroup.find_by_reg_doc_id(manuhome_id, reg_doc_id)
    if exists:
        assert groups
        for owngroup in groups:
            assert owngroup.manuhome_id == manuhome_id
            assert owngroup.group_id == group_id
            assert owngroup.reg_document_id == reg_doc_id
            assert owngroup.tenancy_type == type
            assert owngroup.can_document_id is not None
            assert owngroup.copy_id is not None
            assert owngroup.status is not None
            assert owngroup.sequence_number is not None
            assert owngroup.pending_flag is not None
            assert owngroup.lessee is not None
            assert owngroup.lessor is not None
            assert owngroup.interest is not None
            assert owngroup.interest_numerator is not None
            assert owngroup.tenancy_specified is not None
    else:
        assert not groups


@pytest.mark.parametrize('interest, numerator, denominator', TEST_DATA_INTEREST)
def test_get_interest_fraction(interest, numerator, denominator):
    """Assert that find document by manuhome id contains all expected elements."""
    owngroup = Db2Owngroup(interest=interest, interest_numerator=1, tenancy_type='TC')
    num_value = owngroup.get_interest_fraction(True)
    den_value = owngroup.get_interest_fraction(False)
    assert num_value == numerator
    assert den_value == denominator


@pytest.mark.parametrize('tenancy_type, legacy_tenancy_type', TEST_DATA_JSON)
def test_owngroup_json(session, tenancy_type, legacy_tenancy_type):
    """Assert that the owngroup renders to a json format correctly."""
    owngroup = Db2Owngroup(manuhome_id=1,
                           group_id=1,
                           copy_id=0,
                           status='5',
                           sequence_number=1,
                           reg_document_id='REG22911',
                           can_document_id='42400339',
                           tenancy_type=legacy_tenancy_type,
                           lessee='',
                           lessor='',
                           interest='UNDIVIDED 1/2',
                           interest_numerator=1,
                           tenancy_specified='Y')

    test_json = {
        'manuhomeId': owngroup.manuhome_id,
        'groupId': owngroup.group_id,
        'copyId': owngroup.copy_id,
        'sequenceNumber': owngroup.sequence_number,
        'status': 'PREVIOUS',
        'pendingFlag': owngroup.pending_flag,
        'registrationDocumentId': owngroup.reg_document_id,
        'canDocumentId': owngroup.can_document_id,
        'type': tenancy_type,
        'lessee': owngroup.lessee,
        'lessor': owngroup.lessor,
        'interest': 'UNDIVIDED',
        'interestNumerator': owngroup.interest_numerator,
        'interestDenominator': 2,
        'tenancySpecified': True
    }
    assert owngroup.json == test_json


@pytest.mark.parametrize('tenancy_type, legacy_tenancy_type', TEST_DATA_JSON)
def test_owngroup_reg_json(session, tenancy_type, legacy_tenancy_type):
    """Assert that the owngroup renders to a registration json format correctly."""
    owngroup = Db2Owngroup(manuhome_id=1,
                           group_id=1,
                           copy_id=0,
                           status='3',
                           sequence_number=1,
                           reg_document_id='REG22911',
                           can_document_id='42400339',
                           tenancy_type=legacy_tenancy_type,
                           lessee='',
                           lessor='',
                           interest='UNDIVIDED 1/2',
                           interest_numerator=1,
                           tenancy_specified='Y')

    test_json = {
        'groupId': owngroup.group_id,
        'type': tenancy_type,
        'status': 'ACTIVE',
        'interest': 'UNDIVIDED',
        'interestNumerator': owngroup.interest_numerator,
        'interestDenominator': 2,
        'tenancySpecified': True,
        'owners': []
    }
    assert owngroup.registration_json == test_json


# testdata pattern is ({type}, {legacy_type}, {data})
@pytest.mark.parametrize('tenancy_type, legacy_tenancy_type, data', TEST_DATA_GROUP_TYPE)
def test_create_type(session, tenancy_type, legacy_tenancy_type, data):
    """Assert that the owngroup type maps from new to legacy correctly."""
    registration: MhrRegistration = MhrRegistration(id=1)
    group_data = copy.deepcopy(data)
    group_data['type'] = tenancy_type
    group: Db2Owngroup = Db2Owngroup.create_from_registration(registration, group_data, 2)
    assert group.tenancy_type == legacy_tenancy_type
