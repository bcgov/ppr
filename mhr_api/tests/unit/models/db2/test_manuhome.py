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
from registry_schemas.example_data.mhr import REGISTRATION, LOCATION, TRANSFER, EXEMPTION, PERMIT

from mhr_api.exceptions import BusinessException
from mhr_api.models import Db2Document, Db2Manuhome, Db2Mhomnote, Db2Owngroup, MhrRegistration, Db2Location
from mhr_api.models import utils as model_utils
from mhr_api.models.db2.manuhome import LEGACY_STATUS_DESCRIPTION
from mhr_api.models.db2.registration_utils import adjust_group_interest
from mhr_api.models.type_tables import MhrPartyTypes, MhrTenancyTypes, MhrDocumentTypes
from mhr_api.services.authz import MANUFACTURER_GROUP, QUALIFIED_USER_GROUP, GOV_ACCOUNT_ROLE, STAFF_ROLE


COMMON_GROUP_1 = Db2Owngroup(interest='UNDIVIDED',
                             interest_numerator=1,
                             interest_denominator=4,
                             group_id=1,
                             tenancy_type='TC',
                             status='3')
COMMON_GROUP_2 = Db2Owngroup(interest='UNDIVIDED',
                             interest_numerator=2,
                             interest_denominator=8,
                             group_id=2,
                             tenancy_type='TC',
                             status='3')
COMMON_GROUP_3 = Db2Owngroup(interest='UNDIVIDED',
                             interest_numerator=2,
                             interest_denominator=4,
                             group_id=3,
                             tenancy_type='TC',
                             status='3')
NOTE_REGISTRATION = {
  'clientReferenceId': 'EX-TP001234',
  'attentionReference': 'JOHN SMITH',
  'submittingParty': {
    'businessName': 'BOB PATERSON HOMES INC.',
    'address': {
      'street': '1200 S. MACKENZIE AVE.',
      'city': 'WILLIAMS LAKE',
      'region': 'BC',
      'country': 'CA',
      'postalCode': 'V2G 3Y1'
    },
    'phoneNumber': '6044620279'
  },
  'note': {
    'documentType': 'CAU',
    'documentId': '62133670',
    'effectiveDateTime': '2023-02-21T18:56:00+00:00',
    'remarks': 'NOTICE OF ACTION COMMENCED MARCH 1 2022 WITH CRANBROOK COURT REGISTRY COURT FILE NO. 3011.',
    'givingNoticeParty': {
      'personName': {
        'first': 'JOHNNY',
        'middle': 'B',
        'last': 'SMITH'
      },
      'address': {
        'street': '222 SUMMER STREET',
        'city': 'VICTORIA',
        'region': 'BC',
        'country': 'CA',
        'postalCode': 'V8W 2V8'
      },
      'phoneNumber': '2504930122'
    }
  }
}
ADMIN_REGISTRATION = {
  'clientReferenceId': 'EX-TP001234',
  'attentionReference': 'JOHN SMITH',
  'documentType': 'NRED',
  'documentId': '62133670',
  'submittingParty': {
    'businessName': 'BOB PATERSON HOMES INC.',
    'address': {
      'street': '1200 S. MACKENZIE AVE.',
      'city': 'WILLIAMS LAKE',
      'region': 'BC',
      'country': 'CA',
      'postalCode': 'V2G 3Y1'
    },
    'phoneNumber': '6044620279'
  },
  'note': {
    'documentType': 'NRED',
    'documentId': '62133670',
    'remarks': 'REMARKS',
    'givingNoticeParty': {
      'personName': {
        'first': 'JOHNNY',
        'middle': 'B',
        'last': 'SMITH'
      },
      'address': {
        'street': '222 SUMMER STREET',
        'city': 'VICTORIA',
        'region': 'BC',
        'country': 'CA',
        'postalCode': 'V8W 2V8'
      },
      'phoneNumber': '2504930122'
    }
  }
}
# testdata pattern is ({exists}, {id}, {mhr_num}, {status}, {doc_id})
TEST_DATA = [
    (True, 1, '022911', 'E', 'REG22911'),
    (True, 10444, '001453', 'C', 'REG01453'),
    (False, 0, None, None, None)
]
# testdata pattern is ({http_status}, {id}, {mhr_num}, {status}, {doc_id}, {own_land})
TEST_MHR_NUM_DATA = [
    (HTTPStatus.OK, 1, '022911', 'E', 'REG22911', False),
    (HTTPStatus.OK, 10444, '001453', 'C', 'REG01453', False),
    (HTTPStatus.NOT_FOUND, 0, None, None, None, False)
]
# testdata pattern is ({mhr_num}, {group_id}, {doc_id_prefix}, {account_id})
TEST_DATA_TRANSFER = [
    ('150062', GOV_ACCOUNT_ROLE, '9', '2523'),
    ('150062', MANUFACTURER_GROUP, '8', '2523'),
    ('150062', QUALIFIED_USER_GROUP, '1', '2523')
]
# testdata pattern is ({mhr_num}, {group_id}, {doc_id_prefix}, {account_id})
TEST_DATA_EXEMPTION = [
    ('150062', GOV_ACCOUNT_ROLE, '9', '2523'),
    ('150062', MANUFACTURER_GROUP, '8', '2523'),
    ('150062', QUALIFIED_USER_GROUP, '1', '2523')
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
# testdata pattern is ({interest}, {numerator}, {denominator}, {new_interest})
TEST_DATA_GROUP_INTEREST = [
    ('', 1, 2, '1/2'),
    ('UNDIVIDED', 1, 2, 'UNDIVIDED 1/2'),
    ('UNDIVIDED', 9999, 10000, 'UNDIVIDED 9999/10000'),
    ('UNDIVIDED', 10000, 20000, '10000/20000'),
    ('Undivided', 1, 2, 'UNDIVIDED 1/2'),
    ('Junk', 1, 2, '1/2')
]
# testdata pattern is ({group1}, {group2}, {group3}, {interest1}, {interest2}, {interest3})
TEST_DATA_GROUP_INTEREST2 = [
    (COMMON_GROUP_1, COMMON_GROUP_2, COMMON_GROUP_3, 'UNDIVIDED 1/4', 'UNDIVIDED 2/8', 'UNDIVIDED 2/4')
]
# testdata pattern is ({tenancy_type}, {group_id}, {mhr_num}, {party_type})
TEST_DATA_GROUP_TYPE = [
    (MhrTenancyTypes.SOLE, 3, '017270', MhrPartyTypes.OWNER_IND),
    (MhrTenancyTypes.JOINT, 3, '016148', MhrPartyTypes.OWNER_BUS),
    (MhrTenancyTypes.COMMON, 2, '080282', MhrPartyTypes.OWNER_BUS),
    (MhrTenancyTypes.NA, 8, '004764', MhrPartyTypes.EXECUTOR),
    (MhrTenancyTypes.NA, 6, '051414', MhrPartyTypes.ADMINISTRATOR),
    (MhrTenancyTypes.NA, 4, '098504', MhrPartyTypes.TRUSTEE)
]
# testdata pattern is ({mhr_num}, {group_id}, {doc_id_prefix}, {account_id}, {doc_type}, {can_doc_id})
TEST_DATA_NOTE = [
    ('003936', STAFF_ROLE, '6', 'ppr_staff', 'CAU', None),
    ('045718', STAFF_ROLE, '9', 'ppr_staff', 'NCAN', '43641595')
]
# testdata pattern is ({mhr_num}, {staff}, {current}, {has_notes}, {ncan_doc_id})
TEST_MHR_NUM_DATA_NOTE = [
    ('080282', True, True, True, None),
    ('092238', True, True, True, '63116143'),
    ('022873', True, True, True, '43599221'),
    ('003936', True, True, False, None),
    ('003936', True, False, False, None),
    ('003936', False, True, False, None)
]
# testdata pattern is ({mhr_num}, {group_id}, {doc_id_prefix}, {account_id}, {doc_type}, {can_doc_id})
TEST_DATA_ADMIN = [
    ('022873', STAFF_ROLE, '6', 'ppr_staff', 'NRED', 50435493),
    ('045718', STAFF_ROLE, '6', 'ppr_staff', 'NCAN', '43641595')
]


@pytest.mark.parametrize('tenancy_type,group_id,mhr_num,party_type', TEST_DATA_GROUP_TYPE)
def test_group_type(session, tenancy_type, group_id, mhr_num, party_type):
    """Assert that find manufauctured home by mhr_number contains all expected elements."""
    if model_utils.is_legacy():
        manuhome: Db2Manuhome = Db2Manuhome.find_by_mhr_number(mhr_num)
        assert manuhome
        json_data = manuhome.registration_json
        for group in json_data.get('ownerGroups'):
            if group.get('groupId') == group_id:
                assert group['type'] == tenancy_type
                if party_type and group.get('owners'):
                    for owner in group.get('owners'):
                        assert owner.get('partyType') == party_type


@pytest.mark.parametrize('exists,id,mhr_num,status,doc_id', TEST_DATA)
def test_find_by_id(session, exists, id, mhr_num, status, doc_id):
    """Assert that find manufauctured home by id contains all expected elements."""
    if model_utils.is_legacy():
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
            assert report_json['status'] == LEGACY_STATUS_DESCRIPTION.get(status)
            assert report_json.get('createDateTime')
            assert report_json.get('clientReferenceId') is not None
            assert report_json.get('declaredValue') >= 0
            assert report_json.get('ownerGroups')
            assert report_json.get('location')
            assert report_json.get('description')
            assert report_json.get('notes')
        else:
            assert not manuhome


@pytest.mark.parametrize('http_status,id,mhr_num,status,doc_id,own_land', TEST_MHR_NUM_DATA)
def test_find_by_mhr_number(session, http_status, id, mhr_num, status, doc_id, own_land):
    """Assert that find a manufactured home by mhr_number contains all expected elements."""
    if model_utils.is_legacy():
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
            assert report_json['status'] == LEGACY_STATUS_DESCRIPTION.get(status)
            assert report_json.get('createDateTime')
            assert report_json.get('clientReferenceId') is not None
            assert report_json.get('declaredValue') >= 0
            assert report_json.get('ownerGroups')
            assert report_json.get('location')
            assert report_json.get('description')
            assert report_json.get('notes')
            assert report_json['ownLand'] == own_land
            for note in report_json.get('notes'):
                assert note.get('documentRegistrationNumber')
        else:
            with pytest.raises(BusinessException) as request_err:
                Db2Manuhome.find_by_mhr_number(mhr_num)
            # check
            assert request_err
            assert request_err.value.status_code == http_status


@pytest.mark.parametrize('mhr_num,staff,current,has_notes,ncan_doc_id', TEST_MHR_NUM_DATA_NOTE)
def test_find_by_mhr_number_note(session, mhr_num, staff, current, has_notes, ncan_doc_id):
    """Assert that find a manufactured home by mhr_number conditionally includes notes."""
    if model_utils.is_legacy():
        manuhome: Db2Manuhome = Db2Manuhome.find_by_mhr_number(mhr_num)
        assert manuhome
        manuhome.current_view = current
        manuhome.staff = staff
        reg_json = manuhome.new_registration_json
        if has_notes:
            assert reg_json.get('notes')
            has_ncan: bool = False
            for note in reg_json.get('notes'):
                assert note.get('documentRegistrationNumber')
                assert note.get('documentId')
                if ncan_doc_id and note.get('documentId') == ncan_doc_id:
                    has_ncan = True
                    assert note.get('cancelledDocumentType')
                    assert note.get('cancelledDocumentRegistrationNumber')
                assert note.get('createDateTime')
                assert note.get('status')
                assert 'remarks' in note
                assert note.get('givingNoticeParty')
            if ncan_doc_id:
                assert has_ncan
        elif staff and current:
            assert 'notes' in reg_json
            assert not reg_json.get('notes')
        else:
            assert not reg_json.get('notes')
        # search version
        reg_json = manuhome.registration_json
        if has_notes:
            assert reg_json.get('notes')
            has_ncan: bool = False
            for note in reg_json.get('notes'):
                assert note.get('documentRegistrationNumber')
                assert note.get('documentId')
                if ncan_doc_id and note.get('documentId') == ncan_doc_id:
                    has_ncan = True
                    assert note.get('cancelledDocumentType')
                    assert note.get('cancelledDocumentRegistrationNumber')
                assert note.get('createDateTime')
                assert note.get('status')
                assert 'remarks' in note
                assert note.get('givingNoticeParty')
            if ncan_doc_id:
                assert has_ncan
        else:
            assert 'notes' not in reg_json


@pytest.mark.parametrize('http_status,id,mhr_num,status,doc_id,own_land', TEST_MHR_NUM_DATA)
def test_find_original_by_mhr_number(session, http_status, id, mhr_num, status, doc_id, own_land):
    """Assert that find the original manufauctured home information by mhr_number contains all expected elements."""
    if model_utils.is_legacy():
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
            assert report_json['status'] == LEGACY_STATUS_DESCRIPTION.get(status)
            assert report_json.get('createDateTime')
            assert report_json.get('clientReferenceId') is not None
            assert report_json.get('declaredValue') >= 0
            assert report_json.get('ownerGroups')
            assert report_json.get('location')
            assert report_json.get('description')
            assert report_json['ownLand'] == own_land
        else:
            with pytest.raises(BusinessException) as request_err:
                Db2Manuhome.find_by_mhr_number(mhr_num)
            # check
            assert request_err
            assert request_err.value.status_code == http_status


@pytest.mark.parametrize('http_status,doc_id,mhr_num,doc_type', TEST_DATA_DOC_ID)
def test_find_by_document_id(session, http_status, doc_id, mhr_num, doc_type):
    """Assert that find manufauctured home information by document id contains all expected elements."""
    if model_utils.is_legacy():
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


@pytest.mark.parametrize('interest,numerator,denominator,new_interest', TEST_DATA_GROUP_INTEREST)
def test_adjust_group_interest_new(session, interest, numerator, denominator, new_interest):
    """Assert that adjusting group interest is working as expected."""
    if model_utils.is_legacy():
        groups = []
        group: Db2Owngroup = Db2Owngroup(status=Db2Owngroup.StatusTypes.ACTIVE,
                                        tenancy_type=Db2Owngroup.TenancyTypes.COMMON,
                                        interest=interest,
                                        interest_numerator=numerator,
                                        interest_denominator=denominator)
        groups.append(group)
        adjust_group_interest(groups, True)
        assert groups[0].interest == new_interest


@pytest.mark.parametrize('group1,group2,group3,interest1,interest2,interest3', TEST_DATA_GROUP_INTEREST2)
def test_adjust_group_interest_2(session, group1, group2, group3, interest1, interest2, interest3):
    """Assert that adjusting group interest is working as expected."""
    if model_utils.is_legacy():
        groups = []
        if group1:
            groups.append(group1)
        if group2:
            groups.append(group2)
        if group3:
            groups.append(group3)
        adjust_group_interest(groups, True)
        for group in groups:
            if group.group_id == 1:
                assert group.interest == interest1
            elif group.group_id == 2:
                assert group.interest == interest2
            elif group.group_id == 3:
                assert group.interest == interest3


def test_notes_sort_order(session):
    """Assert that manufactured home notes sort order is as expected."""
    if model_utils.is_legacy():
        manuhome: Db2Manuhome = Db2Manuhome.find_by_mhr_number('053341')
        report_json = manuhome.registration_json
        assert len(report_json['notes']) == 2
        assert report_json['notes'][0]['documentId'] == '90001986'
        assert report_json['notes'][1]['documentId'] == '43405528'


def test_declared_value(session):
    """Assert that manufauctured home declared value is as expected."""
    if model_utils.is_legacy():
        manuhome: Db2Manuhome = Db2Manuhome.find_by_mhr_number('077344')
        report_json = manuhome.registration_json
        assert report_json['declaredValue'] == 28200
        assert str(report_json['declaredDateTime']).startswith('2010-11-09')


def test_create_new_from_json(session):
    """Assert that the new MHR registration is created from registration json correctly."""
    if model_utils.is_legacy():
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
        assert manuhome.update_id == current_app.config.get('DB2_RACF_ID')
        assert manuhome.reg_documents
        assert len(manuhome.reg_documents) == 1
        doc: Db2Document = manuhome.reg_documents[0]
        assert doc.update_id == manuhome.update_id
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
    if model_utils.is_legacy():
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
        assert doc.update_id == current_app.config.get('DB2_RACF_ID')
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


@pytest.mark.parametrize('mhr_num,user_group,doc_id_prefix,account_id', TEST_DATA_EXEMPTION)
def test_create_exemption_from_json(session, mhr_num, user_group, doc_id_prefix, account_id):
    """Assert that an MHR tranfer is created from MHR exemption json correctly."""
    if model_utils.is_legacy():
        json_data = copy.deepcopy(EXEMPTION)
        del json_data['documentId']
        del json_data['documentRegistrationNumber']
        del json_data['documentDescription']
        del json_data['createDateTime']
        del json_data['payment']
        json_data['mhrNumber'] = mhr_num
        json_data['nonResidential'] = False
        json_data['note']['remarks'] = 'remarks'
        json_data['note']['expiryDateTime'] = '2022-10-07T18:43:45+00:00'
        base_reg: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
        assert base_reg
        assert base_reg.manuhome
        assert base_reg.manuhome.reg_documents
        # current_app.logger.info(json_data)
        registration: MhrRegistration = MhrRegistration.create_exemption_from_json(base_reg,
                                                                                json_data,
                                                                                'PS12345',
                                                                                'userid',
                                                                                user_group)
        assert registration.doc_id
        assert json_data.get('documentId')
        assert str(json_data.get('documentId')).startswith(doc_id_prefix)
        manuhome: Db2Manuhome = Db2Manuhome.create_from_exemption(registration, json_data)
        assert manuhome.mh_status == Db2Manuhome.StatusTypes.EXEMPT
        assert len(manuhome.reg_documents) > 1
        index: int = len(manuhome.reg_documents) - 1
        doc: Db2Document = manuhome.reg_documents[index]
        assert doc.id == registration.doc_id
        assert doc.document_type == Db2Document.DocumentTypes.RES_EXEMPTION
        assert doc.document_reg_id == registration.doc_reg_number
        assert doc.attention_reference
        assert doc.client_reference_id
        assert doc.registration_ts
        assert manuhome.reg_notes
        note: Db2Mhomnote = manuhome.reg_notes[0]
        assert note.document_type == doc.document_type
        assert note.reg_document_id == doc.id
        assert note.destroyed == 'N'
        assert note.remarks == 'remarks'
        assert note.expiry_date
        assert note.expiry_date.year == 2022
        assert note.expiry_date.month == 10


@pytest.mark.parametrize('mhr_num,user_group,doc_id_prefix,account_id', TEST_DATA_EXEMPTION)
def test_create_permit_from_json(session, mhr_num, user_group, doc_id_prefix, account_id):
    """Assert that an MHR tranfer is created from MHR exemption json correctly."""
    if model_utils.is_legacy():
        json_data = copy.deepcopy(PERMIT)
        del json_data['documentId']
        del json_data['documentRegistrationNumber']
        del json_data['documentDescription']
        del json_data['createDateTime']
        del json_data['payment']
        del json_data['note']
        del json_data['registrationType']
        json_data['mhrNumber'] = mhr_num
        base_reg: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
        assert base_reg
        assert base_reg.manuhome
        assert base_reg.manuhome.reg_documents
        # current_app.logger.info(json_data)
        registration: MhrRegistration = MhrRegistration.create_permit_from_json(base_reg,
                                                                                json_data,
                                                                                'PS12345',
                                                                                'userid',
                                                                                user_group)
        assert registration.doc_id
        assert json_data.get('documentId')
        assert str(json_data.get('documentId')).startswith(doc_id_prefix)
        manuhome: Db2Manuhome = Db2Manuhome.create_from_permit(registration, json_data)
        assert len(manuhome.reg_documents) > 1
        index: int = len(manuhome.reg_documents) - 1
        doc: Db2Document = manuhome.reg_documents[index]
        assert doc.id == registration.doc_id
        assert doc.document_type == Db2Document.DocumentTypes.PERMIT
        assert doc.document_reg_id == registration.doc_reg_number
        assert doc.client_reference_id
        assert doc.registration_ts
        assert manuhome.reg_notes
        note: Db2Mhomnote = manuhome.reg_notes[0]
        assert note.document_type == doc.document_type
        assert note.reg_document_id == doc.id
        assert note.destroyed == 'N'
        # assert note.remarks
        assert note.expiry_date
        assert manuhome.reg_location
        assert manuhome.reg_location.status == Db2Location.StatusTypes.HISTORICAL
        assert manuhome.reg_location.can_document_id == doc.id
        assert manuhome.new_location
        assert manuhome.new_location.status == Db2Location.StatusTypes.ACTIVE
        assert manuhome.new_location.reg_document_id == doc.id
        assert not manuhome.new_location.can_document_id
        assert manuhome.new_location.manuhome_id == manuhome.id


def test_save_new(session):
    """Assert that saving a new MHR registration is working correctly."""
    if model_utils.is_legacy():
        json_data = copy.deepcopy(REGISTRATION)
        json_data['location'] = copy.deepcopy(LOCATION)
        json_data['documentId'] = 'TT000001'
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


@pytest.mark.parametrize('mhr_num,user_group,doc_id_prefix,account_id,doc_type,can_doc_id', TEST_DATA_NOTE)
def test_create_note_from_json(session, mhr_num, user_group, doc_id_prefix, account_id, doc_type, can_doc_id):
    """Assert that an MHR unit note registration is created from json correctly."""
    if model_utils.is_legacy():
        json_data = copy.deepcopy(NOTE_REGISTRATION)
        json_data['note']['documentType'] = doc_type
        if doc_type == MhrDocumentTypes.NCAN:
            json_data['cancelDocumentId'] = can_doc_id
        base_reg: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
        assert base_reg
        existing_count = len(base_reg.manuhome.reg_notes)
        # current_app.logger.info(json_data)
        registration: MhrRegistration = MhrRegistration.create_note_from_json(base_reg,
                                                                            json_data,
                                                                            'ppr_staff',
                                                                            'userid',
                                                                            user_group)
        assert registration.id > 0
        assert registration.doc_id
        assert json_data.get('documentId')
        assert str(json_data.get('documentId')).startswith(doc_id_prefix)
        manuhome: Db2Manuhome = Db2Manuhome.create_from_note(registration, json_data)
        assert len(manuhome.reg_documents) > 1
        index: int = len(manuhome.reg_documents) - 1
        doc: Db2Document = manuhome.reg_documents[index]
        assert doc.id == registration.doc_id
        assert doc.document_type.strip() == doc_type
        assert doc.document_reg_id == registration.doc_reg_number
        assert doc.attention_reference
        assert doc.client_reference_id
        assert doc.registration_ts
        if doc_type != MhrDocumentTypes.NCAN:
            assert manuhome.reg_notes
            note: Db2Mhomnote = manuhome.reg_notes[0]
            assert note.document_type == doc.document_type
            assert note.reg_document_id == doc.id
            assert note.destroyed == 'N'
            assert note.remarks
            assert note.status
            assert note.expiry_date
            assert note.name
            assert note.phone_number
            assert note.legacy_address
        else:
            assert len(manuhome.reg_notes) == existing_count


@pytest.mark.parametrize('mhr_num,user_group,doc_id_prefix,account_id,doc_type,can_doc_id', TEST_DATA_ADMIN)
def test_create_admin_from_json(session, mhr_num, user_group, doc_id_prefix, account_id, doc_type, can_doc_id):
    """Assert that an MHR admin registration is created from json correctly."""
    if model_utils.is_legacy():
        json_data = copy.deepcopy(ADMIN_REGISTRATION)
        json_data['documentType'] = doc_type
        if doc_type in (MhrDocumentTypes.NRED, MhrDocumentTypes.NCAN):
            json_data['note']['documentType'] = doc_type
            json_data['updateDocumentId'] = can_doc_id
        else:
            del json_data['note']
        base_reg: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
        assert base_reg
        # current_app.logger.info(json_data)
        registration: MhrRegistration = MhrRegistration.create_admin_from_json(base_reg,
                                                                            json_data,
                                                                            account_id,
                                                                            'userid',
                                                                            user_group)
        assert registration.id > 0
        assert registration.doc_id
        assert json_data.get('documentId')
        assert str(json_data.get('documentId')).startswith(doc_id_prefix)
        manuhome: Db2Manuhome = Db2Manuhome.create_from_admin(registration, json_data)
        assert len(manuhome.reg_documents) > 1
        index: int = len(manuhome.reg_documents) - 1
        doc: Db2Document = manuhome.reg_documents[index]
        assert doc.id == registration.doc_id
        assert doc.document_type.strip() == doc_type
        assert doc.document_reg_id == registration.doc_reg_number
        assert doc.attention_reference
        assert doc.client_reference_id
        assert doc.registration_ts
