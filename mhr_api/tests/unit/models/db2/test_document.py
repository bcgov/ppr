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

"""Tests to assure the legacy DB2 Document Model.

Test-Suite to ensure that the legacy DB2 Document Model is working as expected.
"""

import pytest

from mhr_api.models import Db2Document, utils as model_utils


# testdata pattern is ({exists}, {id}, {mhr_num}, {doc_type}, {doc_reg_id})
TEST_DATA = [
    (True, 'REG22911', '022911', 'CONV', '00022911'),
    (False, 0, None, None, None)
]


@pytest.mark.parametrize('exists,id,mhr_num,doc_type,doc_reg_id', TEST_DATA)
def test_find_by_id(session, exists, id, mhr_num, doc_type, doc_reg_id):
    """Assert that find document by id contains all expected elements."""
    doc: Db2Document = Db2Document.find_by_id(id)
    if exists:
        assert doc
        assert doc.id == id
        assert doc.mhr_number == mhr_num
        assert doc.document_type == doc_type
        assert doc.document_reg_id == doc_reg_id
        assert doc.draft_ts is not None
        assert doc.registration_ts is not None
        assert doc.interimed is not None
        assert doc.owner_cross_reference is not None
        assert doc.interest_denominator is not None
        assert doc.declared_value is not None
        assert doc.own_land is not None
        assert doc.routing_slip_number is not None
        assert doc.last_service is not None
        assert doc.bcol_account is not None
        assert doc.dat_number is not None
        assert doc.examiner_id is not None
        assert doc.update_id is not None
        assert doc.phone_number is not None
        assert doc.attention_reference is not None
        assert doc.legacy_address is not None
        assert doc.number_of_pages is not None
        assert doc.transfer_execution_date is not None
        assert doc.consideration_value is not None
        assert doc.affirm_by_name is not None
        assert doc.liens_with_consent is not None
        assert doc.client_reference_id is not None

    else:
        assert not doc


@pytest.mark.parametrize('exists,id,mhr_num,doc_type,doc_reg_id', TEST_DATA)
def test_find_by_mhr_number(session, exists, id, mhr_num, doc_type, doc_reg_id):
    """Assert that find document by mhr number contains all expected elements."""
    docs = Db2Document.find_by_mhr_number(mhr_num)
    if exists:
        assert docs
        for doc in docs:
            assert doc.mhr_number == mhr_num
            if doc.id == id:
                assert doc.document_type == doc_type
                assert doc.document_reg_id == doc_reg_id
                assert doc.draft_ts is not None
                assert doc.registration_ts is not None
                assert doc.interimed is not None
                assert doc.owner_cross_reference is not None
                assert doc.interest_denominator is not None
                assert doc.declared_value is not None
                assert doc.own_land is not None
                assert doc.routing_slip_number is not None
                assert doc.last_service is not None
                assert doc.bcol_account is not None
                assert doc.dat_number is not None
                assert doc.examiner_id is not None
                assert doc.update_id is not None
                assert doc.phone_number is not None
                assert doc.attention_reference is not None
                assert doc.legacy_address is not None
                assert doc.number_of_pages is not None
                assert doc.transfer_execution_date is not None
                assert doc.consideration_value is not None
                assert doc.affirm_by_name is not None
                assert doc.liens_with_consent is not None
                assert doc.client_reference_id is not None

    else:
        assert not docs


@pytest.mark.parametrize('exists,id,mhr_num,doc_type,doc_reg_id', TEST_DATA)
def test_find_by_doc_id(session, exists, id, mhr_num, doc_type, doc_reg_id):
    """Assert that find document by document id contains all expected elements."""
    doc = Db2Document.find_by_doc_id(doc_reg_id)
    if exists:
        assert doc
        assert doc.mhr_number == mhr_num
        if doc.id == id:
            assert doc.document_type == doc_type
            assert doc.document_reg_id == doc_reg_id
            assert doc.draft_ts is not None
            assert doc.registration_ts is not None
            assert doc.interimed is not None
            assert doc.owner_cross_reference is not None
            assert doc.interest_denominator is not None
            assert doc.declared_value is not None
            assert doc.own_land is not None
            assert doc.routing_slip_number is not None
            assert doc.last_service is not None
            assert doc.bcol_account is not None
            assert doc.dat_number is not None
            assert doc.examiner_id is not None
            assert doc.update_id is not None
            assert doc.phone_number is not None
            assert doc.attention_reference is not None
            assert doc.legacy_address is not None
            assert doc.number_of_pages is not None
            assert doc.transfer_execution_date is not None
            assert doc.consideration_value is not None
            assert doc.affirm_by_name is not None
            assert doc.liens_with_consent is not None
            assert doc.client_reference_id is not None
    else:
        assert not doc


def test_document_json(session):
    """Assert that the document renders to a json format correctly."""
    doc = Db2Document(mhr_number='022911',
                        document_type='CONV',
                        document_reg_id='00022911',
                        interimed=' ',
                        owner_cross_reference=' ',
                        interest_denominator=0,
                        declared_value=12000,
                        own_land='N',
                        routing_slip_number='1234')
    doc.last_service = ' '
    doc.bcol_account = '1234'
    doc.dat_number = '5678'
    doc.examiner_id = 'X1234'
    doc.update_id = 'Y1234'
    doc.phone_number = '6041234567'
    doc.attention_reference = 'attn'
    doc.name = 'name'
    doc.legacy_address = 'address'
    doc.number_of_pages = 0
    doc.consideration_value = 'considerationValue'
    doc.affirm_by_name = 'affirmByName'
    doc.liens_with_consent = 'liensWithConsent'
    doc.client_reference_id = 'clientReferenceId'
    doc.draft_ts = model_utils.ts_from_iso_format('1995-11-10T17:20:22+00:00')
    doc.registration_ts = model_utils.ts_from_iso_format('1995-11-14T08:00:01+00:00')
    doc.transfer_execution_date = model_utils.date_from_iso_format('0001-01-01')

    test_json = {
        'mhrNumber': doc.mhr_number,
        'documentType': doc.document_type,
        'documentRegistrationId': doc.document_reg_id,
        'interimed': doc.interimed,
        'ownerCrossReference': doc.owner_cross_reference,
        'interestDenominator': doc.interest_denominator,
        'declaredValue': doc.declared_value,
        'ownLand': doc.own_land,
        'routingSlipNumber': doc.routing_slip_number,
        'lastService': doc.last_service,
        'bcolAccount': doc.bcol_account,
        'datNumber': doc.dat_number,
        'examinerId': doc.examiner_id,
        'updateId': doc.update_id,
        'phoneNumber': doc.phone_number,
        'attentionReference': doc.attention_reference,
        'name': doc.name,
        'legacyAddress': doc.legacy_address,
        'numberOfPages': doc.number_of_pages,
        'considerationValue': doc.consideration_value,
        'affirmByName': doc.affirm_by_name,
        'liensWithConsent': doc.liens_with_consent,
        'clientReferenceId': doc.client_reference_id,
        'draftDateTime': '1995-11-10T17:20:22+00:00',
        'createDateTime': '1995-11-14T08:00:01+00:00',
        'transferExecutionDate': '0001-01-01'
    }
    assert doc.json == test_json
