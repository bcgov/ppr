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

import pytest
from flask import current_app
from registry_schemas.example_data.ppr import (
    AMENDMENT_STATEMENT,
    FINANCING_STATEMENT,
    DRAFT_AMENDMENT_STATEMENT,
    DRAFT_FINANCING_STATEMENT,
    RENEWAL_STATEMENT,
)

from ppr_api.models import Draft, FinancingStatement, Registration, utils as model_utils
from ppr_api.models.draft import DRAFT_PAY_PENDING_PREFIX
from ppr_api.models.type_tables import RegistrationTypes
from ppr_api.resources import cc_payment_utils, utils as resource_utils
from ppr_api.resources.financing_utils import setup_cc_draft


CC_PAYREF = {
     "invoiceId": "88888888",
     "receipt": "receipt",
     "ccPayment": True,
     "paymentActionRequired": True,
     "paymentPortalURL": "{PAYMENT_PORTAL_URL}/{invoice_id}/{return_URL}"
}
# testdata pattern is ({pay_ref}, {account_id}, {username}, {draft_json}, {create_draft}, {base_reg_num}, {reg_type})
TEST_CHANGE_DATA = [
    (CC_PAYREF, "PS12345", "username", AMENDMENT_STATEMENT, False, "TEST0001", RegistrationTypes.AM.value),
    (CC_PAYREF, "PS12345", "username", AMENDMENT_STATEMENT, True, "TEST0001", RegistrationTypes.AM.value)
]
TEST_NEW_DATA = [
    (CC_PAYREF, "PS12345", "username", FINANCING_STATEMENT, False, RegistrationTypes.SA.value)
]
# testdata pattern is ({draft_json}, {reg_num}, {fs_id}, {reg_class}, {invoice_id})
TEST_REGISTRATION_DATA = [
    (FINANCING_STATEMENT, None, None, model_utils.REG_CLASS_PPSA, "20000200"),
    (AMENDMENT_STATEMENT, "TEST0001", 200000000, model_utils.REG_CLASS_AMEND, "20000201"),
    (RENEWAL_STATEMENT, "TEST0005", 200000004, model_utils.REG_CLASS_RENEWAL, "20000202")
]


@pytest.mark.parametrize('pay_ref,account_id,username,draft_json,create_draft,reg_type', TEST_NEW_DATA)
def test_new_registration(session, pay_ref, account_id, username, draft_json, create_draft, reg_type):
    """Assert that a new home registration is set up correctly for a credit card payment client registration."""
    json_data = copy.deepcopy(draft_json)
    json_data['type'] = reg_type
    del json_data['createDateTime']
    del json_data['baseRegistrationNumber']
    del json_data['payment']
    del json_data['lifeInfinite']
    del json_data['expiryDate']
    del json_data['documentId']
    del json_data['lienAmount']
    del json_data['surrenderDate']
    json_data = setup_cc_draft(json_data, pay_ref, account_id, username)
    if create_draft:
        new_draft_json = copy.deepcopy(DRAFT_FINANCING_STATEMENT)
        draft: Draft = Draft.create_from_json(new_draft_json, account_id)
        draft.save()
        assert draft.document_number
        json_data['documentId'] = draft.document_number
    save_reg: Registration = resource_utils.create_new_pay_registration(json_data, account_id)
    new_fs: FinancingStatement = cc_payment_utils.save_new_cc_draft(json_data, save_reg)
    assert not new_fs.id
    new_reg: Registration = new_fs.registration[0]
    assert not new_reg.id
    assert new_reg.draft
    assert new_reg.reg_json
    draft: Draft = new_reg.draft
    assert draft.document_number.startswith(DRAFT_PAY_PENDING_PREFIX)
    assert draft.user_id == pay_ref.get("invoiceId")
    assert not draft.registration_number
    assert draft.registration_type == reg_type
    reg_json = new_reg.reg_json
    assert reg_json.get("paymentPending")
    assert reg_json["payment"] == pay_ref
    assert reg_json.get("accountId") == account_id
    assert reg_json.get("username") == username
    assert reg_json.get("registrationType") == reg_type
    assert not reg_json.get("registrationNumber")


@pytest.mark.parametrize('pay_ref,account_id,username,draft_json,create_draft,base_reg_num,reg_type', TEST_CHANGE_DATA)
def test_change_registration(session, pay_ref, account_id, username, draft_json, create_draft, base_reg_num, reg_type):
    """Assert that a change registration is set up correctly for a credit card payment client registration."""
    json_data = copy.deepcopy(draft_json)
    del json_data['createDateTime']
    del json_data['amendmentRegistrationNumber']
    del json_data['payment']
    del json_data['addTrustIndenture']
    del json_data['removeTrustIndenture']
    if json_data.get("courtOrderInformation"):
        del json_data["courtOrderInformation"]
    if "documentId" in json_data:
        del json_data["documentId"]
    json_data = setup_cc_draft(json_data, pay_ref, account_id, username)
    financing_statement = FinancingStatement.find_by_financing_id(200000000)
    assert financing_statement
    for party in financing_statement.parties:
        if party.registration_id != 200000000 and not party.registration_id_end:
            if party.party_type == 'DB' or party.party_type == 'DI':
                json_data['deleteDebtors'][0]['partyId'] = party.id
            elif party.party_type == 'SP':
                json_data['deleteSecuredParties'][0]['partyId'] = party.id

    for gc in financing_statement.general_collateral:
        if gc.registration_id != 200000000 and not gc.registration_id_end:
            json_data['deleteGeneralCollateral'][0]['collateralId'] = gc.id

    for vc in financing_statement.vehicle_collateral:
        if vc.registration_id != 200000000 and not vc.registration_id_end:
            json_data['deleteVehicleCollateral'][0]['vehicleId'] = vc.id

    if create_draft:
        new_draft_json = copy.deepcopy(DRAFT_AMENDMENT_STATEMENT)
        draft = Draft.create_from_json(new_draft_json, account_id)
        draft.save()
        assert draft.document_number
        json_data['documentId'] = draft.document_number

    save_reg: Registration = resource_utils.create_new_pay_registration(json_data, account_id, model_utils.REG_CLASS_AMEND)
    new_reg: Registration = cc_payment_utils.save_change_cc_draft(financing_statement.registration[0],
                                                                  json_data,
                                                                  save_reg)
    assert not new_reg.id
    assert new_reg.draft
    assert new_reg.reg_json
    draft: Draft = new_reg.draft
    assert draft.document_number.startswith(DRAFT_PAY_PENDING_PREFIX)
    assert draft.user_id == pay_ref.get("invoiceId")
    assert draft.registration_number == base_reg_num
    reg_json = new_reg.reg_json
    assert reg_json.get("paymentPending")
    assert reg_json["payment"] == pay_ref
    assert reg_json.get("accountId") == account_id
    assert reg_json.get("username") == username
    assert reg_json.get("registrationType") == reg_type
    assert reg_json.get("baseRegistrationNumber") == base_reg_num
    test_reg: Registration = Registration.find_by_registration_number(base_reg_num, account_id, True)
    assert test_reg.ver_bypassed == cc_payment_utils.REG_STATUS_LOCKED


@pytest.mark.parametrize('draft_json,reg_num,fs_id,reg_class,invoice_id', TEST_REGISTRATION_DATA)
def test_create_registration(session, draft_json, reg_num, fs_id, reg_class, invoice_id):
    """Assert that creating a new cc payment registration from a callback works as expected."""
    json_data = setup_registration(draft_json, reg_class, invoice_id)
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
    draft: Draft = Draft.find_by_invoice_id(invoice_id)
    assert draft
    if model_utils.REG_CLASS_PPSA == reg_class:
        statement = cc_payment_utils.create_new_statement(draft)
        assert statement.id
        new_reg = statement.registration[0]
    else:
        statement = FinancingStatement.find_by_registration_number(
                draft.registration_number, draft.account_id, True, True
            )
        assert statement
        new_reg = cc_payment_utils.create_change_registration(draft, statement)
        assert new_reg.base_registration_num == reg_num
    assert new_reg.id
    assert new_reg.registration_num


def setup_registration(draft_json: dict, reg_class: str, invoice_id: str) -> dict:
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
    else:
        del json_data['createDateTime']
        del json_data['renewalRegistrationNumber']
        del json_data['payment']
        del json_data['courtOrderInformation']
    if "documentId" in json_data:
        del json_data["documentId"]
    pay_ref: dict = copy.deepcopy(CC_PAYREF)
    if invoice_id:
        pay_ref["invoiceId"] = invoice_id
    json_data = setup_cc_draft(json_data, pay_ref, account_id, "ppr_staff")
    return json_data


def is_ci_testing() -> bool:
    """Check unit test environment: exclude most reports for CI testing."""
    return  current_app.config.get("DEPLOYMENT_ENV", "testing") == "testing"
