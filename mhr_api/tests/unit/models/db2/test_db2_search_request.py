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

"""Tests to assure the Search Model.

Test-Suite to ensure that the Search Model is working as expected.
"""
from http import HTTPStatus
import copy

from flask import current_app

import pytest

from mhr_api.models import SearchRequest, utils as model_utils
from mhr_api.models.db2 import search_utils as search_db2_utils
from mhr_api.exceptions import BusinessException


MHR_NUMBER_JSON = {
    'type': 'MHR_NUMBER',
    'criteria': {
        'value': '022911'
    },
    'clientReferenceId': 'T-SQ-MH-1'
}
MH_INVALID_JSON = {
    'type': 'MHR_NUMBER',
    'criteria': {
        'ownerName': {
            'first': 'JAMES',
            'last': 'BROWN'
        }
    }
}
# Test valid criteria with no results.
MH_NONE_JSON = {
    'type': 'MHR_NUMBER',
    'criteria': {
        'value': '999999'
    },
    'clientReferenceId': 'T-SQ-MH-4'
}
ORG_NAME_JSON = {
    'type': 'ORGANIZATION_NAME',
    'criteria': {
        'value': 'JANDEL HOMES LTD.'
    },
    'clientReferenceId': 'T-SQ-MO-1'
}
MO_INVALID_JSON = {
    'type': 'ORGANIZATION_NAME',
    'criteria': {
        'ownerName': {
            'first': 'JAMES',
            'last': 'BROWN'
        }
    }
}
# Test valid criteria with no results.
MO_NONE_JSON = {
    'type': 'ORGANIZATION_NAME',
    'criteria': {
        'value': 'XXXXXXXXXXXZZZZZ'
    },
    'clientReferenceId': 'T-SQ-MH-4'
}
OWNER_NAME_JSON = {
    'type': 'OWNER_NAME',
    'criteria': {
        'ownerName': {
            'first': 'David',
            'last': 'Hamm'
        }
    },
    'clientReferenceId': 'T-SQ-MI-1'
}
OWNER_NAME_JSON2 = {
    'type': 'OWNER_NAME',
    'criteria': {
        'ownerName': {
            'first': 'ROSE',
            'middle': 'CHERYL',
            'last': 'LESLIE'
        }
    },
    'clientReferenceId': 'T-SQ-MI-1'
}
MI_INVALID_JSON = {
    'type': 'OWNER_NAME',
    'criteria': {
        'value': 'GUTHRIE HOLDINGS LTD.'
    }
}
# Test valid criteria with no results.
MI_NONE_JSON = {
    'type': 'OWNER_NAME',
    'criteria': {
        'ownerName': {
            'first': 'ZZZZYYYYY',
            'last': 'XXXXXXXXOO'
        }
    },
    'clientReferenceId': 'T-SQ-MI-4'
}
SERIAL_NUMBER_JSON = {
    'type': 'SERIAL_NUMBER',
    'criteria': {
        'value': 'XF1048'
    },
    'clientReferenceId': 'T-SQ-MS-1'
}
MS_INVALID_JSON = {
    'type': 'SERIAL_NUMBER',
    'criteria': {
        'ownerName': {
            'first': 'JAMES',
            'last': 'BROWN'
        }
    }
}
# Test valid criteria with no results.
MS_NONE_JSON = {
    'type': 'SERIAL_NUMBER',
    'criteria': {
        'value': 'XXX999999999'
    },
    'clientReferenceId': 'T-SQ-MS-4'
}

# testdata pattern is ({search type}, {JSON data})
TEST_VALID_DATA = [
    ('MM', MHR_NUMBER_JSON),
    ('MO', ORG_NAME_JSON),
    ('MI', OWNER_NAME_JSON),
    ('MI', OWNER_NAME_JSON2),
    ('MS', SERIAL_NUMBER_JSON),
]

# testdata pattern is ({search type}, {JSON data})
TEST_NONE_DATA = [
    ('MM', MH_NONE_JSON),
    ('MO', MO_NONE_JSON),
    ('MI', MO_NONE_JSON),
    ('MS', MS_NONE_JSON)
]
# testdata pattern is ({search type}, {JSON data})
TEST_INVALID_DATA = [
    ('MM', MH_INVALID_JSON),
    ('MO', MO_INVALID_JSON),
    ('MI', MI_INVALID_JSON),
    ('MS', MS_INVALID_JSON)
]
# testdata pattern is ({serial_val}, {key_hex_val})
TEST_SERIAL_NUMBER_KEY_DATA = [
    ('0310282AB', '04BC0A'),
    ('NAL1467920204A', '0E0A8C'),
    ('NAL1467920204B', '0E0A8C'),
    ('NAL1467920204C', '0E0A8C'),
    ('NAL1467940419A', '0E5983'),
    ('NAL1467940419B', '0E5983'),
    ('NAL1448940419C', '0E5983'),
    ('0316371A', '04D3D3'),
    ('0316422A', '04D406'),
    ('0316422B', '04D406'),
    ('313', '000139'),
    ('S4006XXA6', '00EA66'),
    ('GH122BRUTCKFLSSTO', '00FA7A'),
    ('2570', '000A0A'),
    ('2564', '000A04'),
    ('4015', '000FAF'),
    ('D1502A', '0005DE'),
    ('75AGF06888A', '001AE8'),
    ('4898A', '001322'),
    ('0315780A', '04D184'),
    ('75BGH08171A', '063A6B'),
    ('SHL26409412480', '064B40'),
    ('*', '000000'),
    ('66', '000042'),
    ('WIN1466944772127', '0BC81F'),
    ('70143CKFRR74AF07', '0B4AA7'),
    ('ALFLLA746063', '0B624F'),
    ('75BGG08140A', '09478C'),
    ('REG1467943877', '0E6705'),
    ('REG1467943900', '0E671C'),
    ('NHH1467940031', '0E57FF'),
    ('ALFL1A3710635', '0AD7EB'),
    ('44G712683508', '0A6DF4'),
    ('681433BRCKFBRCL', '0A65D9'),
    ('B60C2ET15750R', '003D86'),
    ('FIEDFXMP60X12721', '0031B1'),
    ('GESCFYMP68X12665', '003179'),
    ('SHL14529211353', '033999'),
    ('GCSCFYMP54X1213660', '03429C'),
    ('MNHM9215141A', '034865'),
    ('727F6600', '0AC828'),
    ('178711979', '0ADD2B'),
    ('68M711099', '0AD9BB'),
    ('S0263', '00C457'),
    ('50273', '00C461'),
    ('6BDS0273', '00C461'),
    ('SATSK618S', '00C5BA')
]


def test_search_no_account(session):
    """Assert that a search query with no account id returns the expected result."""
    if model_utils.is_legacy():
        json_data = copy.deepcopy(MHR_NUMBER_JSON)
        query = SearchRequest.create_from_json(json_data, None)
        query.search()

        assert query.id
        assert query.search_response


@pytest.mark.parametrize('search_type,json_data', TEST_VALID_DATA)
def test_search_valid(session, search_type, json_data):
    """Assert that a valid search returns the expected search type result."""
    if model_utils.is_legacy():
        test_data = copy.deepcopy(json_data)
        test_data['type'] = model_utils.TO_DB_SEARCH_TYPE[json_data['type']]
        SearchRequest.validate_query(test_data)

        query: SearchRequest = SearchRequest.create_from_json(json_data, 'PS12345', 'UNIT_TEST')
        query.search_db2()
        assert not query.updated_selection
        result = query.json
        current_app.logger.debug('Results size:' + str(result['totalResultsSize']))
        assert query.id
        assert query.search_response
        assert query.account_id == 'PS12345'
        assert query.user_id == 'UNIT_TEST'
        assert result['searchId']
        assert result['searchQuery']
        assert result['searchDateTime']
        assert result['totalResultsSize']
        assert result['maxResultsSize']
        assert result['returnedResultsSize']
        if search_type != 'MS':
            assert len(result['results']) >= 1
        if result.get('results'):
            for match in result['results']:
                assert match['mhrNumber']
                assert match['status']
                assert match.get('activeCount') >= 0
                assert match.get('exemptCount') >= 0
                assert match.get('historicalCount') >= 0
                assert match['createDateTime']
                assert match['homeLocation']
                assert match['serialNumber']
                assert match['baseInformation']
                assert 'year' in match['baseInformation']
                assert 'make' in match['baseInformation']
                assert match['baseInformation']['model'] is not None
                assert 'organizationName' in match or 'ownerName' in match
                if match.get('ownerName'):
                    assert match['ownerName']['first']
                    assert match['ownerName']['last']


@pytest.mark.parametrize('search_type,json_data', TEST_NONE_DATA)
def test_search_no_results(session, search_type, json_data):
    """Assert that a search query with no results returns the expected result."""
    if model_utils.is_legacy():
        query: SearchRequest = SearchRequest.create_from_json(json_data, None)
        query.search_db2()

        assert query.id
        assert not query.search_response
        assert query.returned_results_size == 0


def test_create_from_json(session):
    """Assert that the search_client creates from a json format correctly."""
    if model_utils.is_legacy():
        json_data = copy.deepcopy(MHR_NUMBER_JSON)
        search_client = SearchRequest.create_from_json(json_data, 'PS12345', 'USERID')

        assert search_client.account_id == 'PS12345'
        assert search_client.search_type == 'MM'
        assert search_client.client_reference_id == 'T-SQ-MH-1'
        assert search_client.search_ts
        assert search_client.search_criteria
        assert search_client.user_id == 'USERID'


@pytest.mark.parametrize('search_type,json_data', TEST_INVALID_DATA)
def test_search_invalid_criteria_400(session, client, jwt, search_type, json_data):
    """Assert that validation of a search request with invalid criteria throws a BusinessException."""
    if model_utils.is_legacy():
        test_data = copy.deepcopy(json_data)
        test_data['type'] = model_utils.TO_DB_SEARCH_TYPE[json_data['type']]
        # test
        with pytest.raises(BusinessException) as bad_request_err:
            SearchRequest.validate_query(test_data)

        # check
        assert bad_request_err
        assert bad_request_err.value.status_code == HTTPStatus.BAD_REQUEST
        # print(bad_request_err.value.error)


@pytest.mark.parametrize('serial_val, key_hex_val', TEST_SERIAL_NUMBER_KEY_DATA)
def test_serial_key_hex(session, serial_val, key_hex_val):
    """Assert that search serial number hex key generation works as expected."""
    if model_utils.is_legacy():
        key: str = search_db2_utils.get_search_serial_number_key_hex(serial_val)
        assert key == key_hex_val
