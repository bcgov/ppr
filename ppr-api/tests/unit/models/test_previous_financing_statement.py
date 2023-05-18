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
import pytest

from ppr_api.models import PreviousFinancingStatement


# testdata pattern is ({valid}, {financing_id})
TEST_ID_DATA = [
    (True, '200000009'),
    (False, '200000000')
]
# testdata pattern is ({cr_date}, {mhr_date}, {iso_date})
TEST_DATE_DATA = [
    ('89DEC 1', None, '1989-12-01T00:00:01-08:00'),
    (None, '80SEP 3', '1980-09-03T00:00:01-08:00'),
    ('80SEP10', None, '1980-09-10T00:00:01-08:00'),
    ('850327', None, '1985-03-27T00:00:01-08:00'),
    (None, '850327', '1985-03-27T00:00:01-08:00')
]
# testdata pattern is ({reg_type}, {cr_num}, {mhr_num}, {trans_num})
TEST_NUMBER_DATA = [
    (PreviousFinancingStatement.PreviousRegistrationTypes.ASSIGNMENT_OF_BOOK_ACCOUNTS, '2074359', None, '2074359'),
    (PreviousFinancingStatement.PreviousRegistrationTypes.FARM_CREDIT_CHATTEL_MORTGAGE, 'FC00340', None, 'FC00340'),
    (PreviousFinancingStatement.PreviousRegistrationTypes.CHATTEL_MORTGAGE, '0252722', None, '0252722'),
    (PreviousFinancingStatement.PreviousRegistrationTypes.CONDITIONAL_SALE_AGREEMENT, '0322912', None, '0322912'),
    (PreviousFinancingStatement.PreviousRegistrationTypes.CHATTEL_MORTGAGE, None, 'C29198', 'C29198'),
    (PreviousFinancingStatement.PreviousRegistrationTypes.MOBILE_HOME_ACT_DOCUMENT, None, 'C79200', 'C79200'),
    (PreviousFinancingStatement.PreviousRegistrationTypes.BILL_OF_SALE_ABSOLUTE, None, 'A16860', 'A16860'),
    (PreviousFinancingStatement.PreviousRegistrationTypes.COMPANY_ACT_DOCUMENT, 'CA20575', None, 'CA20575')
]


@pytest.mark.parametrize('valid,financing_id', TEST_ID_DATA)
def test_find_by_financing_id(session, valid, financing_id):
    """Assert that find a previous financing statement by financing ID contains all expected elements."""
    previous_statement = PreviousFinancingStatement.find_by_id(financing_id)
    if valid:
        assert previous_statement
        assert previous_statement.financing_id == 200000009
        assert previous_statement.registration_type
        assert previous_statement.cb_number
        assert previous_statement.cb_date
        assert previous_statement.cr_number
        assert previous_statement.cr_date
        assert previous_statement.mhr_number
        assert previous_statement.mhr_date
    else:
        assert not previous_statement


def test_previous_financing_json(session):
    """Assert that the previous financing statement model renders to a json format correctly."""
    previous_statement = PreviousFinancingStatement(
        financing_id=1000,
        registration_type=PreviousFinancingStatement.PreviousRegistrationTypes.COMPANY_ACT_DOCUMENT,
        cr_date='89NOV01',
        cr_number='CA21250'    )
    previous_statement_json = {
        'transitionDescription': previous_statement.registration_type,
        'transitionDate': '1989-11-01T00:00:01-08:00',
        'transitionNumber': 'CA21250'
    }
    assert previous_statement.json == previous_statement_json


@pytest.mark.parametrize('cr_date,mhr_date,iso_date', TEST_DATE_DATA)
def test_transition_date(session, cr_date, mhr_date, iso_date):
    """Assert that the transition cr and mhr dates are formatted as expected."""
    statement: PreviousFinancingStatement = PreviousFinancingStatement(cr_date=cr_date, mhr_date=mhr_date)
    test_date: str = statement.get_transition_date()
    assert test_date == iso_date


@pytest.mark.parametrize('reg_type,cr_num,mhr_num,trans_num', TEST_NUMBER_DATA)
def test_transition_number(session, reg_type, cr_num, mhr_num, trans_num):
    """Assert that the transition cr and mhr numbers are formatted as expected."""
    statement: PreviousFinancingStatement = PreviousFinancingStatement(registration_type=reg_type,
                                                                       cr_number=cr_num,
                                                                       mhr_number=mhr_num)
    test_number: str = statement.get_transition_number()
    assert test_number == trans_num
