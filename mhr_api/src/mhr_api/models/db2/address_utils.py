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
"""This module holds utility functions for mapping legacy addresses to the new format."""
# from flask import current_app


DB2_REMOVE_TRAILING_COUNTRY = [' CA', ' US', ' USA']
DB2_REMOVE_STARTING_COUNTRY = ['CA ', 'US ', 'USA ']
# Also use this to remove values so order is important.
DB2_PROVINCE_MAPPING = {
    ', BC ': 'BC',
    ' BC ': 'BC',
    ',BC ': 'BC',
    ',BC,': 'BC',
    'BC, ': 'BC',
    'BC,': 'BC',
    ' B,.C. ': 'BC',
    ', B.C.': 'BC',
    ',B.C.': 'BC',
    ',B.C ': 'BC',
    ' B.C.': 'BC',
    ' B.C': 'BC',
    ' B . C. ': 'BC',
    'B.C. ': 'BC',
    'B C ': 'BC',
    'B..C': 'BC',
    'B. C. ': 'BC',
    '/BC/': 'BC',
    ' B,C, ': 'BC',
    ' B\\C ': 'BC',
    ' B,C. ': 'BC',
    ' B.,C,. ': 'BC',
    ', CB ': 'BC',
    ', B. C> ': 'BC',
    ', B. C ': 'BC',
    ' B>C ': 'BC',
    ', B .C. ': 'BC',
    ' BDC ': 'BC',
    ' BXC ': 'BC',
    ' B. .C ': 'BC',
    'BRITISHCOLUMBIA': 'BC',
    'BRITISH COLUMBIA': 'BC',
    'BRITSH COLUMBIA': 'BC',
    'BRITSH COLUMIA': 'BC',
    'BRITSH COLUMBIA': 'BC',
    'BTISH COLUMBIA': 'BC',
    'BRTISH COLUMBIA': 'BC',
    'BRITSIH COLUMBIA': 'BC',
    'BRITIHS COLUMBIA': 'BC',
    'BRISITH COLUMBIA': 'BC',
    'BRISTISH COLUMBIA': 'BC',
    'BRISITSH COLUMBIA': 'BC',
    'BRITISIH COLUMBIA': 'BC',
    'BRIRISH COLUMBIA': 'BC',
    'BRIISH COLUMBIA': 'BC',
    'BREITISH COLUMBIA': 'BC',
    'BRITISH COLUBIA': 'BC',
    'BREITISH COLUMBIA': 'BC',
    ' AB ': 'AB',
    ' A.B. ': 'AB',
    ' AB, ': 'AB',
    ' AB,': 'AB',
    ' AB. ': 'AB',
    ',AB ': 'AB',
    ',AB,': 'AB',
    ' ALTA ': 'AB',
    ' ALTA. ': 'AB',
    ' ALB ': 'AB',
    'ALBERT ': 'AB',
    'ALERTA ': 'AB',
    'ALBERTA ': 'AB',
    'ALBERTA,': 'AB',
    'ABLERTA ': 'AB',
    'ABERTA': 'AB',
    'ALBRTA': 'AB',
    'ALBETRA': 'AB',
    ', MAN. ': 'MB',
    ' MAN. ': 'MB',
    ' MAN ': 'MB',
    ' MB ': 'MB',
    ' MB, ': 'MB',
    ' MB,': 'MB',
    ' MB. ': 'MB',
    ',MB ': 'MB',
    ',MB,': 'MB',
    ',MB': 'MB',
    'MANITOBA': 'MB',
    'MANAITOBA': 'MB',
    'MANITOBE': 'MB',
    ' NB ': 'NB',
    ', NB': 'NB',
    'NEW BRUNSWICK': 'NB',
    ' NFLD ': 'NL',
    ' NL ': 'NL',
    ' N.L. ': 'NL',
    ', NL': 'NL',
    'NEWFOUNDLAND': 'NL',
    ' NS ': 'NS',
    ', NS': 'NS',
    'NOVA SCOTIA': 'NS',
    ' NWT ': 'NT',
    ' N.W.T. ': 'NT',
    ' N.T. ': 'NT',
    ' NT ': 'NT',
    ', NT': 'NT',
    'NORTH WEST TERRITORIES': 'NT',
    'NORTHWEST TERRITORIES': 'NT',
    ' NUNUVIT ': 'NU',
    ' NU ': 'NU',
    ', NU': 'NU',
    ' PEI ': 'PE',
    ' P.E.I. ': 'PE',
    ' PE ': 'PE',
    ', PE': 'PE',
    'PRINCE EDWARD ISLAND': 'PE',
    ' QC ': 'QC',
    ' QC': 'QC',
    ', QC': 'QC',
    ' QUEBEC ': 'QC',
    ' QUEBEC, ': 'QC',
    ' QUE ': 'QC',
    ' QU ': 'QC',
    ' YK ': 'YT',
    ' YT ': 'YT',
    ', YT': 'YT',
    ' YUKON TERRITORIES ': 'YT',
    ' YUKON TERRITORY ': 'YT',
    ' YUKON ': 'YT',
    ' SK ': 'SK',
    ' SK. ': 'SK',
    ', SK': 'SK',
    ', SA ': 'SK',
    ' SASKATCHEWAN ': 'SK',
    ' ASKATCHEWAN ': 'SK',
    ' SASK. ': 'SK',
    ' ONTARIO,': 'ON',
    ' ONTARIO ': 'ON',
    ' ONTARION ': 'ON',
    'ONTARO': 'ON',
    ' ONT ': 'ON',
    ' ONT. ': 'ON',
    ' ON ': 'ON',
    ' ON. ': 'ON',
    ', ON ': 'ON',
    ',ON ': 'ON'
}
DB2_STATE_MAPPING = {
    ' ALASKA ': 'AK',
    ' AK ': 'AK',
    ' AR ': 'AR',
    ' ARIZONA ': 'AR',
    ' AZ ': 'AZ',
    ' CALFORNIA ': 'CA',
    ' CALIFORNIA ': 'CA',
    ' CALIFORNIA,': 'CA',
    ' CA ': 'CA',
    ' CA, ': 'CA',
    ' CA. ': 'CA',
    'CALFORNIA': 'CA',
    ' CALIF. ': 'CA',
    ' COLORADO ': 'CO',
    ' CO ': 'CO',
    ' CO, ': 'CO',
    'CONNECTICUT': 'CT',
    ' CT ': 'CT',
    ' FLORIDA ': 'FL',
    ' FL ': 'FL',
    ' FL. ': 'FL',
    ' GA ': 'GA',
    ' GEORGIA ': 'GA',
    ' HAWAII ': 'HI',
    ' HI ': 'HI',
    ' ID ': 'ID',
    ' IDAHO ': 'ID',
    'IDAHO ': 'ID',
    'IDAHO,': 'ID',
    'ILLINOIS': 'IL',
    ' IL ': 'IL',
    ' INDIANA ': 'IN',
    ' IN ': 'IN',
    ' KANSAS ': 'KS',
    ' KS ': 'KS',
    ' KY ': 'KY',
    ' KENTUCKY ': 'KY',
    ' LA ': 'LA',
    ' LOUISIANA ': 'LA',
    ' MONTANA ': 'MT',
    ' MT ': 'MT',
    'MASSACHUSETTS': 'MA',
    ' MA ': 'MA',
    ' MARYLAND ': 'MD',
    ' MD ': 'MD',
    'MICHIGAN': 'MI',
    ' MI ': 'MI',
    'MINNESOTA': 'MN',
    ' MN ': 'MN',
    ' MISSOURI ': 'MO',
    ' MO ': 'MO',
    ' NEBRASKA ': 'NE',
    ' NE ': 'NE',
    ' NEVADA ': 'NV',
    ' NEVADA, ': 'NV',
    ' NV ': 'NV',
    ' NV. ': 'NV',
    ' NORTH CAROLINA ': 'NC',
    ' NC ': 'NC',
    ' NORTH DAKOTA ': 'ND',
    ' ND ': 'ND',
    ' NEW YORK ': 'NY',
    ' NY ': 'NY',
    ' OH ': 'OH',
    ' OK ': 'OK',
    ' OHIO,': 'OH',
    ' OHIO ': 'OH',
    ' OR. ': 'OR',
    ' OR, ': 'OR',
    ' OR ': 'OR',
    ',OR ': 'OR',
    ' ORGEON ': 'OR',
    ', OREGON ': 'OR',
    ' OREGON, ': 'OR',
    ' OREGAN ': 'OR',
    ', PA, ': 'PA',
    ' PENNSYLVANIA ': 'PA',
    ', PA, ': 'PA',
    ' SOUTH CAROLINA ': 'SC',
    ' SC ': 'SC',
    ' TENNESSEE ': 'TN',
    ' TENN. ': 'TN',
    ' TN ': 'TN',
    ' TEXAS ': 'TX',
    ' TX ': 'TX',
    ' UT ': 'UT',
    ' UTAH ': 'UT',
    ' VIRGINIA ': 'VA',
    ' VA ': 'VA',
    ' VERMONT ': 'VT',
    ' VT ': 'VT',
    ', WA ': 'WA',
    ', WA. ': 'WA',
    ' WA, ': 'WA',
    ' WA ': 'WA',
    ' WASHINTON ': 'WA',
    ', WASHINGTON ': 'WA',
    ' WAHINGTON ': 'WA',
    ' WASHINGTON ': 'WA',
    ' WI ': 'WI',
    ' WISCONSIN ': 'WI'
}
DB2_COUNTRY_MAPPING = {
    'U.S.A.': 'US',
    'U.SA.': 'US',
    ' USA ': 'US',
    'USA ': 'US',
    ' CA ': 'CA',
    'CANADA': 'CA',
    'BERMUDA': 'BM',
    'BOTSWANA, AFRICA': 'BW',
    'BOTSWANA': 'BW',
    'ARMENIA': 'AM',
    'AUSTRALIA': 'AU',
    'AUSTRIA': 'AT',
    'FRANCE UN': 'FR',
    'FRANCE': 'FR',
    '-GERMANY': 'DE',
    'WEST GERMANY': 'DE',
    'WEST GERMANU': 'DE',
    'GERMANY': 'DE',
    'HONG KONG ': 'HK',
    'HONGKONG': 'HK',
    ' HK ': 'HK',
    'INDONESIA': 'ID',
    '(ITALY) ITALIA': 'IT',
    'JAPAN': 'JP',
    'LATVIA': 'LV',
    'MALTA': 'MT',
    'MEXICO': 'MX',
    'MALAYSIA': 'MY',
    'MONGOLIA': 'MN',
    'HOLLAND': 'NL',
    'NETHERLANDS': 'NL',
    'NETHERLAND': 'NL',
    'NEW ZEALAND': 'NZ',
    'NORTHERN IRELAND': 'GB',
    'PAPUA, NEW GUINEA': 'PG',
    'PHILIPPINES': 'PH',
    'PORTUGAL': 'PT',
    'SCOTLAND': 'GB',
    'SPAIN': 'ES',
    'SWEDEN': 'SE',
    'SWITZERLAND': 'CH',
    'CHANNEL ISLANDS': 'GB',
    'ENGLAND, UK': 'GB',
    'ENGLABD': 'GB',
    'ENGLAND': 'GB',
    'UNITED KINGDOM': 'GB',
    'UNITED KINGDON': 'GB',
    ' U.K. ': 'GB',
    ' UK ': 'GB',
    'VIETNAM': 'VN'
}
COUNTRY_CA = 'CA'
COUNTRY_US = 'US'
PROVINCE_BC = 'BC'
PROVINCE_QC = 'QC'
PROVINCE_CODES = ' BC AB SK MB ON QC PE YT NU NT NS NL NB '
STATE_CODES = ' AK AR AZ CA CO CT FL GA HI ID IL IN KS KY LA MA MD MI MO MT MN ND NE NC NY NV OH OK OR PA SC TN TX ' + \
              ' UT VA VT WA WI '


def get_region_country(legacy_value: str, default_region: str = '', default_country: str = ''):
    """Get a province or state code and country code from DB2 legacy address text (not the street)."""
    region: str = default_region
    # current_app.logger.info(f'legacy_value ${legacy_value}$')
    for key, val in DB2_PROVINCE_MAPPING.items():
        if legacy_value.find(key) > -1:
            region = val
            break
    if region and PROVINCE_CODES.find(region) > 0:
        return region, COUNTRY_CA
    for key_state, val2 in DB2_STATE_MAPPING.items():
        if legacy_value.find(key_state) > -1:
            region = val2
            break
    if region and STATE_CODES.find(region) > 0:
        return region, COUNTRY_US
    # No region but country identified
    for key_country, val3 in DB2_COUNTRY_MAPPING.items():
        if legacy_value.find(key_country) > -1:
            return region, val3
    # Default region and country.
    return region, default_country


def get_region(legacy_value: str, default_region: str = ''):
    """Get a province or state code when country exists but no region extracted yet."""
    region: str = default_region
    # current_app.logger.info(f'legacy_value ${legacy_value}$')
    for key, val in DB2_PROVINCE_MAPPING.items():
        if legacy_value.find(key) > 0:
            return val
    for key_state, val2 in DB2_STATE_MAPPING.items():
        if legacy_value.find(key_state) > 0:
            return val2
    return region


def get_country_from_region(region: str, default: str = ''):
    """Get a country code from region code."""
    if region and PROVINCE_CODES.find(region) > 0:
        return COUNTRY_CA
    if region and STATE_CODES.find(region) > 0:
        return COUNTRY_US
    return default


def get_default_postal_code(legacy_value: str) -> str:
    """Try to get a Canadian postal code from a legacy value."""
    if not legacy_value or len(legacy_value) > 7:
        return ''
    test_val: str = legacy_value
    if len(test_val) == 7:
        test_val = test_val.replace(' ', '')
    if len(test_val) == 7:
        test_val = test_val.replace('-', '')
    # check pattern here.
    if len(test_val) == 6 and test_val[0].isalpha() and test_val[2].isalpha() and test_val[4].isalpha() and \
            test_val[1].isdigit() and test_val[3].isdigit() and test_val[5].isdigit():
        return legacy_value
    return ''


def get_country_from_postal_code(legacy_value: str):
    """Try to get the default country (Canada) from a Canadian postal code value."""
    # If no country or region postal code should always be last in the address text.
    if not legacy_value:
        return ''
    test_val: str = legacy_value.strip()
    if len(test_val) < 6 or len(test_val) > 7:
        return ''
    p_code: str = get_default_postal_code(test_val)
    if p_code:
        return COUNTRY_CA
    return ''


def get_region_country_from_postal_code(legacy_value: str):
    """Try to get the country (Canada) and default BC region from a Canadian postal code value."""
    # If no country or region postal code should always be last in the address text.
    if not legacy_value:
        return '', ''
    test_val: str = legacy_value.strip()
    p_code: str = ''
    if len(test_val) < 6:
        return '', ''
    if len(test_val) == 6:
        p_code = get_default_postal_code(test_val)
    else:
        test_val = test_val[(len(test_val) - 7):]
        if test_val[3:4] not in (' ', '-'):
            test_val = test_val[1:]
        p_code: str = get_default_postal_code(test_val)
    if p_code:
        return PROVINCE_BC, COUNTRY_CA
    return '', ''


def get_postal_code(legacy_value: str, country: str):
    """Try to get a postal code from a legacy value."""
    p_code = ''
    if legacy_value and country and country == COUNTRY_CA:  # and len(legacy_value) in (6, 7):
        if len(legacy_value) in (6, 7):
            p_code = legacy_value
        else:
            p_code = legacy_value[(len(legacy_value) - 7):]
            if p_code[3:4] not in (' ', '-'):
                p_code = p_code[1:]
        return get_default_postal_code(p_code)
    elif legacy_value and country and country == COUNTRY_US:
        if len(legacy_value) < 12:
            p_code = legacy_value
        else:
            p_code = legacy_value[(len(legacy_value) - 12):]
        test_val: str = ''
        pos: int = 0  # Look for first digit (may contain space characters).
        for character in p_code:
            if character.isdigit():
                test_val = p_code[pos:]
                break
            pos += 1
        if test_val:
            p_code = test_val
            # current_app.logger.info('Found test US zip=' + p_code)
            test_val = test_val.replace(' ', '')
            if test_val.isdigit():
                return p_code
    return ''


def remove_region_country(legacy_value: str, region: str, country: str, region_only: bool = False) -> str:
    """Remove region and country from the legacy text."""
    if legacy_value.strip() == '':
        return legacy_value
    value: str = legacy_value
    if country and country == COUNTRY_CA:
        for key in DB2_PROVINCE_MAPPING:
            if value.find(key) > -1:
                if key.find('QUEBEC') == -1 or region == PROVINCE_QC:
                    value = value.replace(key, '')
    elif country and country == COUNTRY_US:
        for key in DB2_STATE_MAPPING:
            if value.find(key) > -1:
                value = value.replace(key, '')
    if not region_only:
        for key_country in DB2_COUNTRY_MAPPING:
            if value.find(key_country) > -1:
                value = value.replace(key_country, '')
    value = value.strip()
    if value.endswith(','):
        value = value[0:(len(value) - 1)]
    if not region_only:
        if country and value == country:
            return ''
        for remove_country in DB2_REMOVE_TRAILING_COUNTRY:
            if value.endswith(remove_country):
                end_pos: int = len(value) - len(remove_country) + 1
                value = value[0:end_pos]
        for remove_country in DB2_REMOVE_STARTING_COUNTRY:
            if value.startswith(remove_country):
                start_pos: int = len(remove_country)
                value = value[start_pos:]
    return value.strip()


def format_postal_code(address: dict) -> str:
    """Format a Canadian address postal code."""
    postal_code = str(address.get('postalCode', ''))
    if not postal_code:
        return postal_code
    country = str(address.get('country', ''))
    if not country:
        country = get_country_from_region(address.get('region', ''))
    p_code: str = postal_code.strip().upper()
    if country and country == COUNTRY_CA:
        p_code = p_code.replace('-', ' ')
        if len(p_code) == 6:
            p_code = p_code[0:3] + ' ' + p_code[3:]
    return p_code


def to_db2_owner_address(address_json):
    """Convert address json to a DB2 legacy owner address."""
    db2_address = str(address_json['street']).upper().ljust(40, ' ')
    city = str(address_json['city']).upper().ljust(40, ' ')
    region: str = ''
    country: str = ''
    rest: str = ''
    if address_json.get('region'):
        region = str(address_json['region']).upper()
    if address_json.get('country'):
        country = str(address_json['country']).upper()
    if region and not country:
        country = get_country_from_region(region, '')
    if country:
        region += ' ' + country.upper()
    if address_json.get('streetAdditional'):
        street_2 = str(address_json['streetAdditional']).upper().ljust(40, ' ')
        db2_address += street_2[0:40]
    db2_address += city
    if region:
        db2_address += region.strip().ljust(40, ' ')
    if len(db2_address) < 81:
        rest = rest.rjust(80, ' ')
        db2_address += rest
    elif len(db2_address) < 121:
        rest = rest.rjust(40, ' ')
        db2_address += rest
    return db2_address[:160]


def to_db2_address(address_json):
    """Convert address json to a DB2 legacy address."""
    db2_address = str(address_json['street']).upper().ljust(40, ' ')
    city = str(address_json['city']).upper().ljust(40, ' ')
    rest = str(address_json['region']).upper() + ' ' + str(address_json['country']).upper()
    if address_json.get('streetAdditional'):
        street_2 = str(address_json['streetAdditional']).upper().ljust(40, ' ')
        db2_address += street_2 + city
    else:
        street_2 = ''.ljust(40, ' ')
        db2_address += street_2 + city
    if address_json.get('postalCode'):
        p_code = address_json.get('postalCode').upper()
        if address_json.get('country') and address_json.get('country') == COUNTRY_CA:
            if len(p_code) == 6:
                p_code = p_code[0:3] + ' ' + p_code[3:]
            rest += p_code.rjust(35, ' ')
            db2_address += rest
        else:
            start_pos: int = len(p_code) - 1
            rest += p_code.rjust(start_pos, ' ')
            db2_address += rest
    else:
        rest = rest.rjust(40, ' ')
        db2_address += rest
    return db2_address[:160]


def get_address_from_db2(legacy_address: str):
    """Get an address json from a DB2 legacy table address."""
    street = legacy_address[0:40].strip()
    legacy_text: str = legacy_address[40:]
    region, country = get_region_country(legacy_text + ' ')
    region: str = ''
    country: str = ''
    line2: str = legacy_text[0:40].strip()
    line3: str = legacy_text[40:80].strip()
    line4: str = legacy_text[80:].strip()
    if line4:
        region, country = get_region_country(' ' + line4 + ' ')
        if country:
            line4 = remove_region_country(' ' + line4 + ' ', region, country)
            if not region:
                region = get_region(' ' + line3 + ' ')
                line3 = remove_region_country(' ' + line3 + ' ', region, country, True)
        else:
            region, country = get_region_country(' ' + line3 + ' ')
            line3 = remove_region_country(' ' + line3 + ' ', region, country)
            if country and not region:
                region = get_region(' ' + line2 + ' ')
                line2 = remove_region_country(' ' + line2 + ' ', region, country, True)
    elif line3:
        region, country = get_region_country(' ' + line3 + ' ')
        if country:
            line3 = remove_region_country(' ' + line3 + ' ', region, country)
            if not region:
                region = get_region(' ' + line2 + ' ')
                line2 = remove_region_country(' ' + line2 + ' ', region, country, True)
        else:
            region, country = get_region_country(' ' + line2 + ' ')
            line2 = remove_region_country(' ' + line2 + ' ', region, country)
    elif line2:
        region, country = get_region_country(' ' + line2 + ' ')
        line2 = remove_region_country(' ' + line2 + ' ', region, country)
    street_add: str = ''
    city: str = ''
    p_code: str = ''
    if not country:
        region, country = get_region_country_from_postal_code(legacy_text)
    # 1. Postal code is always last after removing region and country.
    # 2. postal code can be in line4, lin3, or line2.
    # 3. A line can contain a city and a postal code.
    if line4:
        p_code = get_postal_code(line4, country)
        if p_code and len(line4) >= 10 and line4[0:3].isalpha():
            city = line4.replace(p_code, '').strip()
            street_add = line2
            if line3:
                street_add += ' ' + line3
        elif line3:
            street_add = line2
            city = line3
            if not p_code:
                street_add += ' ' + line3
                city = line4
        else:
            city = line2
            if not p_code:
                street_add = line2
                city = line4
    elif line3:
        p_code = get_postal_code(line3, country)
        if p_code and len(line3) >= 10 and line3[0:3].isalpha():
            city = line3.replace(p_code, '').strip()
            street_add = line2
        else:
            city = line2
        if not p_code:
            street_add = line2
            city = line3
    else:
        p_code = get_postal_code(line2, country)
        if p_code and len(line2) >= 10 and line2[0:3].isalpha():
            city = line2.replace(p_code, '').strip()
        else:
            city = line2
    # current_app.logger.info('city=' + city)
    # current_app.logger.info('add=' + street_add)
    if len(p_code) == 6 and country != COUNTRY_US:
        p_code = p_code[0:3] + ' ' + p_code[3:]
    address = {
        'city': city,
        'street': street,
        'region': region,
        'country': country,
        'postalCode': p_code
    }
    if street_add:
        address['streetAdditional'] = street_add.strip()
    return address


def get_address_from_db2_owner(legacy_address: str, postal_code: str):
    """Get an onwer address json from a DB2 legacy owner table address."""
    if not postal_code and not postal_code.strip():
        return get_address_from_db2(legacy_address)

    street = legacy_address[0:40].strip()
    p_code: str = postal_code.strip()
    legacy_text: str = legacy_address[40:]
    if legacy_text.find(' ' + p_code) > -1:
        legacy_text = legacy_text.replace((' ' + p_code), '')
    region: str = ''
    country: str = ''
    line2: str = legacy_text[0:40].strip()
    line3: str = legacy_text[40:80].strip()
    line4: str = legacy_text[80:].strip()
    if line4:
        region, country = get_region_country(' ' + line4 + ' ')
        line4 = remove_region_country(' ' + line4 + ' ', region, country)
        if country and not region:
            region = get_region(' ' + line3 + ' ')
            line3 = remove_region_country(' ' + line3 + ' ', region, country, True)
    elif line3:
        # current_app.logger.info(f'LINE 3={line3}')
        region, country = get_region_country(' ' + line3 + ' ')
        # current_app.logger.info(f'LINE 3 region={region}, country={country}')
        line3 = remove_region_country(' ' + line3 + ' ', region, country)
        if country and not region:
            region = get_region(' ' + line2 + ' ')
            line2 = remove_region_country(' ' + line2 + ' ', region, country, True)
    elif line2:
        region, country = get_region_country(' ' + line2 + ' ')
        line2 = remove_region_country(' ' + line2 + ' ', region, country)
    if not country:
        country = get_country_from_postal_code(p_code)
    # current_app.logger.info('2=' + line2)
    # current_app.logger.info('3=' + line3)
    # current_app.logger.info('4=' + line4)
    street_add: str = ''
    city: str = ''
    if line4:
        city = line4
        if line2:
            street_add += line2
        if line3:
            street_add += ' ' + line3

    elif line3:
        city = line3
        if line2:
            street_add += line2
    else:
        city = line2
    # current_app.logger.info('city=' + city)
    # current_app.logger.info('add=' + street_add)
    if len(p_code) == 6 and country != COUNTRY_US:
        p_code = p_code[0:3] + ' ' + p_code[3:]
    address = {
        'city': city,
        'street': street,
        'region': region,
        'country': country,
        'postalCode': p_code
    }
    if street_add:
        address['streetAdditional'] = street_add.strip()
    return address


def get_address_from_db2_manufact(legacy_address: str):
    """Get an address json from a DB2 legacy table address."""
    street = legacy_address[0:38].strip()
    legacy_text = legacy_address[39:].strip()
    pos = legacy_text.find(',')
    if pos == -1:
        pos = legacy_text.find(' ')
        if len(legacy_text[(pos + 1):]) > 12:
            next_pos = legacy_text[(pos + 1):].find(' ')
            pos += next_pos + 1
    city = legacy_text[0:pos]
    legacy_text = legacy_text[(pos + 1):].strip()
    legacy_text = legacy_text.replace('.', '')
    pos = legacy_text.find(' ')
    province = legacy_text[0:pos]
    postal_code = legacy_text[(pos + 1):].strip()
    address = {
        'city': city,
        'street': street,
        'region': province,
        'country': get_country_from_region(province),
        'postalCode': postal_code
    }
    return address
