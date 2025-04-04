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

"""Tests to verify the endpoints for maintaining MH transfers.

Test-Suite to ensure that the /transfers endpoint is working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from flask import current_app
from registry_schemas.example_data.mhr import TRANSFER

from mhr_api.models import MhrRegistration, MhrRegistrationReport, MhrDocument
from mhr_api.models.type_tables import MhrRegistrationTypes
from mhr_api.services.authz import BCOL_HELP_ROLE, MHR_ROLE, STAFF_ROLE, COLIN_ROLE, REQUEST_EXEMPTION_RES, \
                                   TRANSFER_DEATH_JT, TRANSFER_SALE_BENEFICIARY, REQUEST_TRANSPORT_PERMIT
from tests.unit.services.utils import create_header, create_header_account
from tests.unit.utils.test_transfer_data import (
    TRAND_DELETE_GROUPS,
    TRAND_ADD_GROUPS,
    EXEC_DELETE_GROUPS,
    EXEC_ADD_GROUPS,
    WILL_DELETE_GROUPS,
    ADMIN_ADD_GROUPS,
    ADMIN_DELETE_GROUPS
)


MOCK_AUTH_URL = 'https://test.api.connect.gov.bc.ca/mockTarget/auth/api/v1/'
MOCK_PAY_URL = 'https://test.api.connect.gov.bc.ca/mockTarget/pay/api/v1/'
DOC_ID_VALID = '63166035'
DEALER_ROLES = [MHR_ROLE,REQUEST_TRANSPORT_PERMIT]
QUALIFIED_USER = [MHR_ROLE, REQUEST_EXEMPTION_RES, TRANSFER_DEATH_JT, TRANSFER_SALE_BENEFICIARY]


# testdata pattern is ({description}, {mhr_num}, {roles}, {status}, {account})
TEST_CREATE_DATA = [
    ('Invalid schema validation missing submitting', '000900', [MHR_ROLE, TRANSFER_SALE_BENEFICIARY],
     HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Missing account', '000900', [MHR_ROLE, TRANSFER_SALE_BENEFICIARY], HTTPStatus.BAD_REQUEST, None),
    ('Staff missing account', '000900', [MHR_ROLE, STAFF_ROLE, TRANSFER_SALE_BENEFICIARY],
     HTTPStatus.BAD_REQUEST, None),
    ('Invalid role product', '000900', [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Invalid BCOL helpdesk role', '000900', [MHR_ROLE, BCOL_HELP_ROLE], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Invalid non-transfer role', '000900', [MHR_ROLE], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Invalid transfer death role', '000900', [MHR_ROLE, TRANSFER_SALE_BENEFICIARY], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Valid staff', '000919', [MHR_ROLE, STAFF_ROLE, TRANSFER_SALE_BENEFICIARY], HTTPStatus.CREATED, 'PS12345'),
    ('Valid non-staff new', '000919', [MHR_ROLE, TRANSFER_DEATH_JT, TRANSFER_SALE_BENEFICIARY],
     HTTPStatus.CREATED, 'PS12345'),
    ('Invalid mhr num', '300655', [MHR_ROLE, TRANSFER_SALE_BENEFICIARY], HTTPStatus.UNAUTHORIZED, 'PS12345'),
    ('Invalid exempt', '000912', [MHR_ROLE, TRANSFER_SALE_BENEFICIARY], HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Invalid historical', '000913', [MHR_ROLE, TRANSFER_SALE_BENEFICIARY], HTTPStatus.BAD_REQUEST, 'PS12345'),
    ('Invalid non-staff missing declared value', '000900', [MHR_ROLE, TRANSFER_DEATH_JT, TRANSFER_SALE_BENEFICIARY],
     HTTPStatus.BAD_REQUEST, 'PS12345')
]
# testdata pattern is ({description}, {mhr_num}, {roles}, {status}, {account}, {reg_type})
TEST_CREATE_TRANS_DEATH_DATA = [
    ('Invalid TRANS_ADMIN non-staff', '000921', [MHR_ROLE, TRANSFER_DEATH_JT], HTTPStatus.BAD_REQUEST, 'PS12345',
     MhrRegistrationTypes.TRANS_ADMIN),
    ('Invalid TRANS_AFFIDAVIT non-staff', '000921', [MHR_ROLE, TRANSFER_DEATH_JT], HTTPStatus.BAD_REQUEST, 'PS12345',
     MhrRegistrationTypes.TRANS_AFFIDAVIT),
    ('Invalid TRANS_WILL non-staff', '000921', [MHR_ROLE, TRANSFER_DEATH_JT], HTTPStatus.BAD_REQUEST, 'PS12345',
     MhrRegistrationTypes.TRANS_WILL),
    ('Valid TRANS_ADMIN staff', '000921', [MHR_ROLE, STAFF_ROLE, TRANSFER_DEATH_JT], HTTPStatus.CREATED, 'PS12345',
     MhrRegistrationTypes.TRANS_ADMIN),
    ('Valid TRAND staff', '000920', [MHR_ROLE, STAFF_ROLE, TRANSFER_DEATH_JT], HTTPStatus.CREATED, 'PS12345',
     MhrRegistrationTypes.TRAND),
    ('Valid TRAND non-staff', '000920', QUALIFIED_USER, HTTPStatus.CREATED, 'PS12345', MhrRegistrationTypes.TRAND),
    ('Valid TRANS_AFFIDAVIT staff', '000921', [MHR_ROLE, STAFF_ROLE, TRANSFER_DEATH_JT], HTTPStatus.CREATED, 'PS12345',
     MhrRegistrationTypes.TRANS_AFFIDAVIT),
    ('Valid TRANS_WILL staff', '000921', [MHR_ROLE, STAFF_ROLE, TRANSFER_DEATH_JT], HTTPStatus.CREATED, 'PS12345',
     MhrRegistrationTypes.TRANS_WILL)
]
# testdata pattern is ({description}, {mhr_num}, {roles}, {status}, {account}, {tran_doc_type})
TEST_CREATE_DATA_TRANSFER = [
    ('Valid ABAN', '000919', [MHR_ROLE, STAFF_ROLE, TRANSFER_SALE_BENEFICIARY], HTTPStatus.CREATED, 'PS12345', 'ABAN'),
    ('Valid TRANS_WRIT_SEIZURE', '000919', [MHR_ROLE, STAFF_ROLE, TRANSFER_SALE_BENEFICIARY], HTTPStatus.CREATED, 
     'PS12345', 'TRANS_WRIT_SEIZURE'),
    ('Invalid schema validation WILL', '000900', [MHR_ROLE, TRANSFER_SALE_BENEFICIARY],
     HTTPStatus.BAD_REQUEST, 'PS12345', 'WILL'),
]

@pytest.mark.parametrize('desc,mhr_num,roles,status,account', TEST_CREATE_DATA)
def test_create(session, client, jwt, desc, mhr_num, roles, status, account):
    """Assert that a post MH registration works as expected."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    json_data = copy.deepcopy(TRANSFER)
    if STAFF_ROLE in roles:
        json_data['documentId'] = DOC_ID_VALID
    else:
        del json_data['documentId']
    del json_data['documentDescription']
    del json_data['createDateTime']
    del json_data['payment']
    json_data['mhrNumber'] = mhr_num
    if status == HTTPStatus.CREATED:
        json_data['deleteOwnerGroups'][0]['groupId'] = 1
        json_data['deleteOwnerGroups'][0]['type'] = 'SOLE'

    if desc == 'Invalid schema validation missing submitting':
        del json_data['submittingParty']
    elif desc == 'Invalid non-staff missing declared value':
        del json_data['declaredValue']
    elif desc == 'Invalid transfer death role':
        json_data['registrationType'] = MhrRegistrationTypes.TRAND

    if account:
        headers = create_header_account(jwt, roles, 'UT-TEST', account)
    else:
        headers = create_header(jwt, roles)
    # test
    response = client.post('/api/v1/transfers/' + mhr_num,
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    if desc == 'Invalid mhr num':
        assert response.status_code == status or response.status_code == HTTPStatus.NOT_FOUND
    else:
        assert response.status_code == status
    if response.status_code == HTTPStatus.CREATED:
        doc_id = response.json.get('documentId')
        assert doc_id
        doc: MhrDocument = MhrDocument.find_by_document_id(doc_id)
        assert doc
        reg_report: MhrRegistrationReport = MhrRegistrationReport.find_by_registration_id(doc.registration_id)
        assert reg_report
        assert reg_report.batch_registration_data


@pytest.mark.parametrize('desc,mhr_num,roles,status,account,reg_type', TEST_CREATE_TRANS_DEATH_DATA)
def test_create_transfer_death(session, client, jwt, desc, mhr_num, roles, status, account, reg_type):
    """Assert that a post MH registration works as expected."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    json_data = copy.deepcopy(TRANSFER)
    if STAFF_ROLE in roles:
        json_data['documentId'] = DOC_ID_VALID
    else:
        del json_data['documentId']
    del json_data['documentDescription']
    del json_data['createDateTime']
    del json_data['payment']
    json_data['mhrNumber'] = mhr_num
    json_data['registrationType'] = reg_type
    if reg_type == MhrRegistrationTypes.TRAND:
        json_data['deleteOwnerGroups'] = copy.deepcopy(TRAND_DELETE_GROUPS)
        json_data['addOwnerGroups'] = copy.deepcopy(TRAND_ADD_GROUPS)
    elif reg_type == MhrRegistrationTypes.TRANS_ADMIN:
        json_data['deleteOwnerGroups'] = copy.deepcopy(ADMIN_DELETE_GROUPS)
        json_data['addOwnerGroups'] = copy.deepcopy(ADMIN_ADD_GROUPS)
    elif reg_type == MhrRegistrationTypes.TRANS_WILL:
        json_data['deleteOwnerGroups'] = copy.deepcopy(WILL_DELETE_GROUPS)
        json_data['addOwnerGroups'] = copy.deepcopy(EXEC_ADD_GROUPS)
    else:
        json_data['deleteOwnerGroups'] = copy.deepcopy(EXEC_DELETE_GROUPS)
        json_data['addOwnerGroups'] = copy.deepcopy(EXEC_ADD_GROUPS)
    if reg_type == MhrRegistrationTypes.TRANS_AFFIDAVIT:
        json_data['declaredValue'] = 25000
    if account:
        headers = create_header_account(jwt, roles, 'UT-TEST', account)
    else:
        headers = create_header(jwt, roles)
    # test
    response = client.post('/api/v1/transfers/' + mhr_num,
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    # current_app.logger.info(response.json)
    assert response.status_code == status
    if response.status_code == HTTPStatus.CREATED:
        doc_id = response.json.get('documentId')
        assert doc_id
        doc: MhrDocument = MhrDocument.find_by_document_id(doc_id)
        assert doc
        reg_report: MhrRegistrationReport = MhrRegistrationReport.find_by_registration_id(doc.registration_id)
        assert reg_report
        assert reg_report.batch_registration_data


@pytest.mark.parametrize('desc,mhr_num,roles,status,account,tran_doc_type', TEST_CREATE_DATA_TRANSFER)
def test_create_tran_doc(session, client, jwt, desc, mhr_num, roles, status, account, tran_doc_type):
    """Assert that a post transfer registration with edge document types works as expected."""
    # setup
    current_app.config.update(PAYMENT_SVC_URL=MOCK_PAY_URL)
    current_app.config.update(AUTH_SVC_URL=MOCK_AUTH_URL)
    headers = None
    json_data = copy.deepcopy(TRANSFER)
    if STAFF_ROLE in roles:
        json_data['documentId'] = DOC_ID_VALID
    else:
        del json_data['documentId']
    del json_data['documentDescription']
    del json_data['createDateTime']
    del json_data['payment']
    json_data['mhrNumber'] = mhr_num
    json_data['deleteOwnerGroups'][0]['groupId'] = 1
    json_data['deleteOwnerGroups'][0]['type'] = 'SOLE'
    if tran_doc_type:
        json_data['transferDocumentType'] = tran_doc_type
    if account:
        headers = create_header_account(jwt, roles, 'UT-TEST', account)
    else:
        headers = create_header(jwt, roles)
    # test
    response = client.post('/api/v1/transfers/' + mhr_num,
                           json=json_data,
                           headers=headers,
                           content_type='application/json')

    # check
    assert response.status_code == status
    if response.status_code == HTTPStatus.CREATED:
        doc_id = response.json.get('documentId')
        assert doc_id
        doc: MhrDocument = MhrDocument.find_by_document_id(doc_id)
        assert doc
        reg_report: MhrRegistrationReport = MhrRegistrationReport.find_by_registration_id(doc.registration_id)
        assert reg_report
        assert reg_report.batch_registration_data
