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
from datetime import timedelta as _timedelta

import pytest

from flask import current_app

from mhr_api.models import utils as model_utils


DB2_IND_NAME_MIDDLE = 'DANYLUK                  LEONARD        MICHAEL                       '
DB2_IND_NAME = 'KING                     MARDI                                        '

# testdata pattern is ({last}, {first}, {middle}, {db2_name})
TEST_DATA_LEGACY_NAME = [
    ('Danyluk', 'Leonard', 'Michael', DB2_IND_NAME_MIDDLE),
    ('DANYLUK', 'Leonard', 'Michael', DB2_IND_NAME_MIDDLE),
    ('Danyluk', 'LEONARD', 'Michael', DB2_IND_NAME_MIDDLE),
    ('Danyluk', 'Leonard', 'MICHAEL', DB2_IND_NAME_MIDDLE),
    ('King', 'Mardi', None, DB2_IND_NAME),
    ('KING', 'Mardi', None, DB2_IND_NAME),
    ('King', 'MARDI', None, DB2_IND_NAME)
]
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
# testdata pattern is ({serial_num}, {hex_value})
TEST_DATA_SERIAL_KEY = [
    ('WIN14569401627', '0620DB'),
    ('A4492', '00118C'),
    ('3E3947', '04A34B'),
    ('6436252B10FK', '03DB8A'),
    ('I1724B', '002DCC'),
    ('2427', '00097B'),
    ('123', '00007B'),
    ('12345', '003039'),
    ('999999', '0F423F')
]
# testdata pattern is ({valid}, {registration_ts}, {tax_cert_ts})
TEST_DATA_TAX_CERT_DATE = [
    (True, '2022-09-01T07:01:00+00:00', '2023-09-01T07:01:00+00:00'),
    (True, '2022-09-01T07:01:00+00:00', '2022-12-01T07:01:00+00:00'),
    (True, '2022-09-01T07:01:00+00:00', '2022-10-02T07:01:00+00:00'),
    (True, '2022-09-01T07:01:00+00:00', '2022-10-01T07:01:00+00:00'),
    (False, '2022-09-01T07:01:00+00:00', '2022-09-30T07:01:00+00:00'),
    (False, '2022-09-01T07:01:00+00:00', '2022-09-01T07:01:00+00:00'),
    (False, '2022-09-01T07:01:00+00:00', '2021-09-01T07:01:00+00:00'),
    (False, '2022-09-01T07:01:00+00:00', None)
]


@pytest.mark.parametrize('last, first, middle, db2_name', TEST_DATA_LEGACY_NAME)
def test_legacy_ind_name(last, first, middle, db2_name):
    """Assert that converting to a legacy individual name works as expected."""
    name = {
        'last': last,
        'first': first
    }
    if middle:
        name['middle'] = middle
    value = model_utils.to_db2_ind_name(name)
    assert value == db2_name


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


@pytest.mark.parametrize('serial_num, hex_value', TEST_DATA_SERIAL_KEY)
def test_search_key_serial(session, serial_num, hex_value):
    """Assert that computing a serial number search key works as expected."""
    value = model_utils.get_serial_number_key_hex(serial_num)
    # current_app.logger.info(f'Key={value}')
    assert len(value) == 6
    assert value == hex_value


@pytest.mark.parametrize('valid,registration_ts,tax_cert_ts', TEST_DATA_TAX_CERT_DATE)
def test_tax_cert_date(session, valid, registration_ts, tax_cert_ts):
    """Assert that validating a tax certificate date from  a registraton ts works as expected."""
    reg_ts = model_utils.ts_from_iso_format(registration_ts)
    tax_test_ts = model_utils.ts_from_iso_format(tax_cert_ts) if tax_cert_ts else None
    is_valid: bool = model_utils.valid_tax_cert_date(reg_ts, tax_test_ts)
    if valid:
        assert is_valid
    else:
        assert not is_valid
