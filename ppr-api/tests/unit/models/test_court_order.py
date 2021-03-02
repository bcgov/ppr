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

"""Tests to assure the CourtOrder Model.

Test-Suite to ensure that the Court Order Model is working as expected.
"""
from http import HTTPStatus
#from datetime import date

import pytest

from ppr_api.models import CourtOrder
from ppr_api.exceptions import BusinessException
from ppr_api.models.utils import format_ts, now_ts

import copy
from registry_schemas.example_data.ppr import RENEWAL_STATEMENT


def test_find_by_id(session):
    """Assert that find court order by court order ID contains all expected elements."""
    court_order = CourtOrder.find_by_id(200000000)
    assert court_order
    assert court_order.court_order_id == 200000000
    assert court_order.court_name
    assert court_order.court_registry
    assert court_order.court_date
    assert court_order.file_number
    assert court_order.effect_of_order

def test_find_by_registration_id(session):
    """Assert that find court order by registration id contains all expected elements."""
    court_order = CourtOrder.find_by_registration_id(200000007)
    assert court_order
    assert court_order.court_order_id == 200000000
    assert court_order.court_name
    assert court_order.court_registry
    assert court_order.court_date
    assert court_order.file_number
    assert court_order.effect_of_order

def test_find_by_id_invalid(session):
    """Assert that find court order by non-existent court order ID returns the expected result."""
    court_order = CourtOrder.find_by_id(300000000)
    assert not court_order

def test_find_by_reg_id_invalid(session):
    """Assert that find court_order by non-existent registration id eturns the expected result."""
    court_order = CourtOrder.find_by_registration_id(300000000)
    assert not court_order

def test_court_order_json(session):
    """Assert that the court order model renders to a json format correctly."""
    court_order = CourtOrder(
        court_order_id=1000,
        court_name='name',
        court_registry='registry',
        file_number='file',
        effect_of_order='effect',
        court_date=now_ts()
    )

    court_json = {
        'courtName': court_order.court_name,
        'courtRegistry': court_order.court_registry,
        'fileNumber': court_order.file_number,
        'orderDate': format_ts(court_order.court_date),
        'effectOfOrder': court_order.effect_of_order
    }

    assert court_order.json == court_json


def test_create_from_renewal_json(session):
    """Assert that the renewal statement json renders to the court order model correctly."""
    json_data = copy.deepcopy(RENEWAL_STATEMENT)

    court_order = CourtOrder.create_from_json(json_data['courtOrderInformation'], 12345)
    assert court_order
    assert court_order.registration_id == 12345
    assert court_order.court_name
    assert court_order.court_registry
    assert court_order.court_date
    assert court_order.file_number
    assert court_order.effect_of_order

