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

"""Tests to assure the MHR document Model.

Test-Suite to ensure that the MHR document Model is working as expected.
"""
import copy

import pytest
from registry_schemas.example_data.mhr import REGISTRATION

from mhr_api.models import MhrDocument, MhrRegistration
from mhr_api.models.type_tables import MhrDocumentTypes


# testdata pattern is ({id}, {has_results})
TEST_ID_DATA = [
    (200000000, True),
    (300000000, False)
]
TEST_DOC_ID_DATA = [
    ('77777000', True),
    ('ABCD0000', False)
]
TEST_DOC_REG_NUM_DATA = [
    ('90499999', True),
    ('ABCD0000', False)
]
TEST_DOCUMENT = MhrDocument(id=1,
    document_type=MhrDocumentTypes.REG_101,
    document_id='66666666',
    document_registration_number='00999999',
    attention_reference='attn',
    own_land='Y',
    declared_value=0,
    consideration_value='$0.00',
    consent='consent',
    owner_cross_reference='XXXXX')


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_id(session, id, has_results):
    """Assert that find document by primary key contains all expected elements."""
    document: MhrDocument = MhrDocument.find_by_id(id)
    if has_results:
        assert document
        assert document.id == 200000000
        assert document.registration_id == 200000000
        assert document.change_registration_id == 200000000
        assert document.document_id == '77777000'
        assert document.document_registration_number == '90499999'
        assert document.document_type == MhrDocumentTypes.REG_101
        assert document.attention_reference == 'attn'
        assert document.declared_value == 90000
        assert document.consideration_value == '$90000.00'
        assert document.own_land == 'Y'
        assert document.transfer_date
        assert not document.consent
        assert not document.owner_cross_reference
    else:
        assert not document


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_registration_id(session, id, has_results):
    """Assert that find document by registration id contains all expected elements."""
    documents = MhrDocument.find_by_registration_id(id)
    if has_results:
        assert documents
        document = documents[0]
        assert document.id == 200000000
        assert document.registration_id == 200000000
        assert document.change_registration_id == 200000000
        assert document.document_id == '77777000'
        assert document.document_registration_number == '90499999'
        assert document.document_type == MhrDocumentTypes.REG_101
        assert document.attention_reference == 'attn'
        assert document.declared_value == 90000
        assert document.consideration_value == '$90000.00'
        assert document.own_land == 'Y'
        assert document.transfer_date
        assert not document.consent
        assert not document.owner_cross_reference
    else:
        assert not documents


@pytest.mark.parametrize('id, has_results', TEST_ID_DATA)
def test_find_by_change_registration_id(session, id, has_results):
    """Assert that find documents by change registration id contains all expected elements."""
    documents = MhrDocument.find_by_change_registration_id(id)
    if has_results:
        assert documents
        document = documents[0]
        assert document.id == 200000000
        assert document.registration_id == 200000000
        assert document.change_registration_id == 200000000
        assert document.document_id == '77777000'
        assert document.document_registration_number == '90499999'
        assert document.document_type == MhrDocumentTypes.REG_101
        assert document.attention_reference == 'attn'
        assert document.declared_value == 90000
        assert document.consideration_value == '$90000.00'
        assert document.own_land == 'Y'
        assert document.transfer_date
        assert not document.consent
        assert not document.owner_cross_reference
    else:
        assert not documents


@pytest.mark.parametrize('id, has_results', TEST_DOC_ID_DATA)
def test_find_by_document_id(session, id, has_results):
    """Assert that find document by document id contains all expected elements."""
    document = MhrDocument.find_by_document_id(id)
    if has_results:
        assert document
        assert document.id == 200000000
        assert document.registration_id == 200000000
        assert document.change_registration_id == 200000000
        assert document.document_id == '77777000'
        assert document.document_registration_number == '90499999'
        assert document.document_type == MhrDocumentTypes.REG_101
        assert document.attention_reference == 'attn'
        assert document.declared_value == 90000
        assert document.consideration_value == '$90000.00'
        assert document.own_land == 'Y'
        assert document.transfer_date
        assert not document.consent
        assert not document.owner_cross_reference
    else:
        assert not document


@pytest.mark.parametrize('id, has_results', TEST_DOC_REG_NUM_DATA)
def test_find_by_doc_reg_num(session, id, has_results):
    """Assert that find document by document registration number contains all expected elements."""
    document = MhrDocument.find_by_doc_reg_num(id)
    if has_results:
        assert document
        assert document.id == 200000000
        assert document.registration_id == 200000000
        assert document.change_registration_id == 200000000
        assert document.document_id == '77777000'
        assert document.document_registration_number == '90499999'
        assert document.document_type == MhrDocumentTypes.REG_101
        assert document.attention_reference == 'attn'
        assert document.declared_value == 90000
        assert document.consideration_value == '$90000.00'
        assert document.own_land == 'Y'
        assert document.transfer_date
        assert not document.consent
        assert not document.owner_cross_reference
    else:
        assert not document


def test_document_json(session):
    """Assert that the document model renders to a json format correctly."""
    document: MhrDocument = TEST_DOCUMENT
    document_json = {
        'documentId': document.document_id,
        'documentRegistrationNumber': document.document_registration_number,
        'documentType': document.document_type,
        'declaredValue': document.declared_value,
        'ownLand': True,
        'attentionReference': document.attention_reference,
        'consideration': document.consideration_value,
        'consent': document.consent,
        'ownerCrossReference': document.owner_cross_reference
    }
    assert document.json == document_json


def test_create_from_reg_json(session):
    """Assert that the new MHR document is created from MH registration json data correctly."""
    json_data = copy.deepcopy(REGISTRATION)
    reg: MhrRegistration = MhrRegistration(id=1000, doc_id='docId', doc_reg_number='regNum')
    document: MhrDocument = MhrDocument.create_from_json(reg, json_data, MhrDocumentTypes.REG_101)
    assert document
    assert document.registration_id == 1000
    assert document.change_registration_id == 1000
    assert document.document_id == 'docId'
    assert document.document_type == MhrDocumentTypes.REG_101
    assert document.document_registration_number == 'regNum'
    assert document.attention_reference
