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


DB2_IND_NAME_MIDDLE = 'DANYLUK                  LEONARD        MICHAEL                       '
DB2_IND_NAME = 'KING                     MARDI                                        '
DB2_ADDRESS_PCODE = '2400 OAKDALE WAY                        ' + \
                    'UNIT# 129                               ' + \
                    'KAMLOOPS                                ' + \
                    'BC CA                            V8R 16W'
DB2_ADDRESS_NO_PCODE = '2400 OAKDALE WAY                        ' + \
                    'UNIT# 129                               ' + \
                    'KAMLOOPS                                ' + \
                    '                                   BC CA'
DB2_ADDRESS_NO_ADD = '2400 OAKDALE WAY                        ' + \
                    '                                        ' + \
                    'KAMLOOPS                                ' + \
                    'BC CA                            V8R 16W'

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
# testdata pattern is ({street}, {street_2}, {city}, {p_code}, {db2_address})
TEST_DATA_LEGACY_ADDRESS = [
    ('2400 OAKDALE WAY', 'UNIT# 129', 'KAMLOOPS', 'V8R 16W', DB2_ADDRESS_PCODE),
    ('2400 OAKDALE WAY', 'UNIT# 129', 'KAMLOOPS', 'V8R16W', DB2_ADDRESS_PCODE),
    ('2400 OAKDALE WAY', 'UNIT# 129', 'Kamloops', 'V8R16W', DB2_ADDRESS_PCODE),
    ('2400 OAKDALE WAY', 'Unit# 129', 'KAMLOOPS', 'V8R16W', DB2_ADDRESS_PCODE),
    ('2400 Oakdale Way', 'UNIT# 129', 'KAMLOOPS', 'V8R16W', DB2_ADDRESS_PCODE),
    ('2400 OAKDALE WAY', 'UNIT# 129', 'KAMLOOPS', None, DB2_ADDRESS_NO_PCODE),
    ('2400 OAKDALE WAY', None, 'KAMLOOPS', 'V8R16W', DB2_ADDRESS_NO_ADD)
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
    ('MADELINE HILL, SALES ASSISTANT', 'P.O. BOX 845                            NO. 200 HIGHWAY #18 WEST', 'ESTEVAN', 'SK', 'MADELINE HILL, SALES ASSISTANT          P.O. BOX 845                            NO. 200 HIGHWAY #18 WEST                ESTEVAN SASKATCHEWAN'),
    ('1985 SOUTH WELLINGTON ROAD', None, 'NANAIMO', 'BC', '1985 SOUTH WELLINGTON ROAD              NANAIMO, BC')
]
# testdata pattern is ({street1}, {street2}, {city}, {region}, {country}, {p_code}, {address})
TEST_DB2_ADDRESS_NEW = [
    ('2400 OAKDALE WAY', 'UNIT# 129', 'KAMLOOPS', 'BC', 'CA', 'V8R 16W', DB2_ADDRESS_PCODE),
    ('2400 OAKDALE WAY', 'UNIT# 129', 'KAMLOOPS', 'BC', 'CA', None, DB2_ADDRESS_NO_PCODE),
    ('2400 OAKDALE WAY', None, 'KAMLOOPS', 'BC', 'CA', 'V8R 16W', DB2_ADDRESS_NO_ADD)
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
#3737 PALM HARBOR DRIVE                  MILLERSBURG,OR  97321   
# testdata pattern is ({street1}, {city}, {region}, {country}, {postal_code}, {address})
TEST_DB2_ADDRESS_MANUFACT = [
    ('PO BOX 190 STATION MAIN', 'PENTICTON', 'BC', 'CA', 'V2A 6J9',
     'PO BOX 190 STATION MAIN                 PENTICTON, BC V2A 6J9'),
    ('3737 PALM HARBOR DRIVE', 'MILLERSBURG', 'OR', 'US', '97321',
     '3737 PALM HARBOR DRIVE                  MILLERSBURG,OR  97321'),
    ('PO BOX 188', 'SHERIDAN', 'OR', 'US', 'USA 97378',
     'PO BOX 188                              SHERIDAN OR USA 97378'),
    ('RR1, S2,C23', 'OKANAGAN FALLS', 'BC', 'CA', 'V0H1RO',
     'RR1, S2,C23                             OKANAGAN FALLS B.C. V0H1RO')
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


@pytest.mark.parametrize('street, street_2, city, p_code, db2_address', TEST_DATA_LEGACY_ADDRESS)
def test_legacy_address(street, street_2, city, p_code, db2_address):
    """Assert that converting to a legacy address works as expected."""
    address = {
        'street': street,
        'city': city,
        'region': 'BC',
        'country': 'CA'
    }
    if street_2:
        address['streetAdditional'] = street_2
    if p_code:
        address['postalCode'] = p_code
    value = model_utils.to_db2_address(address)
    assert value == db2_address


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


@pytest.mark.parametrize('street1, street2, city, region, country, p_code, address', TEST_DB2_ADDRESS_NEW)
def test_db2_address_new(session, street1, street2, city, region, country, p_code, address):
    """Assert that parsing a legacy db2 address for a new registration works as expected."""
    test_address = model_utils.get_address_from_db2(address)
    current_app.logger.info(test_address)
    assert test_address['street'] == street1
    assert test_address['city'] == city
    assert test_address['region'] == region
    assert test_address['country'] == country
    if p_code:
        assert test_address['postalCode'] == p_code
    else:
        assert not test_address.get('postalCode')
    if street2:
        assert test_address['streetAdditional'] == street2
    else:
        assert not test_address.get('streetAdditional')
    

@pytest.mark.parametrize('street1, city, region, country, postal_code, address', TEST_DB2_ADDRESS_MANUFACT)
def test_db2_address_manufact(session, street1, city, region, country, postal_code, address):
    """Assert that parsing a legacy db2 manufact table address works as expected."""
    test_address = model_utils.get_address_from_db2_manufact(address)
    current_app.logger.info(test_address)
    assert test_address['street'] == street1
    assert test_address['city'] == city
    assert test_address['region'] == region
    assert test_address['country'] == country
    assert test_address['postalCode'] == postal_code
