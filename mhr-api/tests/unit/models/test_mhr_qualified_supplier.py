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

"""Tests to assure the MHR qualified supplier Model.

Test-Suite to ensure that the MHR qualified supplier Model is working as expected.
"""
from flask import current_app

import pytest

from mhr_api.models import Address, MhrQualifiedSupplier, MhrParty
from  mhr_api.models.type_tables import MhrPartyTypes


# testdata pattern is ({id}, {has_results})
TEST_ID_DATA = [
    (200000000, True),
    (300000000, False)
]
# testdata pattern is ({account_id}, {has_results})
TEST_ACCOUNT_ID_DATA = [
    ('PS12345', True),
    ('JUNK', False)
]
SUPPLIER_JSON = {
    'businessName': 'TEST NOTARY PUBLIC',
    'partyType': 'CONTACT',
    'address': {
        'street': '1704 GOVERNMENT ST.',
        'city': 'PENTICTON',
        'region': 'BC',
        'postalCode': 'V2A 7A1',
        'country': 'CA'
    },
    'emailAddress': 'test@gmail.com',
    'phoneNumber': '2507701067',
    'termsAccepted': False,
    'dbaName': 'DBA NAME',
    'authorizationName': 'John Smith'
}


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_id(session, id, has_results):
    """Assert that find qualified supplier by primary key contains all expected elements."""
    supplier: MhrQualifiedSupplier = MhrQualifiedSupplier.find_by_id(id)
    if has_results:
        assert supplier
        assert supplier.id == id
        assert supplier.account_id
        assert supplier.business_name
        assert supplier.address
        assert supplier.phone_number
    else:
        assert not supplier


@pytest.mark.parametrize('account_id, has_results', TEST_ACCOUNT_ID_DATA)
def test_find_by_account_id(session, account_id, has_results):
    """Assert that find qualified supplier by account id contains all expected elements."""
    supplier: MhrQualifiedSupplier = MhrQualifiedSupplier.find_by_account_id(account_id)
    if has_results:
        assert supplier
        assert supplier.id
        assert supplier.account_id == account_id
        assert supplier.business_name
        assert supplier.address
        assert supplier.phone_number
        json_data = supplier.json
        assert json_data
        assert json_data.get('businessName')
        assert json_data.get('partyType')
        assert json_data.get('address')
        assert json_data.get('phoneNumber')
    else:
        assert not supplier


def test_supplier_json(session):
    """Assert that the qualifed supplier model renders to a json format correctly."""
    address: Address = Address.create_from_json(SUPPLIER_JSON.get('address'))
    supplier: MhrQualifiedSupplier = MhrQualifiedSupplier(id=1,
                                                          party_type=MhrPartyTypes.CONTACT,
                                                          business_name=SUPPLIER_JSON.get('businessName'),
                                                          address=address,
                                                          email_id=SUPPLIER_JSON.get('emailAddress'),
                                                          phone_number=SUPPLIER_JSON.get('phoneNumber'),
                                                          dba_name=SUPPLIER_JSON.get('dbaName'),
                                                          authorization_name=SUPPLIER_JSON.get('authorizationName'))
    # current_app.logger.debug(supplier.json)
    assert SUPPLIER_JSON == supplier.json


def test_create_from_json(session):
    """Assert that creating a valid manufacturer from JSON is as expected."""
    account_id: str = '1234'
    supplier: MhrQualifiedSupplier = MhrQualifiedSupplier.create_from_json(SUPPLIER_JSON,
                                                                           account_id,
                                                                           MhrPartyTypes.CONTACT)
    assert supplier
    assert supplier.party_type == MhrPartyTypes.CONTACT
    assert supplier.account_id == account_id
    assert supplier.business_name
    assert supplier.address
    assert supplier.phone_number


def test_save_new_from_json(session):
    """Assert that saving a valid manufacturer from JSON is as expected."""
    account_id: str = '1234'
    supplier: MhrQualifiedSupplier = MhrQualifiedSupplier.create_from_json(SUPPLIER_JSON,
                                                                           account_id,
                                                                           MhrPartyTypes.CONTACT)
    assert supplier
    supplier.save()
    assert supplier.id > 0
    assert supplier.party_type == MhrPartyTypes.CONTACT
    assert supplier.account_id == account_id
    assert supplier.business_name
    assert supplier.address
    assert supplier.phone_number
