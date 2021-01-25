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
from http import HTTPStatus

import pytest

from ppr_api.models import Address


def test_find_by_id(session):
    """Assert that find address by id contains all expected elements."""
    address = Address.find_by_id(200000000)
    assert address
    if address:
        json_data = address.json
        assert json_data['street']
        assert json_data['streetAdditional']
        assert json_data['city']
        assert json_data['region']
        assert json_data['postalCode']
        assert json_data['country']

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

