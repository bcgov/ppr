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

from flask import current_app

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
# testdata pattern is ({street1}, {street2}, {city}, {region}, {address})
TEST_DB2_ADDRESS = [
    ('22-3949 COLUMBIA VALLEY RD', None, 'CULTUS LAKE', 'BC', '22-3949 COLUMBIA VALLEY RD              CULTUS LAKE                             BRITISH COLUMBIA'),
    ('#210A - 3120 NORTH ISLAND HIGHWAY', None, 'CAMPBELL RIVER', 'BC', '#210A - 3120 NORTH ISLAND HIGHWAY       CAMPBELL RIVER, B.C.'),
    ('33597 - 7TH AVENUE', None, 'MISSION', 'BC', '33597 - 7TH AVENUE                      MISSION BC'),
    ('101 JASPER DRIVE', None, 'LOGAN LAKE', 'BC', '101 JASPER DRIVE                        LOGAN LAKE, BC'),
    ('LAKAHAMEN TRAILER COURT', 'PAD 12, 41495 NORTH NICOMEN ROAD', 'DEROCHE', 'BC', 'LAKAHAMEN TRAILER COURT                 PAD 12, 41495 NORTH NICOMEN ROAD        DEROCHE, BC'),
    ('GREEN TREE MOBILE HOME ESTATES', 'PAD 25                                  15820 FRASER HIGHWAY', 'SURREY', 'BC', 'GREEN TREE MOBILE HOME ESTATES          PAD 25                                  15820 FRASER HIGHWAY                    SURREY, BC'),
    ('2269 - 30TH AVENUE NORTH', 'CRANBROOK, BC                           S.S.#3, SITE 5 A-8', 'CRANBROOK', 'BC', '2269 - 30TH AVENUE NORTH                CRANBROOK, BC                           S.S.#3, SITE 5 A-8                      CRANBROOK, BC'),
    ('1870 WILLIS ROAD', None, 'CAMPBELL RIVER', 'BC', '1870 WILLIS ROAD                                                                CAMPBELL RIVER                          BRITISH COLUMBIA'),
    ('#133', '1840 - 160TH STREET', 'SURREY', 'BC', '#133                                    1840 - 160TH STREET                     SURREY                                  BC'),
    ('#61-5130 NORTH NECHAKO ROAD', None, 'PRINCE GEORGE', 'BC', '#61-5130 NORTH NECHAKO ROAD             PRINCE GEORGE                           BRITISH COLUMBIA                        CANADA'),
    ('814 UPPER CRESCENT', 'P.O. BOX 152', 'BRITTANIA BEACH', 'BC', '814 UPPER CRESCENT                      P.O. BOX 152                                                                    BRITTANIA BEACH, B.C.'),
    ('RR #2', 'BOX 2176', 'CLEARWATER', 'BC', 'RR #2                                   BOX 2176                                CLEARWATER                              B.C.'),
    ('700 MONTREAL ROAD', None, 'OTTAWA', 'ON', '700 MONTREAL ROAD                                                                                                       OTTAWA ONTARIO'),
    ('9407 - 163 AVENUE', None, 'GRANDE PRAIRIE', 'AB', '9407 - 163 AVENUE                                                                                                       GRANDE PRAIRIE, ALBERTA'),
    ('18215 105TH AVENUE', None, 'EDMONTON', 'AB', '18215 105TH AVENUE                                                                                                      EDMONTON, AB'),
    ('MADELINE HILL, SALES ASSISTANT', 'P.O. BOX 845                            NO. 200 HIGHWAY #18 WEST', 'ESTEVAN', 'SK', 'MADELINE HILL, SALES ASSISTANT          P.O. BOX 845                            NO. 200 HIGHWAY #18 WEST                ESTEVAN SASKATCHEWAN')
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


@pytest.mark.parametrize('street1, street2, city, region, address', TEST_DB2_ADDRESS)
def test_db2_address(session, street1, street2, city, region, address):
    """Assert that parsing a legacy db2 address works as expected."""
    test_address = model_utils.get_address_from_db2(address)
    assert test_address['street'] == street1
    assert test_address['city'] == city
    assert test_address['region'] == region
    if street2 is None:
        assert 'streetAdditional' not in test_address
    else:
        assert test_address['streetAdditional'] == street2
