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

"""Tests to assure the legacy DB2 Manuhome Model.

Test-Suite to ensure that the legacy DB2 Manuhome Model is working as expected.
"""
from http import HTTPStatus

import pytest

from mhr_api.exceptions import BusinessException
from mhr_api.models import Db2Manuhome, utils as model_utils


# testdata pattern is ({exists}, {id}, {mhr_num}, {status}, {doc_id})
TEST_DATA = [
    (True, 1, '022911', 'E', 'REG22911'),
    (False, 0, None, None, None)
]
# testdata pattern is ({http_status}, {id}, {mhr_num}, {status}, {doc_id})
TEST_MHR_NUM_DATA = [
    (HTTPStatus.OK, 1, '022911', 'E', 'REG22911'),
    (HTTPStatus.NOT_FOUND, 0, None, None, None)
]


@pytest.mark.parametrize('exists,id,mhr_num,status,doc_id', TEST_DATA)
def test_find_by_id(session, exists, id, mhr_num, status, doc_id):
    """Assert that find manufauctured home by id contains all expected elements."""
    manuhome: Db2Manuhome = Db2Manuhome.find_by_id(id)
    if exists:
        assert manuhome
        assert manuhome.id == id
        assert manuhome.mhr_number == mhr_num
        assert manuhome.mh_status == status
        assert manuhome.reg_document_id == doc_id
        assert manuhome.exempt_flag is not None
        assert manuhome.presold_decal is not None
        assert manuhome.update_count is not None
        assert manuhome.update_id is not None
        assert manuhome.update_date is not None
        assert manuhome.update_time is not None
        assert manuhome.accession_number is not None
        assert manuhome.box_number is not None
        assert manuhome.reg_documents
        assert manuhome.reg_owners
        assert manuhome.reg_location
        assert manuhome.reg_descript
        assert manuhome.reg_notes
        report_json = manuhome.registration_json
        assert report_json['mhrNumber'] == mhr_num
        assert report_json['status'] == status
        assert report_json.get('createDateTime')
        assert report_json.get('clientReferenceId') is not None
        assert report_json.get('declaredValue') >= 0
        assert report_json.get('owners')
        assert report_json.get('location')
        assert report_json.get('description')
        assert report_json.get('notes')
    else:
        assert not manuhome


@pytest.mark.parametrize('http_status,id,mhr_num,status,doc_id', TEST_MHR_NUM_DATA)
def test_find_by_mhr_number(session, http_status, id, mhr_num, status, doc_id):
    """Assert that find manufauctured home by mhr_number contains all expected elements."""
    if http_status == HTTPStatus.OK:
        manuhome: Db2Manuhome = Db2Manuhome.find_by_mhr_number(mhr_num)
        assert manuhome
        assert manuhome.id == id
        assert manuhome.mhr_number == mhr_num
        assert manuhome.mh_status == status
        assert manuhome.reg_document_id == doc_id
        assert manuhome.exempt_flag is not None
        assert manuhome.presold_decal is not None
        assert manuhome.update_count is not None
        assert manuhome.update_id is not None
        assert manuhome.update_date is not None
        assert manuhome.update_time is not None
        assert manuhome.accession_number is not None
        assert manuhome.box_number is not None
        assert manuhome.reg_documents
        assert manuhome.reg_owners
        assert manuhome.reg_location
        assert manuhome.reg_descript
        assert manuhome.reg_notes
        report_json = manuhome.registration_json
        assert report_json['mhrNumber'] == mhr_num
        assert report_json['status'] == status
        assert report_json.get('createDateTime')
        assert report_json.get('clientReferenceId') is not None
        assert report_json.get('declaredValue') >= 0
        assert report_json.get('owners')
        assert report_json.get('location')
        assert report_json.get('description')
        assert report_json.get('notes')
    else:
        with pytest.raises(BusinessException) as request_err:
            Db2Manuhome.find_by_mhr_number(mhr_num)
        # check
        assert request_err
        assert request_err.value.status_code == http_status


def test_notes_sort_order(session):
    """Assert that manufauctured home notes sort order is as expected."""
    manuhome: Db2Manuhome = Db2Manuhome.find_by_mhr_number('053341')
    report_json = manuhome.registration_json
    assert len(report_json['notes']) == 2
    assert report_json['notes'][0]['documentId'] == '90001986'
    assert report_json['notes'][1]['documentId'] == '43405528'


def test_declared_value(session):
    """Assert that manufauctured home declared value is as expected."""
    manuhome: Db2Manuhome = Db2Manuhome.find_by_mhr_number('077344')
    report_json = manuhome.registration_json
    assert report_json['declaredValue'] == 28200
    assert str(report_json['declaredDateTime']).startswith('2010-11-09')


def test_manuhome_json(session):
    """Assert that the manufactured home info renders to a json format correctly."""
    manuhome = Db2Manuhome(mhr_number='022911',
                           mh_status='E',
                           reg_document_id='REG22911',
                           exempt_flag='R',
                           presold_decal=' ',
                           update_count=1,
                           update_id='PA96558',
                           accession_number='943972',
                           box_number='409')
    manuhome.update_date = model_utils.date_from_iso_format('1999-09-30')
    manuhome.update_time = model_utils.time_from_iso_format('11:01:47')

    test_json = {
        'mhrNumber': manuhome.mhr_number,
        'status': manuhome.mh_status,
        'registrationDocumentId': manuhome.reg_document_id,
        'exemptFlag': manuhome.exempt_flag,
        'presoldDecal': manuhome.presold_decal,
        'updateCount': manuhome.update_count,
        'updateId': manuhome.update_id,
        'accessionNumber': manuhome.accession_number,
        'boxNumber': manuhome.box_number,
        'updateDate': '1999-09-30',
        'updateTime': '11:01:47'
    }
    assert manuhome.json == test_json
