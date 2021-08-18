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

"""Tests to assure the Previous Financing Statement Model.

Test-Suite to ensure that the Previous Financing Statement Model is working as expected.
"""
from ppr_api.models import PreviousFinancingStatement


def test_find_by_financing_id(session):
    """Assert that find a previous financing statement by financing ID contains all expected elements."""
    previous_statement = PreviousFinancingStatement.find_by_id(200000009)
    assert previous_statement
    assert previous_statement.financing_id == 200000009
    assert previous_statement.registration_type
    assert previous_statement.cb_number
    assert previous_statement.cb_date
    assert previous_statement.cr_number
    assert previous_statement.cr_date
    assert previous_statement.mhr_number
    assert previous_statement.mhr_date


def test_find_by_financing_id_invalid(session):
    """Assert that find a previous financing statement by a non-existent financing ID returns the expected result."""
    previous_statement = PreviousFinancingStatement.find_by_id(200000000)
    assert not previous_statement


def test_previous_financing_json(session):
    """Assert that the previous financing statement model renders to a json format correctly."""
    previous_statement = PreviousFinancingStatement(
        financing_id=1000,
        registration_type='TEST',
        mhr_date='2012-01-20',
        mhr_number='MH12345',
        cr_date='2012-01-21',
        cr_number='CR12345',
        cb_date='2012-01-22',
        cb_number='CB12345'
    )
    previous_statement_json = {
        'registrationType': previous_statement.registration_type,
        'mhrDate': '2012-01-20',
        'mhrNumber': 'MH12345',
        'crDate': '2012-01-21',
        'crNumber': 'CR12345',
        'cbDate': '2012-01-22',
        'cbNumber': 'CB12345'
    }

    assert previous_statement.json == previous_statement_json
