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

"""Tests to assure the Address Model.

Test-Suite to ensure that the Address Model is working as expected.
"""
import pytest

from mhr_api.models import Address


# testdata pattern is ({hasStreet}, {hasCity}, {hasRegion}, {hasCountry}, {hasPostalCode})
TEST_LEGACY_DATA = [
    (True, False, False, False, False),
    (False, True, False, False, False),
    (False, False, True, False, False),
    (False, False, False, True, False),
    (False, False, False, False, True)
]


def test_find_by_id(session):
    """Assert that find address by id contains all expected elements."""
    address = Address.find_by_id(200000000)
    assert address
    assert address.id
    if address:
        json_data = address.json
        assert json_data['street']
        assert json_data['streetAdditional']
        assert json_data['city']
        assert json_data['region']
        assert json_data['postalCode']
        assert json_data['country']


def test_find_by_id_legacy(session):
    """Assert that find address by id with missing properties contains all expected elements."""
    address = Address.find_by_id(200000034)
    assert address
    assert address.id
    assert address.street
    assert address.city
    json_data = address.json
    assert json_data['street']
    assert json_data['city']
    assert 'streetAdditional' not in json_data
    assert 'region' not in json_data
    assert 'postalCode' not in json_data
    assert 'country' not in json_data


def test_address_json(session):
    """Assert that the address renders to a json format correctly."""
    address = Address(
        street='Street',
        street_additional='Street 2',
        city='Test City',
        postal_code='T3S3T3',
        country='CA',
        region='BC'
    )

    address_json = {
        'street': address.street,
        'streetAdditional': address.street_additional,
        'city': address.city,
        'region': address.region,
        'country': address.country,
        'postalCode': address.postal_code
    }
    assert address.json == address_json


# testdata pattern is ({hasStreet}, {hasCity}, {hasRegion}, {hasCountry}, {hasPostalCode})
@pytest.mark.parametrize('street,city,region,country,postal_code', TEST_LEGACY_DATA)
def test_address_legacy_json(session, street, city, region, country, postal_code):
    """Assert that the address with poor legacy data renders to a json format correctly."""
    address = Address(id=1)
    if street:
        address.street = 'street'
    if city:
        address.city = 'city'
    if region:
        address.region = 'BC'
    if country:
        address.country = 'CA'
    if postal_code:
        address.postal_code = 'V8V1V1'

    address_json = address.json
    if street:
        assert address_json['street']
    else:
        assert 'street' not in address_json
    if city:
        assert address_json['city']
    else:
        assert 'city' not in address_json
    if region:
        assert address_json['region']
    else:
        assert 'region' not in address_json
    if country:
        assert address_json['country']
    else:
        assert 'country' not in address_json
    if postal_code:
        assert address_json['postalCode']
    else:
        assert 'postalCode' not in address_json
