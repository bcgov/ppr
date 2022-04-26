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

"""Tests to assure the legacy DB2 Docdes Model.

Test-Suite to ensure that the legacy DB2 Docdes Model is working as expected.
"""
import pytest

from mhr_api.models import Db2Docdes


# testdata pattern is ({exists}, {type}, {name}, {fee_code})
TEST_DATA = [
    (True, '101', 'REGISTER NEW UNIT', 'MHR400'),
    (True, '102', 'DECAL REPLACEMENT', 'MHR410'),
    (True, '103', 'TRANSPORT PERMIT', 'MHR415'),
    (False, 'XXX', None, None)
]


@pytest.mark.parametrize('exists,type, name, fee_code', TEST_DATA)
def test_find_by_id(session, exists, type, name, fee_code):
    """Assert that find doc description by type contains all expected elements."""
    docdes: Db2Docdes = Db2Docdes.find_by_id(type)
    if exists:
        assert docdes
        assert docdes.doc_type == type
        assert docdes.doc_name == name
        assert docdes.fee_code == fee_code
        json_data = docdes.json
        assert json_data['documentType'] == type
        assert json_data['documentName'] == name
        assert json_data['feeCode'] == fee_code
    else:
        assert not docdes


def test_docdes_json(session):
    """Assert that the doc description renders to a json format correctly."""
    docdes = Db2Docdes(
        doc_type='1234',
        doc_name='Doc Name',
        fee_code='abcde'
    )

    test_json = {
        'documentType': docdes.doc_type,
        'documentName': docdes.doc_name,
        'feeCode': docdes.fee_code
    }
    assert docdes.json == test_json
