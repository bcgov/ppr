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
DB2_IND_NAME_MAX = 'M.BELLERIVE-MAXIMILLIAN-JCHARLES-OLIVIERGUILLAUME-JEAN-CLAUDE-VAN-DAMN'
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
# testdata pattern is ({serial_num}, {key_value})
TEST_DATA_SERIAL_KEY = [
    ('313000Z009206AB', '920608'),
    ('WIN24440204003A', '040030'),
    ('KW2191U', '021910'),
    ('6436252B10FK', '281000'),
    ('D1644', '001644'),
    ('2427', '002427'),
    ('123', '000123'),
    ('12345', '012345'),
    ('BC123452', '123452')
]
# testdata pattern is ({valid}, {registration_ts}, {tax_cert_ts})
TEST_DATA_TAX_CERT_DATE = [
    (True, '2022-09-01T07:01:00+00:00', '2023-09-01T07:01:00+00:00'),
    (True, '2022-09-01T07:01:00+00:00', '2022-12-01T07:01:00+00:00'),
    (True, '2022-09-01T07:01:00+00:00', '2022-10-02T07:01:00+00:00'),
    (True, '2022-09-01T07:01:00+00:00', '2022-10-01T07:01:00+00:00'),
    (True, '2022-09-01T07:01:00+00:00', '2022-09-30T07:01:00+00:00'),
    (True, '2022-09-01T07:01:00+00:00', '2022-09-01T07:01:00+00:00'),
    (False, '2022-09-02T07:01:00+00:00', '2021-09-01T07:01:00+00:00'),
    (False, '2022-09-01T07:01:00+00:00', '2021-09-01T07:01:00+00:00'),
    (False, '2022-09-01T07:01:00+00:00', None)
]
# testdata pattern is ({test_ts}, {expected_ts})
TEST_DATA_TS_NO_TZ = [
    ('2024-06-01T08:00:00', '2024-06-01T15:00:00+00:00'),
    ('2024-09-01T21:00:00', '2024-09-02T04:00:00+00:00'),
    ('2024-12-01T21:00:00', '2024-12-02T05:00:00+00:00'),
    ('2024-06-01T08:00:00-07:00', '2024-06-01T15:00:00+00:00'),
    ('2024-09-01T21:00:00-07:00', '2024-09-02T04:00:00+00:00'),
    ('2024-12-01T21:00:00-08:00', '2024-12-02T05:00:00+00:00')
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


@pytest.mark.parametrize('serial_num, key_value', TEST_DATA_SERIAL_KEY)
def test_search_key_serial(session, serial_num, key_value):
    """Assert that computing a serial number search key works as expected."""
    value = model_utils.get_search_serial_number_key(serial_num)
    # current_app.logger.info(f'Key={value}')
    assert len(value) == 6
    assert value == key_value


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


def test_permit_expiry_days(session):
    """Assert that setting and computing expiry days works as expected."""
    expiry_ts = model_utils.compute_permit_expiry()
    current_app.logger.debug(model_utils.format_ts(model_utils.now_ts()))
    current_app.logger.debug(model_utils.format_ts(expiry_ts))
    expiry_days = model_utils.expiry_ts_days(expiry_ts)
    assert expiry_days == 30


@pytest.mark.parametrize('registration_ts,expected_ts', TEST_DATA_TS_NO_TZ)
def test_ts_from_iso_format_no_tz(session, registration_ts, expected_ts):
    """Assert that converting an ISO timestamp with no time zone works as expected."""
    reg_ts = model_utils.ts_from_iso_format_no_tz(registration_ts)
    test_ts = model_utils.format_ts(reg_ts)
    current_app.logger.debug(f'In={registration_ts} out={test_ts}')
    assert test_ts == expected_ts
    if len(registration_ts) > 19:
        reg_ts = model_utils.ts_from_iso_format(registration_ts)
        test_ts = model_utils.format_ts(reg_ts)
        assert test_ts == expected_ts
