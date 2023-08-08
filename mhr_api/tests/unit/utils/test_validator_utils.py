# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Common validator utils validation tests."""
import copy

from flask import current_app
import pytest
from registry_schemas import utils as schema_utils
from registry_schemas.example_data.mhr import DESCRIPTION

from mhr_api.models import utils as model_utils
from mhr_api.utils import validator_utils


INVALID_TEXT_CHARSET = 'TEST \U0001d5c4\U0001d5c6/\U0001d5c1 INVALID'

# testdata pattern is ({description}, {rebuilt}, {other}, {csa_num}, {eng_date}, {staff}, {message content})
TEST_DESCRIPTION_DATA = [
    ('Non utf-8 rebuilt remarks', INVALID_TEXT_CHARSET, None, None, None, True, None),
    ('Non utf-8 other remarks', None, INVALID_TEXT_CHARSET, None, None, True, None),
    ('Staff no csa, engineer', 'remarks', 'other', None, None, True, None),
    ('Non-staff csa', 'remarks', 'other', '1234', None, False, None),
    ('Non-staff eng date', 'remarks', 'other', None, '2023-06-09T19:00:00+00:00', False, None),
    ('Non-staff no csa, eng date', 'remarks', 'other', None, None, False,
     validator_utils.DESCRIPTION_CSA_ENGINEER_REQUIRED)
]
# testdata pattern is ({description}, {year}, {make}, {model}, {year_offset}, {staff}, {message content})
TEST_DESCRIPTION_DATA2 = [
    ('Valid all', 2020, 'CHAMPION', 'DELUXE 5000', 0, True, None),
    ('Valid min year', 1900, 'CHAMPION', 'DELUXE 5000', 0, True, None),
    ('Valid next year', None, 'CHAMPION', 'DELUXE 5000', 1, True, None),
    ('Valid no make', 2020, None, 'DELUXE 5000', 0, True, None),
    ('Valid no model', 2020, 'CHAMPION', None, 0, True, None),
    ('Invalid future year', None, 'CHAMPION', 'DELUXE 5000', 2, False, validator_utils.DESCRIPTION_YEAR_INVALID),
    ('Invalid year missing', None, 'CHAMPION', 'DELUXE 5000', 0, False, validator_utils.DESCRIPTION_YEAR_REQUIRED),
    ('Invalid no make or model', 2020, None, None, 0, True, validator_utils.DESCRIPTION_MAKE_MODEL_REQUIRED)
]


@pytest.mark.parametrize('desc,rebuilt,other,csa_num,eng_date,staff,message_content', TEST_DESCRIPTION_DATA)
def test_validate_description(session, desc, rebuilt, other, csa_num, eng_date, staff, message_content):
    """Assert that description validation works as expected."""
    # setup
    description = copy.deepcopy(DESCRIPTION)
    if rebuilt:
        description['rebuiltRemarks'] = rebuilt
    elif other:
        description['otherRemarks'] = other
    if csa_num:
        description['csaNumber'] = csa_num
    else:
        del description['csaNumber']
        del description['csaStandard']
    if eng_date:
        description['engineerDate'] = eng_date
        description['engineerName'] = 'ENG NAME'
    else:
        del description['engineerDate']
        del description['engineerName']
    if not staff:
        description['baseInformation']['year'] = model_utils.now_ts().year
    error_msg = validator_utils.validate_description(description, staff)
    if message_content:
        assert error_msg.find(message_content) != -1
    else:
        assert not error_msg


@pytest.mark.parametrize('desc,year,make,model,year_offset,staff,message_content', TEST_DESCRIPTION_DATA2)
def test_validate_description2(session, desc, year, make, model, year_offset, staff, message_content):
    """Assert that description validation works as expected."""
    # setup
    description = copy.deepcopy(DESCRIPTION)
    if year:
        description['baseInformation']['year'] = year
    elif year_offset > 0:
       description['baseInformation']['year'] = (model_utils.now_ts().year + year_offset) 
    else:
        del description['baseInformation']['year']
    if make:
        description['baseInformation']['make'] = make
    else:
        del description['baseInformation']['make']
    if model:
        description['baseInformation']['model'] = model
    else:
        description['baseInformation']['model'] = ''

    error_msg = validator_utils.validate_description(description, staff)
    if message_content:
        assert error_msg.find(message_content) != -1
    else:
        assert not error_msg
