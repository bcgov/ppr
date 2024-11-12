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
import copy

from flask import current_app

import pytest

from mhr_api.models import Address, MhrQualifiedSupplier
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
DEALER_JSON = {
    'businessName': 'TEST DEALER',
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
    'termsAccepted': True,
    'confirmRequirements': True,
    'locationAddress': {
        'street': '1704 LOCATION ST.',
        'city': 'KELOWNA',
        'region': 'BC',
        'postalCode': 'V2A 7A1',
        'country': 'CA'
    },
    'authorizationName': 'John Smith'
}
DEALER2_JSON = {
    'businessName': 'TEST DEALER',
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
    'confirmRequirements': False,
    'authorizationName': 'John Smith'
}
UPDATE_JSON = {
    'businessName': 'TEST UPDATE DEALER',
    'emailAddress': 'test2@gmail.com',
    'phoneNumber': '2508889999',
    'termsAccepted': True,
    'confirmRequirements': True,
    'locationAddress': {
        'street': '1704 LOCATION ST.',
        'city': 'KELOWNA',
        'region': 'BC',
        'postalCode': 'V2A 7A1',
        'country': 'CA'
    },
    'authorizationName': 'John Smith'
}
# testdata pattern is ({account_id}, {qs_data}, {confirm_req}, {loc_address})
TEST_SAVE_DATA = [
    ('UT00001', SUPPLIER_JSON, None, None),
    ('UT00002', DEALER_JSON, None, None),
    ('UT00002', DEALER_JSON, True, True)
]
# testdata pattern is ({account_id}, {qs_data}, {update_json})
TEST_UPDATE_DATA = [
    ('UT00001', DEALER2_JSON, UPDATE_JSON)
]


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
    qs_json = supplier.json
    if "confirmRequirements" in qs_json and "confirmRequirements" not in SUPPLIER_JSON:
        del qs_json["confirmRequirements"]
    assert SUPPLIER_JSON == qs_json


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


@pytest.mark.parametrize('account_id, qs_data, confirm_req, loc_address', TEST_SAVE_DATA)
def test_save_new_from_json(session, account_id, qs_data, confirm_req, loc_address):
    """Assert that saving a valid qualifed supplier from JSON is as expected."""
    json_data = copy.deepcopy(qs_data)
    if not confirm_req and qs_data.get("confirmRequirements"):
        del json_data["confirmRequirements"]
    if not loc_address and qs_data.get("locationAddress"):
        del json_data["locationAddress"]

    supplier: MhrQualifiedSupplier = MhrQualifiedSupplier.create_from_json(json_data,
                                                                           account_id,
                                                                           MhrPartyTypes.CONTACT)
    assert supplier
    supplier.save()
    assert supplier.id > 0
    assert supplier.party_type == MhrPartyTypes.CONTACT
    assert supplier.account_id == account_id
    assert supplier.business_name == json_data.get("businessName")
    assert supplier.address
    assert supplier.phone_number == json_data.get("phoneNumber")
    supplier_json = supplier.json
    if not confirm_req:
        assert not supplier.confirm_requirements
        assert not supplier_json.get("confirmRequirements")
    else:
        assert supplier.confirm_requirements == "Y"
        assert supplier_json.get("confirmRequirements")
    if not loc_address:
        assert not supplier.location_address_id
        assert not supplier.location_address
    else:
        assert supplier.location_address_id
        assert supplier.location_address
        assert supplier_json.get("locationAddress") == json_data.get("locationAddress")


@pytest.mark.parametrize('account_id, qs_data, update_data', TEST_UPDATE_DATA)
def test_update(session, account_id, qs_data, update_data):
    """Assert that updating a qualifed supplier from JSON is as expected."""
    supplier: MhrQualifiedSupplier = MhrQualifiedSupplier.create_from_json(qs_data,
                                                                           account_id,
                                                                           MhrPartyTypes.CONTACT)
    assert supplier
    supplier.save()
    assert supplier.id > 0
    supplier.update(update_data)
    assert supplier.account_id == account_id
    if update_data.get("businessName"):
        assert supplier.business_name == update_data.get("businessName")
    if update_data.get("phoneNumber"):
        assert supplier.phone_number == update_data.get("phoneNumber")
    supplier_json = supplier.json
    if update_data.get("termsAccepted"):
        assert supplier.terms_accepted == "Y"
        assert supplier_json.get("termsAccepted")
    if update_data.get("confirmRequirements"):
        assert supplier.confirm_requirements == "Y"
        assert supplier_json.get("confirmRequirements")
    if update_data.get("locationAddress"):
        assert supplier.location_address_id
        assert supplier.location_address
        assert supplier_json.get("locationAddress") == update_data.get("locationAddress")
