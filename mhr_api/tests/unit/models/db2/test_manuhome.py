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
import copy
from http import HTTPStatus

from flask import current_app
import pytest
from registry_schemas.example_data.mhr import REGISTRATION, LOCATION, TRANSFER

from mhr_api.exceptions import BusinessException
from mhr_api.models import Db2Document, Db2Manuhome, Db2Owngroup, MhrRegistration
from mhr_api.services.authz import MANUFACTURER_GROUP, QUALIFIED_USER_GROUP, GOV_ACCOUNT_ROLE


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
# testdata pattern is ({mhr_num}, {group_id}, {doc_id_prefix}, {account_id})
TEST_DATA_TRANSFER = [
    ('150062', GOV_ACCOUNT_ROLE, '9', '2523'),
    ('150062', MANUFACTURER_GROUP, '8', '2523'),
    ('150062', QUALIFIED_USER_GROUP, '1', '2523')
]
# testdata pattern is ({http_status}, {document_id}, {mhr_num}, {doc_type})
TEST_DATA_DOC_ID = [
    (HTTPStatus.OK, '10104535', '102265', 'TRAN'),
    (HTTPStatus.NOT_FOUND, 'XXX04535', None, None)
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
        assert manuhome.reg_owner_groups
        assert manuhome.reg_location
        assert manuhome.reg_descript
        assert manuhome.reg_notes
        report_json = manuhome.registration_json
        assert report_json['mhrNumber'] == mhr_num
        assert report_json['status'] in ('E', 'EXEMPT')
        assert report_json.get('createDateTime')
        assert report_json.get('clientReferenceId') is not None
        assert report_json.get('declaredValue') >= 0
        assert report_json.get('ownerGroups')
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
        assert manuhome.reg_owner_groups
        assert manuhome.reg_location
        assert manuhome.reg_descript
        assert manuhome.reg_notes
        report_json = manuhome.registration_json
        assert report_json['mhrNumber'] == mhr_num
        assert report_json['status'] in ('E', 'EXEMPT')
        assert report_json.get('createDateTime')
        assert report_json.get('clientReferenceId') is not None
        assert report_json.get('declaredValue') >= 0
        assert report_json.get('ownerGroups')
        assert report_json.get('location')
        assert report_json.get('description')
        assert report_json.get('notes')
    else:
        with pytest.raises(BusinessException) as request_err:
            Db2Manuhome.find_by_mhr_number(mhr_num)
        # check
        assert request_err
        assert request_err.value.status_code == http_status


@pytest.mark.parametrize('http_status,id,mhr_num,status,doc_id', TEST_MHR_NUM_DATA)
def test_find_original_by_mhr_number(session, http_status, id, mhr_num, status, doc_id):
    """Assert that find the original manufauctured home information by mhr_number contains all expected elements."""
    if http_status == HTTPStatus.OK:
        manuhome: Db2Manuhome = Db2Manuhome.find_original_by_mhr_number(mhr_num)
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
        assert manuhome.reg_owner_groups
        assert manuhome.reg_location
        assert manuhome.reg_descript
        report_json = manuhome.new_registration_json
        # current_app.logger.info(report_json)
        assert report_json['mhrNumber'] == mhr_num
        assert report_json['status'] == 'EXEMPT'
        assert report_json.get('createDateTime')
        assert report_json.get('clientReferenceId') is not None
        assert report_json.get('declaredValue') >= 0
        assert report_json.get('ownerGroups')
        assert report_json.get('location')
        assert report_json.get('description')
    else:
        with pytest.raises(BusinessException) as request_err:
            Db2Manuhome.find_by_mhr_number(mhr_num)
        # check
        assert request_err
        assert request_err.value.status_code == http_status


@pytest.mark.parametrize('http_status,doc_id,mhr_num,doc_type', TEST_DATA_DOC_ID)
def test_find_by_document_id(session, http_status, doc_id, mhr_num, doc_type):
    """Assert that find manufauctured home information by document id contains all expected elements."""
    if http_status == HTTPStatus.OK:
        manuhome: Db2Manuhome = Db2Manuhome.find_by_document_id(doc_id)
        assert manuhome
        assert manuhome.id
        assert manuhome.mhr_number == mhr_num
        assert manuhome.reg_documents
        doc = manuhome.reg_documents[0]
        assert doc.id == doc_id
        assert doc.document_type == doc_type
        report_json = manuhome.json
        assert report_json['mhrNumber'] == mhr_num
        assert report_json.get('status')
        assert report_json.get('createDateTime')
        assert report_json.get('clientReferenceId') is not None
        assert report_json.get('documentId') == doc_id
        assert report_json.get('submittingParty')
        if doc_type in (Db2Document.DocumentTypes.TRAND, Db2Document.DocumentTypes.TRANS):
            assert manuhome.reg_owner_groups
            assert len(manuhome.reg_owner_groups) == 2
            assert len(report_json.get('deleteOwnerGroups')) + len(report_json.get('addOwnerGroups')) == 2
    else:
        with pytest.raises(BusinessException) as request_err:
            Db2Manuhome.find_by_document_id(doc_id)
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


def test_create_new_from_json(session):
    """Assert that the new MHR registration is created from registration json correctly."""
    json_data = copy.deepcopy(REGISTRATION)
    json_data['location'] = copy.deepcopy(LOCATION)
    json_data['documentId'] = 'UT000001'
    json_data['attentionReference'] = 'ATTN_REF'
    # current_app.logger.info(json_data)
    registration: MhrRegistration = MhrRegistration.create_new_from_json(json_data, 'PS12345')
    manuhome: Db2Manuhome = Db2Manuhome.create_from_registration(registration, json_data)
    mh_json = manuhome.new_registration_json
    current_app.logger.info(mh_json)
    assert manuhome.id == registration.id
    assert manuhome.mhr_number == registration.mhr_number
    assert manuhome.reg_document_id == json_data['documentId'] 
    assert manuhome.mh_status == Db2Manuhome.StatusTypes.REGISTERED
    assert manuhome.reg_documents
    assert len(manuhome.reg_documents) == 1
    assert manuhome.reg_location
    assert manuhome.reg_location.status == 'A'
    assert manuhome.reg_descript
    assert manuhome.reg_descript.status == 'A'
    assert manuhome.reg_owner_groups
    assert len(manuhome.reg_owner_groups) == 2
    for group in manuhome.reg_owner_groups:
        assert group.owners
        assert len(group.owners) == 1
        assert group.status == Db2Owngroup.StatusTypes.ACTIVE
        assert group.reg_document_id == json_data['documentId']


@pytest.mark.parametrize('mhr_num,user_group,doc_id_prefix,account_id', TEST_DATA_TRANSFER)
def test_create_transfer_from_json(session, mhr_num, user_group, doc_id_prefix, account_id):
    """Assert that an MHR tranfer is created from MHR transfer json correctly."""
    json_data = copy.deepcopy(TRANSFER)
    del json_data['documentId']
    del json_data['documentDescription']
    del json_data['createDateTime']
    del json_data['payment']
    json_data['mhrNumber'] = mhr_num
    json_data['consideration'] = '$120000.00'
    json_data['declaredValue'] = 120000
    json_data['ownLand'] = 'Y'
    json_data['transferDate'] = '2022-10-07T18:43:45+00:00'
    base_reg: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    assert base_reg
    assert base_reg.manuhome
    # current_app.logger.info(json_data)
    registration: MhrRegistration = MhrRegistration.create_transfer_from_json(base_reg,
                                                                              json_data,
                                                                              'PS12345',
                                                                              'userid',
                                                                              user_group)
    assert registration.doc_id
    assert json_data.get('documentId')
    assert str(json_data.get('documentId')).startswith(doc_id_prefix)
    manuhome: Db2Manuhome = Db2Manuhome.create_from_transfer(registration, json_data)
    assert len(manuhome.reg_documents) > 1
    index: int = len(manuhome.reg_documents) - 1
    doc: Db2Document = manuhome.reg_documents[index]
    assert doc.id == registration.doc_id
    assert doc.document_type == Db2Document.DocumentTypes.TRANS
    assert doc.document_reg_id == registration.doc_reg_number
    assert manuhome.reg_owner_groups
    assert len(manuhome.reg_owner_groups) > 2
    for group in manuhome.reg_owner_groups:
        if group.group_id == 1:
            assert group.status == Db2Owngroup.StatusTypes.PREVIOUS
            assert group.can_document_id == registration.doc_id
        elif group.group_id == 3:
            assert group.status == Db2Owngroup.StatusTypes.ACTIVE
            assert group.reg_document_id == registration.doc_id
    assert doc.consideration_value
    assert doc.own_land == 'Y'
    assert doc.declared_value == 120000
    assert doc.consideration_value == '$120000.00'
    assert doc.transfer_execution_date
    assert doc.transfer_execution_date.year == 2022
    assert doc.transfer_execution_date.month == 10


def test_save_new(session):
    """Assert that saving a new MHR registration is working correctly."""
    json_data = copy.deepcopy(REGISTRATION)
    json_data['location'] = copy.deepcopy(LOCATION)
    json_data['documentId'] = 'UT000001'
    json_data['attentionReference'] = 'ATTN_REF'
    registration: MhrRegistration = MhrRegistration.create_new_from_json(json_data, 'PS12345')
    manuhome: Db2Manuhome = Db2Manuhome.create_from_registration(registration, json_data)
    manuhome.save()
    mh_json = manuhome.new_registration_json
    current_app.logger.info(mh_json)
    reg_new = Db2Manuhome.find_by_mhr_number(registration.mhr_number)
    assert reg_new
    assert manuhome.reg_documents
    assert len(manuhome.reg_documents) == 1
    assert manuhome.mh_status == 'R'
    assert manuhome.reg_location
    assert manuhome.reg_location.status == 'A'
    assert manuhome.reg_descript
    assert manuhome.reg_descript.status == 'A'
    assert manuhome.reg_owner_groups
    assert len(manuhome.reg_owner_groups) == 2
    for group in manuhome.reg_owner_groups:
        assert group.status == '3'
