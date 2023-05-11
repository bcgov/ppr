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
"""Test Suite to ensure the model utility address mapping functions are working as expected."""
import pytest

from flask import current_app

from mhr_api.models.db2 import address_utils


DB2_ADDRESS_PCODE = '2400 OAKDALE WAY                        ' + \
                    'UNIT# 129                               ' + \
                    'KAMLOOPS                                ' + \
                    'BC CA                            V8R 3L7'
DB2_ADDRESS_NO_PCODE = '2400 OAKDALE WAY                        ' + \
                    'UNIT# 129                               ' + \
                    'KAMLOOPS                                ' + \
                    '                                   BC CA'
DB2_ADDRESS_NO_ADD = '2400 OAKDALE WAY                        ' + \
                    '                                        ' + \
                    'KAMLOOPS                                ' + \
                    'BC CA                            V8R 3L7'
ADDRESS1 = {
    'street': '3122B LYNNLARK PLACE',
    'city': 'VICTORIA',
    'region': 'BC',
    'postalCode': '',
    'country': 'CA'
}
ADDRESS2 = {
    'street': '3122B LYNNLARK PLACE',
    'streetAdditional': 'SECOND FLOOR',
    'city': 'VICTORIA',
    'region': 'BC',
    'postalCode': 'v1v1v1',
    'country': 'CA'
}
ADDRESS3 = {
    'street': '3122B LYNNLARK PLACE',
    'streetAdditional': 'SECOND FLOOR',
    'city': 'VICTORIA'
}
ADDRESS4 = {
    'street': '3122B LYNNLARK PLACE',
    'city': 'VICTORIA',
    'region': 'BC',
    'postalCode': 'V1V-1V1'
}


# testdata pattern is ({street}, {street_2}, {city}, {p_code}, {db2_address})
TEST_DATA_LEGACY_ADDRESS = [
    ('2400 OAKDALE WAY', 'UNIT# 129', 'KAMLOOPS', 'V8R 3L7', DB2_ADDRESS_PCODE),
    ('2400 OAKDALE WAY', 'UNIT# 129', 'KAMLOOPS', 'V8R 3L7', DB2_ADDRESS_PCODE),
    ('2400 OAKDALE WAY', 'UNIT# 129', 'Kamloops', 'V8R 3L7', DB2_ADDRESS_PCODE),
    ('2400 OAKDALE WAY', 'Unit# 129', 'KAMLOOPS', 'V8R 3L7', DB2_ADDRESS_PCODE),
    ('2400 Oakdale Way', 'UNIT# 129', 'KAMLOOPS', 'V8R 3L7', DB2_ADDRESS_PCODE),
    ('2400 OAKDALE WAY', 'UNIT# 129', 'KAMLOOPS', None, DB2_ADDRESS_NO_PCODE),
    ('2400 OAKDALE WAY', None, 'KAMLOOPS', 'V8R 3L7', DB2_ADDRESS_NO_ADD)
]
# testdata pattern is ({street1}, {street2}, {city}, {region}, {address})
TEST_DB2_ADDRESS = [
    ('22-3949 COLUMBIA VALLEY RD', None, 'CULTUS LAKE', 'BC', '22-3949 COLUMBIA VALLEY RD              CULTUS LAKE                             BRITISH COLUMBIA'),
    ('#210A - 3120 NORTH ISLAND HIGHWAY', None, 'CAMPBELL RIVER', 'BC', '#210A - 3120 NORTH ISLAND HIGHWAY       CAMPBELL RIVER, B.C.'),
    ('33597 - 7TH AVENUE', None, 'MISSION', 'BC', '33597 - 7TH AVENUE                      MISSION BC'),
    ('101 JASPER DRIVE', None, 'LOGAN LAKE', 'BC', '101 JASPER DRIVE                        LOGAN LAKE, BC'),
    ('LAKAHAMEN TRAILER COURT', 'PAD 12, 41495 NORTH NICOMEN ROAD', 'DEROCHE', 'BC', 'LAKAHAMEN TRAILER COURT                 PAD 12, 41495 NORTH NICOMEN ROAD        DEROCHE, BC'),
    ('GREEN TREE MOBILE HOME ESTATES', 'PAD 25 15820 FRASER HIGHWAY', 'SURREY', 'BC', 'GREEN TREE MOBILE HOME ESTATES          PAD 25                                  15820 FRASER HIGHWAY                    SURREY, BC'),
    ('2269 - 30TH AVENUE NORTH', 'CRANBROOK S.S.#3, SITE 5 A-8', 'CRANBROOK', 'BC', '2269 - 30TH AVENUE NORTH                CRANBROOK, BC                           S.S.#3, SITE 5 A-8                      CRANBROOK, BC'),
    ('1870 WILLIS ROAD', None, 'CAMPBELL RIVER', 'BC', '1870 WILLIS ROAD                                                                CAMPBELL RIVER                          BRITISH COLUMBIA'),
    ('#133', '1840 - 160TH STREET', 'SURREY', 'BC', '#133                                    1840 - 160TH STREET                     SURREY                                  BC'),
    ('#61-5130 NORTH NECHAKO ROAD', None, 'PRINCE GEORGE', 'BC', '#61-5130 NORTH NECHAKO ROAD             PRINCE GEORGE                           BRITISH COLUMBIA                        CANADA'),
    ('814 UPPER CRESCENT', 'P.O. BOX 152', 'BRITTANIA BEACH', 'BC', '814 UPPER CRESCENT                      P.O. BOX 152                                                                    BRITTANIA BEACH, B.C.'),
    ('RR #2', 'BOX 2176', 'CLEARWATER', 'BC', 'RR #2                                   BOX 2176                                CLEARWATER                              B.C.'),
    ('700 MONTREAL ROAD', None, 'OTTAWA', 'ON', '700 MONTREAL ROAD                                                                                                       OTTAWA ONTARIO'),
    ('9407 - 163 AVENUE', None, 'GRANDE PRAIRIE', 'AB', '9407 - 163 AVENUE                                                                                                       GRANDE PRAIRIE, ALBERTA'),
    ('18215 105TH AVENUE', None, 'EDMONTON', 'AB', '18215 105TH AVENUE                                                                                                      EDMONTON, AB'),
    ('MADELINE HILL, SALES ASSISTANT', 'P.O. BOX 845 NO. 200 HIGHWAY #18 WEST', 'ESTEVAN', 'SK', 'MADELINE HILL, SALES ASSISTANT          P.O. BOX 845                            NO. 200 HIGHWAY #18 WEST                ESTEVAN SASKATCHEWAN'),
    ('1985 SOUTH WELLINGTON ROAD', None, 'NANAIMO', 'BC', '1985 SOUTH WELLINGTON ROAD              NANAIMO, BC')
]

# testdata pattern is ({street1}, {street2}, {city}, {region}, {country}, {p_code}, {address})
TEST_DB2_ADDRESS_NEW = [
    ('2400 OAKDALE WAY', 'UNIT# 129', 'KAMLOOPS', 'BC', 'CA', 'V8R 3L7', DB2_ADDRESS_PCODE),
    ('2400 OAKDALE WAY', 'UNIT# 129', 'KAMLOOPS', 'BC', 'CA', None, DB2_ADDRESS_NO_PCODE),
    ('2400 OAKDALE WAY', None, 'KAMLOOPS', 'BC', 'CA', 'V8R 3L7', DB2_ADDRESS_NO_ADD)
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
# testdata pattern is ({street1}, {street2}, {city}, {region}, {country}, {p_code}, {address})
TEST_DB2_ADDRESS_NOTE = [
#    ('', '', '', 'BC', 'CA', '', ''),
    ('2779 STAUTW ROAD', '', 'CEDAR RIDGE MANUFACTURED HOME PARK', 'BC', 'CA', 'V8M 2C8', '2779 STAUTW ROAD                        CEDAR RIDGE MANUFACTURED HOME PARK      V8M 2C8'),
    ('PO BOX 309', '', 'RED LAKE FALLS', 'MN', 'US', '56750 0309', 'PO BOX 309                              RED LAKE FALLS , MN                     USA                           56750 0309'),
    ('784 5 112TH STREET', '', 'TACOMA', 'WA', 'US', '98448', '784 5 112TH STREET                      TACOMA WA  USA  98448'),
    ('9500 JIM BAILEY ROAD', '', 'KELOWNA', 'BC', 'CA', 'V4V 1S5', '9500 JIM BAILEY ROAD                      KELOWNA, BC V4V 1S5'),
    ('550 BOOTH BEND ROAD', 'PO BOX 388', 'MCMINNVILLE', 'OR', 'US', '97128', '550 BOOTH BEND ROAD                     PO BOX 388                              MCMINNVILLE, OREGON  USA 97128'),
    ('1605 PERKINS ROAD', '', 'CAMPBELL RIVER', 'BC', 'CA', 'V9W 4R8', '1605 PERKINS ROAD                                                                                                       CAMPBELL RIVER BC V9W4R8'),
    ('1605 PERKINS ROAD', '', 'CAMPBELL RIVER', 'BC', 'CA', 'V9W 4R8', '1605 PERKINS ROAD                       CAMPBELL RIVER BC                       V9W4R8'),
    ('MILLERSBURG OREGON', '3737 PALM HARBOR DRIVE', 'MILLERSBURG', 'OR', 'US', '97321', 'MILLERSBURG OREGON                      3737 PALM HARBOR DRIVE                  MILLERSBURG , OR                        USA                           97321'),
    ('REGENCY CHRYSLER', '150 JUNIPER STREET', 'QUESNEL', 'BC', 'CA', 'V2J 4C6', 'REGENCY CHRYSLER                        150 JUNIPER STREET                      QUESNEL , BC                            CANADA                        V2J 4C6'),
    ('936 YELLOWHEAD HWY', None, 'KAMLOOPS', 'BC', 'CA', 'V2H 1A2', '936 YELLOWHEAD HWY                      KAMLOOPS                                BC                                      V2H 1A2'),
    ('C/O BOX 2200', None, 'MERRITT', 'BC', 'CA', 'V1K 1B8', 'C/O BOX 2200                            MERRITT , BC                            CANADA                        V1K 1B8')
]
TEST_DB2_ADDRESS_NOTE2 = [
#    ('', '', '', 'BC', 'CA', '', ''),
    ('PO BOX 309', '', 'RED LAKE FALLS', 'MN', 'US', '56750 0309', 'PO BOX 309                              RED LAKE FALLS , MN                     USA                           56750 0309')
]
TEST_DB2_ADDRESS_DOCUMENT = [
    ('BOX 253', '', 'FRASER LAKE', 'BC', 'CA', 'V0J 1S0', 'BOX 253                                 FRASER LAKE V0J 1S0'),
    ('4 ST. GERMAIN', '', 'SAWYERVILLE', 'QC', 'CA', 'J0B 3A0', '4 ST. GERMAIN                           SAWYERVILLE QUEBEC      J0B 3A0'),
    ('NOTARY PUBLIC', '201 - 575 QUEBEC STREET', 'PRINCE GEORGE', 'BC', 'CA', 'V2L 1W6', 'NOTARY PUBLIC                           201 - 575 QUEBEC STREET                 PRINCE GEORGE BC  V2L 1W6'),
    ('10404 NEWPORT HWY', '', 'SPOKANE', 'WA', 'US', '99218', '10404 NEWPORT HWY                       SPOKANE , WA                            USA                           99218'),
    ('503 STEELE STREET', '', 'WHITEHORSE', 'YT', 'CA', 'Y1A 2Y9', '503 STEELE STREET                       WHITEHORSE YK  Y1A 2Y9'),
    ('BOX 29', '', 'CRESCENT VALLEY', 'BC', 'CA', 'V0G 1H0', 'BOX 29                                  CRESCENT VALLEY                         V0G 1H0'),
    ('DAWSON CREEK', '', '', '', '', '', 'DAWSON CREEK'),
    ('1985 SOUTH WELLINGTON ROAD', '', 'NANAIMO', '', '', '', '1985 SOUTH WELLINGTON ROAD              NANAIMO'),
    ('P.O. BOX 1873', '', 'FERNIE', 'BC', 'CA', 'V0B 1M0', 'P.O. BOX 1873                                                                   FERNIE                    BC V0B 1M0    CANADA'),
    ('936 YELLOWHEAD HWY', '', 'KAMLOOPS', 'BC', 'CA', 'V2H 1A2', '936 YELLOWHEAD HWY                      KAMLOOPS                                BC                                      V2H 1A2'),
    ('BROOKE DOWNS VENNARD LLP', 'PO BOX 67', 'SALMON ARM', 'BC', 'CA', 'V1E 4N2', 'BROOKE DOWNS VENNARD LLP                PO BOX 67                               SALMON ARM BC  V1E 4N2'),
    ('16-6245 METAL DRIVE', '', 'NANAIMO', 'BC', 'CA', 'V9T 2L9', '16-6245 METAL DRIVE                     NANAIMO BC  V9T 2L9'),
    ('940 BLANSHARD', '', 'VICTORIA', 'BC', 'CA', '', '940 BLANSHARD                           VICTORIA BC'),
    ('P.O. BOX 2400', '1018B-7TH AVENUE', 'INVERMERE', 'BC', 'CA', 'V0A 1K0', 'P.O. BOX 2400                           1018B-7TH AVENUE                        INVERMERE                 BC V0A 1K0    CANADA')
]
TEST_DB2_ADDRESS_OWNER = [
#    ('', '', '', 'BC', 'CA', '', ''),
    ('233-16TH AVENUE SOUTH', '', 'CRANBROOK', 'BC', 'CA', '', '233-16TH AVENUE SOUTH                   CRANBROOK                               BC                                      V1C 2Z5'),
    ('STUTTGARTER STRASSE 56', '74321 BIETIGHEIM', 'BISSINGEN', '', 'DE', '', 'STUTTGARTER STRASSE 56                  74321 BIETIGHEIM                        BISSINGEN, GERMANY'),
    ('45116 YALE ROAD WEST', 'PO BOX 158', 'CHILLIWACK', 'BC', 'CA', 'V0M 1K0', '45116 YALE ROAD WEST                    PO BOX 158                              CHILLIWACK BC'),
    ('PO BOX 529, STATION C', '82 WINNIPEG STREET', 'GOOSE BAY, LABRADOR', 'NL', 'CA', 'V0M 1K0', 'PO BOX 529, STATION C                   82 WINNIPEG STREET                      GOOSE BAY, LABRADOR, NL'),
    ('1510-211 AVENUE N.E.', 'BOX 46, SITE 10, RR#6', 'EDMONTON', 'AB', 'CA', 'V0M 1K0', '1510-211 AVENUE N.E.                    BOX 46, SITE 10, RR#6                   EDMONTON                                ALBERT'),
    ('98-1277 KAAHUMANU STREET', 'SUITE 106-729', 'AIEA', 'HI', 'US', '92054', '98-1277 KAAHUMANU STREET                SUITE 106-729                           AIEA, HAWAII                            USA'),
    ('11 WILLIAM STREET', '', 'UPPER KINGSCLEAR', 'NB', 'CA', 'V0M 1K0', '11 WILLIAM STREET                       UPPER KINGSCLEAR, NEW BRUNSWICK'),
    ('P.O. BOX 1804', '', 'GARIBALDI HIGHLANDS', '', 'CA', 'V0M 1K0', 'P.O. BOX 1804                                                                                                           GARIBALDI HIGHLANDS'),
    ('#715, 603 SEAGAZE DRIVE', '', 'OCEANSIDE', 'CA', 'US', '92054', '#715, 603 SEAGAZE DRIVE                 OCEANSIDE, CA                           U.S.A.   92054')
]
# testdata pattern is ({address}, {p_code}, {legacy_address})
TEST_DB2_ADDRESS_OWNER_FORMAT = [
    (ADDRESS1, '', '3122B LYNNLARK PLACE                    VICTORIA                                BC CA                                                                           '),
    (ADDRESS2, 'V1V 1V1', '3122B LYNNLARK PLACE                    SECOND FLOOR                            VICTORIA                                BC CA                                   '),
    (ADDRESS3, '', '3122B LYNNLARK PLACE                    SECOND FLOOR                            VICTORIA                                                                        '),
    (ADDRESS4, 'V1V 1V1', '3122B LYNNLARK PLACE                    VICTORIA                                BC CA                                                                           ')
]


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
    value = address_utils.to_db2_address(address)
    assert value == db2_address


@pytest.mark.parametrize('street1, street2, city, region, address', TEST_DB2_ADDRESS)
def test_db2_address(session, street1, street2, city, region, address):
    """Assert that parsing a legacy db2 address works as expected."""
    test_address = address_utils.get_address_from_db2(address)
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
    test_address = address_utils.get_address_from_db2(address)
    # current_app.logger.info(test_address)
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
    

@pytest.mark.parametrize('street1, street2, city, region, country, p_code, address', TEST_DB2_ADDRESS_NOTE)
def test_db2_address_note(session, street1, street2, city, region, country, p_code, address):
    """Assert that parsing a legacy db2 document note address works as expected."""
    test_address = address_utils.get_address_from_db2(address)
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
    test_address = address_utils.get_address_from_db2_manufact(address)
    current_app.logger.info(test_address)
    assert test_address['street'] == street1
    assert test_address['city'] == city
    assert test_address['region'] == region
    assert test_address['country'] == country
    assert test_address['postalCode'] == postal_code
    

@pytest.mark.parametrize('street1, street2, city, region, country, p_code, address', TEST_DB2_ADDRESS_DOCUMENT)
def test_db2_address_document(session, street1, street2, city, region, country, p_code, address):
    """Assert that parsing a legacy db2 document address works as expected."""
    test_address = address_utils.get_address_from_db2(address)
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
    

@pytest.mark.parametrize('street1, street2, city, region, country, p_code, address', TEST_DB2_ADDRESS_OWNER)
def test_db2_address_owner(session, street1, street2, city, region, country, p_code, address):
    """Assert that parsing a legacy db2 owner address works as expected."""
    test_address = address_utils.get_address_from_db2_owner(address, p_code)
    current_app.logger.info(test_address)
    assert test_address['street'] == street1
    assert test_address['city'] == city
    assert test_address['region'] == region
    assert test_address['country'] == country
    if p_code:
        assert test_address['postalCode'] == p_code
    if street2:
        assert test_address['streetAdditional'] == street2
    else:
        assert not test_address.get('streetAdditional')


@pytest.mark.parametrize('address, p_code, legacy_address', TEST_DB2_ADDRESS_OWNER_FORMAT)
def test_db2_address_owner_format(session, address, p_code, legacy_address):
    """Assert that formatting an address to  the legacy owner format works as expected."""
    test_address: str = address_utils.to_db2_owner_address(address)
    assert test_address == legacy_address
    test_pcode = address_utils.format_postal_code(address)
    assert p_code == test_pcode
    address_json = address_utils.get_address_from_db2_owner(test_address, test_pcode)
    assert address_json.get('street') == address.get('street')
    assert address_json.get('streetAdditional', '') == address.get('streetAdditional', '')
    assert address_json.get('city', '') == address.get('city', '')
    assert address_json.get('region', '') == address.get('region', '')
    assert address_json.get('postalCode', '') == test_pcode
    if address.get('country'):
        assert address_json.get('country') == address.get('country')
    elif address.get('region'):
        assert address_json.get('country')
