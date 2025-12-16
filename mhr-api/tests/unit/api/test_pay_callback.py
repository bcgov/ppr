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

"""Tests to assure the credit card payment helper functions.

Test-Suite to ensure that the credit card payment helper functions are working as expected.
"""
import copy
from http import HTTPStatus

import pytest
from flask import current_app
from registry_schemas.example_data.mhr import ADMIN_REGISTRATION, EXEMPTION, PERMIT, REGISTRATION, TRANSFER

from mhr_api.exceptions import BusinessException
from mhr_api.models import MhrDraft, MhrRegistration, SearchRequest, SearchResult
from mhr_api.models.mhr_draft import DRAFT_PAY_PENDING_PREFIX
from mhr_api.models.search_result import SCORE_PAY_PENDING
from mhr_api.models.type_tables import MhrRegistrationStatusTypes, MhrRegistrationTypes
from mhr_api.resources import cc_payment_utils
from mhr_api.resources.registration_utils import setup_cc_draft
from mhr_api.resources.v1.pay_callback import get_search_id
from tests.unit.utils.test_registration_data import LOCATION_MANUFACTURER

# Valid search test data
MHR_NUMBER_JSON = {
    'type': 'MHR_NUMBER',
    'criteria': {
        'value': '000900'
    },
    'clientReferenceId': 'T-SQ-MM-1'
}
SET_SELECT_MM = [
    {'mhrNumber': '000900', 'status': 'ACTIVE', 'createDateTime': '1995-11-14T00:00:01+00:00',
     'homeLocation': 'CITY', 'serialNumber': '000060',
     'baseInformation': {'year': 2015, 'make': 'make', 'model': 'model'},
     'ownerName': {'first': 'BOB', 'middle': 'ARTHUR', 'last': 'MCKAY'}}
]
CC_PAYREF = {
     "invoiceId": "88888888",
     "receipt": "receipt",
     "ccPayment": True,
     "paymentActionRequired": True,
     "paymentPortalURL": "{PAYMENT_PORTAL_URL}/{invoice_id}/{return_URL}"
}
PUB_SUB_PAYLOAD = {
    "corpTypeCode": "MHR",
    "id": "999999999",
    "statusCode": "COMPLETED",
    "filingIdentifier": ""
}
# valid registration data
TRANSFER_DEATH = copy.deepcopy(TRANSFER)
TRANSFER_DEATH["registrationType"] = MhrRegistrationTypes.TRAND.value
ADMIN_REGISTRATION_CANCELLED = copy.deepcopy(ADMIN_REGISTRATION)
ADMIN_REGISTRATION_CANCELLED["documentType"] = "CANCEL_PERMIT"
ADMIN_REGISTRATION_CANCELLED["location"] = copy.deepcopy(LOCATION_MANUFACTURER)
# testdata pattern is ({desc}, {status}, {draft_json}, {mhr_num}, {reg_type}, {invoice_id})
TEST_CALLBACK_DATA = [
    ('Valid new reg', HTTPStatus.OK, REGISTRATION, None, MhrRegistrationTypes.MHREG.value, "20000100"),
    ('Valid exemption', HTTPStatus.OK, EXEMPTION, "000919", MhrRegistrationTypes.EXEMPTION_RES.value, "20000101"),
    ('Valid permit', HTTPStatus.OK, PERMIT, "000900", MhrRegistrationTypes.PERMIT.value, "20000102"),
    ('Valid transfer', HTTPStatus.OK, TRANSFER, "000919", MhrRegistrationTypes.TRANS.value, "20000103"),
    ('Valid transfer to surviving joint tenant', HTTPStatus.OK, TRANSFER_DEATH, "000901", MhrRegistrationTypes.TRAND.value, "20000104"),
    ('Valid permit extension', HTTPStatus.OK, PERMIT, "000931", MhrRegistrationTypes.PERMIT_EXTENSION.value, "20000105"),
    ('Valid amendment', HTTPStatus.OK, PERMIT, "000931", MhrRegistrationTypes.PERMIT_EXTENSION.value, "20000106"),
    ('Valid permit cancelled', HTTPStatus.OK, ADMIN_REGISTRATION_CANCELLED, "000931", MhrRegistrationTypes.REG_STAFF_ADMIN.value, "20000107"),
    ('Invalid admin reg', HTTPStatus.OK, ADMIN_REGISTRATION, "000931", MhrRegistrationTypes.REG_STAFF_ADMIN.value, "20000100"),
    ('Invalid no key', HTTPStatus.UNAUTHORIZED, REGISTRATION, None, MhrRegistrationTypes.MHREG.value, "20000100"),
    ('Invalid missing payload', HTTPStatus.BAD_REQUEST, REGISTRATION, None, MhrRegistrationTypes.MHREG.value, "20000100"),
    ('Invalid missing status', HTTPStatus.BAD_REQUEST, REGISTRATION, None, MhrRegistrationTypes.MHREG.value, "20000100"),
    ('Invalid status', HTTPStatus.BAD_REQUEST, REGISTRATION, None, MhrRegistrationTypes.MHREG.value, "20000100"),
    ('Invalid used', HTTPStatus.OK, REGISTRATION, None, MhrRegistrationTypes.MHREG.value, "20000100"),
]
# testdata pattern is ({desc}, {invoice_id},  {search_id})
TEST_SEARCH_ID_DATA = [
    ('Valid', 20000200, 20000200),
]
# testdata pattern is ({description}, {status}, {search data}, {select data}, {invoice_id})
TEST_SEARCH_DATA = [
    ('MHR Number Match', HTTPStatus.OK, MHR_NUMBER_JSON, SET_SELECT_MM, "88888888"),
]


def setup_registration(draft_json: dict, reg_type: str, invoice_id: str) -> dict:
    """Set up registration for cc processing."""
    json_data = copy.deepcopy(draft_json)
    json_data["registrationType"] = reg_type
    if json_data.get("mhrNumber") and reg_type == MhrRegistrationTypes.MHREG.value:
        del json_data["mhrNumber"]
    elif reg_type == MhrRegistrationTypes.EXEMPTION_RES.value:
        del json_data['documentId']
        del json_data['documentRegistrationNumber']
        del json_data['documentDescription']
        del json_data['createDateTime']
        json_data['nonResidential'] = False
    elif reg_type in (
        MhrRegistrationTypes.PERMIT.value,
        MhrRegistrationTypes.PERMIT_EXTENSION.value,
        MhrRegistrationTypes.AMENDMENT.value
    ):
        del json_data['documentId']
        del json_data['documentRegistrationNumber']
        del json_data['documentDescription']
        del json_data['createDateTime']
        del json_data['payment']
        del json_data['note']
    elif reg_type in (
        MhrRegistrationTypes.TRANS.value,
        MhrRegistrationTypes.TRAND.value
    ):
        del json_data['documentId']
        del json_data['documentDescription']
        del json_data['createDateTime']
        del json_data['payment']
    elif reg_type == MhrRegistrationTypes.REG_STAFF_ADMIN.value:
        del json_data['documentId']
        del json_data['documentRegistrationNumber']
        del json_data['documentDescription']
        del json_data['createDateTime']
        del json_data['updateDocumentId']
        del json_data['payment']
        del json_data['note']
    pay_ref: dict = copy.deepcopy(CC_PAYREF)
    if invoice_id:
        pay_ref["invoiceId"] = invoice_id
    json_data = setup_cc_draft(json_data, pay_ref, "PS12345", "username@idir", "ppr_staff")
    return json_data


# testdata pattern is ({description}, {search data}, {select data}, {invoice_id})
@pytest.mark.parametrize('desc,status,search_data,select_data,invoice_id', TEST_SEARCH_DATA)
def test_pay_callback_search(session, client, jwt, desc, status, search_data, select_data, invoice_id):
    """Assert that completing a new cc payment search from a callback works as expected."""
    if not current_app.config.get('SUBSCRIPTION_API_KEY'):
        return
    apikey = current_app.config.get('SUBSCRIPTION_API_KEY')
    headers = {
        'x-apikey': apikey
    }
    pay_ref = copy.deepcopy(CC_PAYREF)
    pay_ref["invoiceId"] = invoice_id
    search_query: SearchRequest = SearchRequest.create_from_json(search_data, 'PS12345')
    search_query.pay_invoice_id = int(invoice_id)
    search_query.pay_path = invoice_id
    search_query.search()
    # current_app.logger.info(search_query.json)
    search_detail: SearchResult = SearchResult.create_from_search_query(search_query)
    search_detail.save()
    pay_params: dict = {
        "searchId": str(search_detail.search_id),
        "clientReferenceId": search_query.client_reference_id,
        "accountId": search_query.account_id,
        "certified": False,
        "staff": False,
        "callbackURL": ""
    }
    search_detail2: SearchResult = SearchResult.validate_search_select(select_data, search_detail.search_id)
    search_detail2.score = SCORE_PAY_PENDING
    search_detail2.update_selection(select_data, 'account name', pay_params, pay_ref)
    cc_payment_utils.track_search_payment(search_detail.search_response, "PS12345", str(search_query.id))
    payload = copy.deepcopy(PUB_SUB_PAYLOAD)
    payload["id"] = invoice_id
    rv = client.post('/api/v1/pay-callback/' + invoice_id,
                     json=payload,
                     headers=headers,
                     content_type='application/json')
    # check
    assert rv.status_code == status
 

@pytest.mark.parametrize('desc,status,draft_json,mhr_num,reg_type,invoice_id', TEST_CALLBACK_DATA)
def test_pay_callback(session, client, jwt, desc, status, draft_json, mhr_num, reg_type, invoice_id):
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
    if status not in (HTTPStatus.UNAUTHORIZED, HTTPStatus.NOT_FOUND):
        json_data = setup_registration(draft_json, reg_type, invoice_id)
        new_reg: MhrRegistration = None
        base_reg: MhrRegistration = None
        if reg_type == MhrRegistrationTypes.MHREG.value:
            new_draft: MhrDraft = MhrDraft.create_from_mhreg_json(json_data, "PS12345", "username@idir")
            new_draft.save()
            mhr_num = new_draft.mhr_number
            json_data["mhrNumber"] = new_draft.mhr_number
            new_reg = cc_payment_utils.save_new_cc_draft(json_data, new_draft)
        else:
            json_data["mhrNumber"] = mhr_num
            base_reg: MhrRegistration = MhrRegistration.find_all_by_mhr_number(mhr_num, "PS12345", True)
            new_reg: MhrRegistration = cc_payment_utils.save_change_cc_draft(base_reg, json_data)

    payload = copy.deepcopy(PUB_SUB_PAYLOAD) if desc != "Invalid missing payload" else {}
    if payload:
        payload["id"] = invoice_id
    if desc == 'Invalid missing status':
        del payload["statusCode"]
    elif desc == 'Invalid status':
        payload["statusCode"] = "CREATED"
    rv = client.post('/api/v1/pay-callback/' + str(invoice_id),
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
        assert rv.status_code in (HTTPStatus.NOT_FOUND, HTTPStatus.BAD_REQUEST, HTTPStatus.OK)
    if desc.startswith('Valid'):
        reg = MhrRegistration.find_by_mhr_number(mhr_num, "PS12345", reg_type=reg_type)
        assert reg
    if desc == 'Invalid admin reg':
        with pytest.raises(BusinessException) as err:
            MhrRegistration.find_by_mhr_number(mhr_num, "PS12345", reg_type=reg_type)
            assert err.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('desc,invoice_id,search_id', TEST_SEARCH_ID_DATA)
def test_get_search_id(session, client, jwt, desc, invoice_id, search_id):
    """Assert that extracting a search id from event tracking record message works as expected."""
    json_data = {
        "payment": {"invoiceId": str(invoice_id)}
    }
    cc_payment_utils.track_search_payment(json_data, "PS12345", str(search_id))
    test_search_id: int = get_search_id(str(invoice_id))
    assert test_search_id
    assert test_search_id == search_id
