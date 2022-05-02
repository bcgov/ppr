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
"""Test Suite to ensure the model utility functions are working as expected."""
import pytest

from mhr_api.models import utils as model_utils


# testdata pattern is ({name}, {key_value})
TEST_DATA_ORG_KEY = [
    ('REGAL HOMES (1994) LTD.', 'REGALHOMESONENINENINEFOURLTD'),
    ('0711355 B.C. LTD.', 'ZEROSEVENONEONETHREEFIVEFIVEBC'),
    ('M&K MOBILE HOMES SALES LTD.', 'MANDKMOBILEHOMESSALESLTD'),
    ('GUTHRIE HOLDINGS LTD.', 'GUTHRIEHOLDINGSLTD'),
    ('?THE GUTHRIE HOLDINGS LTD.', 'GUTHRIEHOLDINGSLTD'),
    ('THE GUTHRIE HOLDINGS LTD.', 'GUTHRIEHOLDINGSLTD'),
    ('BRITISH COLUMBIA GUTHRIE HOLDINGS LTD.', 'BCGUTHRIEHOLDINGSLTD'),
    ('BRITISH COLUMBI TEST LTD.', 'BRITISHCOLUMBITESTLTD'),
    ('WEST MOBERLY FIRST NATIONS #545', 'WESTMOBERLYFIRSTNATIONSNUMBERF'),
    ('0123456', 'ZEROONETWOTHREEFOURFIVESIX'),
    ('BC 789 INC.', 'BCSEVENEIGHTNINEINC')
]
TEST_DATA_OWNER_KEY = [
    ('SANDHU                   PRITNAM  ', 'SANDHUPRITNAM'),
    ('HOLT-COLLINS             GENEVIEVE ', 'HOLTCOLLINSGENEVIEVE'),
    ('VAN HULLEBUSH            RAYMOND        RONALD   ', 'VANHULLEBUSHRAYMONDRONALD'),
    ('MCCAUGHAN-MORRISON       MARGARET       MORRISON ', 'MCCAUGHANMORRISONMARGARETMORRI'),
    ('SCHWARTZENBERGER         RAYMOND        AMBROSE   ', 'SCHWARTZENBERGERRAYMONDAMBROSE')
]


@pytest.mark.parametrize('name, key_value', TEST_DATA_ORG_KEY)
def test_search_key_org(name, key_value):
    """Assert that computing an organization name search key works as expected."""
    value = model_utils.get_compressed_key(name)
    assert value == key_value


@pytest.mark.parametrize('name, key_value', TEST_DATA_OWNER_KEY)
def test_search_key_owner(name, key_value):
    """Assert that computing an owner name search key works as expected."""
    value = model_utils.get_compressed_key(name)
    assert value == key_value
