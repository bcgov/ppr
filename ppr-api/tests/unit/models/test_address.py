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

from ppr_api.models import Address


BASE_ADDRESS = {
    'street': 'STREET',
    'streetAdditional': 'STREET2',
    'city': 'CITY',
    'region': 'BC',
    'country': 'CA',
    'postalCode': 'V8V 1V1'
}

# testdata pattern is ({hasStreet}, {hasCity}, {hasRegion}, {hasCountry}, {hasPostalCode})
TEST_LEGACY_DATA = [
    (True, False, False, False, False),
    (False, True, False, False, False),
    (False, False, True, False, False),
    (False, False, False, True, False),
    (False, False, False, False, True)
]
# testdata pattern is ({equal}, {street}, {street2}, {city}, {region}, {country}, {postalCode})
TEST_EQUALITY_DATA = [
    (True, 'street', 'street2', 'city', 'BC', 'CA', 'V8V 1V1'),
    (False, 'street', None, 'city', 'BC', 'CA', 'V8V 1V1'),
    (False, 'street', 'street2', None, 'BC', 'CA', 'V8V 1V1'),
    (False, 'street', 'street2', 'city', None, 'CA', 'V8V 1V1'),
    (False, 'street', 'street2', 'city', 'BC', None, 'V8V 1V1'),
    (False, 'street', 'street2', 'city', 'BC', 'CA', None),
    (False, 'xtreet', 'street2', 'city', 'BC', 'CA', 'V8V 1V1'),
    (False, 'street', 'xstreet2', 'city', 'BC', 'CA', 'V8V 1V1'),
    (False, 'street', 'street2', 'xcity', 'AB', 'CA', 'V8V 1V1'),
    (False, 'street', 'street2', 'city', 'BC', 'US', 'V8V 1V1'),
    (False, 'street', 'street2', 'city', 'BC', 'CA', 'V8X 1V1')
]
# testdata pattern is ({test_value}, {country}, {expected_value})
TEST_POSTAL_CODE_DATA = [
    ('V8V 1V1', 'CA', 'V8V 1V1'),
    ('V8V1V1', 'CA', 'V8V 1V1'),
    ('V8V 1V1', None, 'V8V 1V1'),
    ('V8V 1V1', 'US', 'V8V 1V1'),
    ('V8V1V1', None, 'V8V1V1'),
    ('V8V1V1', 'US', 'V8V1V1')
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


def test_save(session):
    """Assert that creating an address works as expected."""
    address_json = {
        'street': 'street1',
        'streetAdditional': 'street2',
        'city': 'city',
        'region': 'BC',
        'country': 'CA',
        'postalCode': 'V8S3R6'
    }
    address = Address.create_from_json(address_json)
    address.save()
    assert address.id


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


@pytest.mark.parametrize('equal,street,street2,city,region,country,postal_code', TEST_EQUALITY_DATA)
def test_address_equality(session, equal, street, street2, city, region, country, postal_code):
    """Assert that the address equality check works as expected."""
    address_json = {
        'street': street,
        'streetAdditional': street2,
        'city': city,
        'region': region,
        'country': country,
        'postalCode': postal_code
    }
    address = Address.create_from_json(address_json)
    address_json = address.json
    if equal:
        assert address_json == BASE_ADDRESS
    else:
        assert address_json != BASE_ADDRESS


@pytest.mark.parametrize('test_value,country,expected_value', TEST_POSTAL_CODE_DATA)
def test_postal_code_format(session, test_value, country, expected_value):
    """Assert that the Canada address postal code formatting works as expected."""
    address_json = {
        'street': 'street',
        'city': 'city',
        'region': 'BC',
        'country': country,
        'postalCode': test_value
    }
    address = Address.create_from_json(address_json)
    assert address.postal_code == expected_value
