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
import copy

from mhr_api.models import CourtOrder
from mhr_api.models.utils import format_ts, now_ts


RENEWAL_STATEMENT = {
    'baseRegistrationNumber': 'TEST0001',
    'clientReferenceId': 'A-00000402',
    'authorizationReceived': True,
    'debtorName': {
        'businessName': 'TEST BUS 2 DEBTOR'
    },
    'registeringParty': {
        'businessName': 'ABC SEARCHING COMPANY',
        'address': {
            'street': '222 SUMMER STREET',
            'city': 'VICTORIA',
            'region': 'BC',
            'country': 'CA',
            'postalCode': 'V8W 2V8'
        },
        'emailAddress': 'bsmith@abc-search.com'
    },
    'courtOrderInformation': {
      'courtName': 'Supreme Court of British Columbia.',
      'courtRegistry': 'VICTORIA',
      'fileNumber': 'BC123495',
      'orderDate': '2021-09-05T07:01:00+00:00',
      'effectOfOrder': 'Court Order to renew Repairers Lien.'
    },
    'lifeYears': 2,
    'payment': {
        'receipt': '/pay/api/v1/payment-requests/2199700/receipts',
        'invoiceId': '2199700'
    }
}


def test_find_by_id(session):
    """Assert that find court order by court order ID contains all expected elements."""
    court_order = CourtOrder.find_by_id(200000000)
    assert court_order
    assert court_order.id == 200000000
    assert court_order.court_name
    assert court_order.court_registry
    assert court_order.order_date
    assert court_order.file_number
    assert court_order.effect_of_order


def test_find_by_registration_id(session):
    """Assert that find court order by registration id contains all expected elements."""
    court_order = CourtOrder.find_by_registration_id(200000007)
    assert court_order
    assert court_order.id == 200000000
    assert court_order.court_name
    assert court_order.court_registry
    assert court_order.order_date
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
        id=1000,
        court_name='name',
        court_registry='registry',
        file_number='file',
        effect_of_order='effect',
        order_date=now_ts()
    )

    court_json = {
        'courtName': court_order.court_name,
        'courtRegistry': court_order.court_registry,
        'fileNumber': court_order.file_number,
        'orderDate': format_ts(court_order.order_date),
        'effectOfOrder': court_order.effect_of_order
    }

    assert court_order.json == court_json
