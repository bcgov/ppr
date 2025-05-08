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

"""Tests to verify the financing-statement endpoint.

Test-Suite to ensure that the /financing-statement endpoint is working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from flask import current_app
from registry_schemas.example_data.ppr import (
    AMENDMENT_STATEMENT,
    FINANCING_STATEMENT,
    RENEWAL_STATEMENT,
)

from ppr_api.models import FinancingStatement, Registration, utils as model_utils
from ppr_api.resources import cc_payment_utils, utils as resource_utils
from ppr_api.resources.financing_utils import setup_cc_draft
from ppr_api.resources.utils import get_payment_details, get_payment_details_financing, \
     get_payment_type_financing
from ppr_api.services.authz import COLIN_ROLE, PPR_ROLE, STAFF_ROLE, BCOL_HELP, GOV_ACCOUNT_ROLE
from ppr_api.services.payment import TransactionTypes
from tests.unit.services.utils import create_header, create_header_account, create_header_account_report


MOCK_URL_NO_KEY = 'https://test.api.connect.gov.bc.ca/mockTarget/auth/api/v1/'
MOCK_PAY_URL = 'https://test.api.connect.gov.bc.ca/mockTarget/pay/api/v1/'
CC_PAYREF = {
     "invoiceId": "88888888",
     "receipt": "receipt",
     "ccPayment": True,
     "paymentActionRequired": True,
     "paymentPortalURL": "{PAYMENT_PORTAL_URL}/{invoice_id}/{return_URL}"
}
PUB_SUB_PAYLOAD = {
    "corpTypeCode": "PPR",
    "id": "88888888",
    "statusCode": "COMPLETED",
    "filingIdentifier": ""
}
# testdata pattern is ({desc}, {status}, {registration_id}, {party_id})
TEST_MAIL_CALLBACK_DATA = [
    ('Missing reg id', HTTPStatus.BAD_REQUEST, None, 9999999),
    ('Invalid reg id', HTTPStatus.NOT_FOUND, 300000005, 200000024),
    ('Missing party id', HTTPStatus.BAD_REQUEST, 200000004, None),
    ('Invalid party id', HTTPStatus.NOT_FOUND, 200000004, 9999999),
    ('Already exists', HTTPStatus.OK, 200000004, 200000013),
    ('Unauthorized', HTTPStatus.UNAUTHORIZED, 200000008, 200000023)
]
# testdata pattern is ({desc}, {status}, {start_ts}, {end_ts})
TEST_MAIL_LIST_DATA = [
    ('Missing start ts', HTTPStatus.BAD_REQUEST, None, None),
    ('Invalid start ts', HTTPStatus.BAD_REQUEST, '2023-01-31TXX:00:01-08:00', None),
    ('Invalid range', HTTPStatus.BAD_REQUEST, '2023-01-31T00:00:01-08:00', '2023-01-30T00:00:01-08:00'),
    ('Invalid end ts', HTTPStatus.BAD_REQUEST, None, '2023-01-31TXX:00:01-08:00'),
    ('Valid start', HTTPStatus.OK, '2023-01-31T00:00:01-08:00', None),
    ('Valid start with job id', HTTPStatus.OK, '2023-01-31T00:00:01-08:00', None),
    ('Unauthorized', HTTPStatus.UNAUTHORIZED, None, None)
]
# testdata pattern is ({desc}, {status}, {draft_json}, {reg_num}, {fs_id}, {reg_class}, {invoice_id})
TEST_PAY_CALLBACK_DATA = [
    ('Valid new reg', HTTPStatus.OK, FINANCING_STATEMENT, None, None, model_utils.REG_CLASS_PPSA, "20000100"),
    ('Valid amendment', HTTPStatus.OK, AMENDMENT_STATEMENT, "TEST0001", 200000000, model_utils.REG_CLASS_AMEND, "20000101"),
    ('Valid renewal', HTTPStatus.OK, RENEWAL_STATEMENT, "TEST0005", 200000004, model_utils.REG_CLASS_RENEWAL, "20000102"),
    ('Invalid no key', HTTPStatus.UNAUTHORIZED, FINANCING_STATEMENT, None, None, model_utils.REG_CLASS_PPSA, "20000100"),
    ('Invalid missing payload', HTTPStatus.BAD_REQUEST, FINANCING_STATEMENT, None, None, model_utils.REG_CLASS_PPSA, "20000100"),
    ('Invalid missing status', HTTPStatus.BAD_REQUEST, FINANCING_STATEMENT, None, None, model_utils.REG_CLASS_PPSA, "20000100"),
    ('Invalid status', HTTPStatus.BAD_REQUEST, FINANCING_STATEMENT, None,  None, model_utils.REG_CLASS_PPSA, "20000100"),
    ('Invalid used', HTTPStatus.OK, FINANCING_STATEMENT, None,  None, model_utils.REG_CLASS_PPSA, "20000100"),
]


@pytest.mark.parametrize('desc,status,reg_id,party_id', TEST_MAIL_CALLBACK_DATA)
def test_callback_mail_report(session, client, jwt, desc, status, reg_id, party_id):
    """Assert that a mail report callback request returns the expected status."""
    # setup
    if is_ci_testing():
        return
    json_data = {
        'registrationId': reg_id,
        'partyId': party_id
    }
    if reg_id is None:
        del json_data['registrationId']
    if party_id is None:
        del json_data['partyId']
    headers = None
    if status != HTTPStatus.UNAUTHORIZED:
        apikey = current_app.config.get('SUBSCRIPTION_API_KEY')
        if apikey:
            headers = {
                'x-apikey': apikey
            }

    # test
    rv = client.post('/api/v1/callbacks/mail-report',
                     json=json_data,
                     headers=headers,
                     content_type='application/json')
    # check
    assert rv.status_code == status


@pytest.mark.parametrize('desc,status,start_ts,end_ts', TEST_MAIL_LIST_DATA)
def test_list_mail_report(session, client, jwt, desc, status, start_ts, end_ts):
    """Assert that list mail reports by timestamp request returns the expected status."""
    # setup
    if is_ci_testing():
        return
    params = ''
    if start_ts:
        params += f'?startDateTime={start_ts}'
        if end_ts:
            params += f'&endDateTime={end_ts}'
    elif end_ts:
        params += f'?endDateTime={end_ts}'
    if desc == 'Valid start with job id':
        params += '&jobId=1234'

    headers = None
    if status != HTTPStatus.UNAUTHORIZED:
        apikey = current_app.config.get('SUBSCRIPTION_API_KEY')
        if apikey:
            headers = {
                'x-apikey': apikey
            }

    # test
    rv = client.get('/api/v1/callbacks/mail-report' + params,
                     headers=headers)
    # check
    assert rv.status_code == status
    if rv.status_code == HTTPStatus.OK:
        assert rv.json
        for result in rv.json:
            assert result.get('id')
            assert result.get('dateTime')
            assert result.get('docStorageRef')
            if desc == 'Valid start with job id':
                assert result.get('jobId')


@pytest.mark.parametrize('desc,status,draft_json,reg_num,fs_id,reg_class,invoice_id', TEST_PAY_CALLBACK_DATA)
def test_pay_callback(session, client, jwt, desc, status, draft_json, reg_num, fs_id, reg_class, invoice_id):
    """Assert that creating a new cc payment registration from a callback works as expected."""
    if not current_app.config.get('SUBSCRIPTION_API_KEY'):
        return
    headers = None
    if status != HTTPStatus.UNAUTHORIZED:
        apikey = current_app.config.get('SUBSCRIPTION_API_KEY')
        if apikey:
            headers = {
                'x-apikey': apikey
            }
    if status not in (HTTPStatus.UNAUTHORIZED, HTTPStatus.BAD_REQUEST):
        json_data = setup_registration(draft_json, reg_class, invoice_id, reg_num)

        account_id: str = "PS12345"
        new_reg: Registration = None
        statement: FinancingStatement = None
        if fs_id:
            statement = FinancingStatement.find_by_financing_id(fs_id)
        if model_utils.REG_CLASS_PPSA == reg_class:
            save_reg: Registration = resource_utils.create_new_pay_registration(json_data, account_id)
            new_fs = cc_payment_utils.save_new_cc_draft(json_data, save_reg)
            new_reg = new_fs.registration[0]
        elif model_utils.REG_CLASS_AMEND == reg_class:
            json_data["baseRegistrationNumber"] = reg_num
            for party in statement.parties:
                if party.registration_id != 200000000 and not party.registration_id_end:
                    if party.party_type == 'DB' or party.party_type == 'DI':
                        json_data['deleteDebtors'][0]['partyId'] = party.id
                    elif party.party_type == 'SP':
                        json_data['deleteSecuredParties'][0]['partyId'] = party.id
            for gc in statement.general_collateral:
                if gc.registration_id != 200000000 and not gc.registration_id_end:
                    json_data['deleteGeneralCollateral'][0]['collateralId'] = gc.id
            for vc in statement.vehicle_collateral:
                if vc.registration_id != 200000000 and not vc.registration_id_end:
                    json_data['deleteVehicleCollateral'][0]['vehicleId'] = vc.id
            save_reg: Registration = resource_utils.create_new_pay_registration(json_data, account_id, reg_class)
            new_reg = cc_payment_utils.save_change_cc_draft(statement.registration[0],
                                                                        json_data,
                                                                        save_reg)
        else:
            json_data["baseRegistrationNumber"] = reg_num
            save_reg: Registration = resource_utils.create_new_pay_registration(json_data, account_id, reg_class)
            new_reg = cc_payment_utils.save_change_cc_draft(statement.registration[0],
                                                                        json_data,
                                                                        save_reg)
        assert new_reg

    payload = copy.deepcopy(PUB_SUB_PAYLOAD) if desc != "Invalid missing payload" else {}
    if payload:
        payload["id"] = invoice_id
    if desc == 'Invalid missing status':
        del payload["statusCode"]
    elif desc == 'Invalid status':
        payload["statusCode"] = "CREATED"
    rv = client.post('/api/v1/callbacks/pay/' + str(invoice_id),
                     json=payload,
                     headers=headers,
                     content_type='application/json')
    # check
    assert rv.status_code == status
    if desc == 'Invalid used':
        rv = client.post('/api/v1/pay-callback/' + str(invoice_id),
                        json=payload,
                        headers=headers,
                        content_type='application/json')
        assert rv.status_code in (HTTPStatus.NOT_FOUND, HTTPStatus.BAD_REQUEST)


def setup_registration(draft_json: dict, reg_class: str, invoice_id: str, reg_num: str) -> dict:
    """Set up registration for cc processing."""
    json_data = copy.deepcopy(draft_json)
    account_id: str = "PS12345"
    if model_utils.REG_CLASS_PPSA == reg_class:
        del json_data['createDateTime']
        del json_data['baseRegistrationNumber']
        del json_data['payment']
        del json_data['lifeInfinite']
        del json_data['expiryDate']
        del json_data['documentId']
        del json_data['lienAmount']
        del json_data['surrenderDate']
    elif model_utils.REG_CLASS_AMEND == reg_class:
        del json_data['createDateTime']
        del json_data['amendmentRegistrationNumber']
        del json_data['payment']
        del json_data['addTrustIndenture']
        del json_data['removeTrustIndenture']
        if json_data.get("courtOrderInformation"):
            del json_data["courtOrderInformation"]
        json_data["baseRegistrationNumber"] = reg_num
    else:
        del json_data['createDateTime']
        del json_data['renewalRegistrationNumber']
        del json_data['payment']
        del json_data['courtOrderInformation']
        json_data["baseRegistrationNumber"] = reg_num
    if "documentId" in json_data:
        del json_data["documentId"]
    pay_ref: dict = copy.deepcopy(CC_PAYREF)
    if invoice_id:
        pay_ref["invoiceId"] = invoice_id
    json_data = setup_cc_draft(json_data, pay_ref, account_id, "username@idir")
    return json_data


def is_ci_testing() -> bool:
    """Check unit test environment: exclude most reports for CI testing."""
    return  current_app.config.get("DEPLOYMENT_ENV", "testing") == "testing"
