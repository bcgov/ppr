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
"""Test Suite to ensure the PPR address schema is valid.

"""
import copy

from registry_schemas import validate
from registry_schemas.example_data.ppr import ADDRESS


def test_valid_address():
    """Assert that the schema is performing as expected."""
    is_valid, errors = validate(ADDRESS, 'address', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert is_valid


def test_valid_address_null_region():
    """Assert that region is allowed to be null."""
    address = copy.deepcopy(ADDRESS)
    address['region'] = None

    is_valid, errors = validate(address, 'address', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert is_valid


def test_invalid_address_street():
    """Assert that an invalid address fails - street too long"""
    address = copy.deepcopy(ADDRESS)
    address['street'] = 'This is a really long string, over the 50 char maximum.'

    is_valid, errors = validate(address, 'address', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid


def test_invalid_address_city():
    """Assert that an invalid address fails - city too long"""
    address = copy.deepcopy(ADDRESS)
    address['city'] = 'This is a really long string, over the 40 char maximum'

    is_valid, errors = validate(address, 'address', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid


def test_invalid_address_postal():
    """Assert that an invalid address fails - postal code too long."""
    address = copy.deepcopy(ADDRESS)
    address['postalCode'] = '0123456789ABCDEF'

    is_valid, errors = validate(address, 'address', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid


def test_invalid_address_street_missing():
    """Assert that an invalid address fails - required street missing"""
    address = copy.deepcopy(ADDRESS)
    del address['street']

    is_valid, errors = validate(address, 'address', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid


def test_invalid_address_city_missing():
    """Assert that an invalid address fails - required city missing."""
    address = copy.deepcopy(ADDRESS)
    del address['city']

    is_valid, errors = validate(address, 'address', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid


def test_invalid_address_missing_region():
    """Assert that an invalid address fails - missing required field address Region."""
    address = copy.deepcopy(ADDRESS)
    del address['region']

    is_valid, errors = validate(address, 'address', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid

def test_invalid_address_postal_missing():
    """Assert that an invalid address fails - required postal code missing."""
    address = copy.deepcopy(ADDRESS)
    del address['postalCode']

    is_valid, errors = validate(address, 'address', 'ppr')

    if errors:
        for err in errors:
            print(err.message)
    print(errors)

    assert not is_valid


