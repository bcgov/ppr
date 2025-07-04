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

"""Tests to assure the ClientCode Model.

Test-Suite to ensure that the ClientCode Model is working as expected.
"""
import copy
import pytest

from ppr_api.models import Address, ClientCode, ClientCodeRegistration, utils as model_utils
from ppr_api.models.type_tables import ClientCodeTypes
from ppr_api.utils.logging import logger


TEST_CODE_NEW =   {
    "accountId": "1234",
    "businessName": "PETERBILT TRUCKS PACIFIC INC.",
    "address": {
      "street": "1079 DOUGLAS ST",
      "city": "VICTORIA",
      "region": "BC",
      "country": "CA",
      "postalCode": "V8W 2C5"
    },
    "emailAddress": "test-1@test-ptc.com",
    "contact": {
      "name": "EXAMPLE CONTACT 1",
      "areaCode": "250",
      "phoneNumber": "3564500"
    }
}
TEST_CODE_NEW_BRANCH =   {
    "accountId": "1234",
    "businessName": "PETERBILT TRUCKS PACIFIC INC. - BRANCH 1",
    "address": {
      "street": "1234 JAMES ST",
      "city": "SAANICH",
      "region": "BC",
      "country": "CA",
      "postalCode": "V8X 1D3"
    },
    "emailAddress": "test-2@test-ptc.com",
    "contact": {
      "name": "EXAMPLE CONTACT 2",
      "areaCode": "250",
      "phoneNumber": "3564501"
    }
}

# testdata pattern is ({description}, {exists}, {reg_id})
TEST_DATA_REG_ID = [
    ('Exists', True, 200000100),
    ('Does not exist', False, 300012345)
]
# testdata pattern is ({code}, {head_code}, {reg_id}, {new_name})
TEST_DATA_NAME_CHANGE = [
    ('99990001', '9999', 200000101, 'TEST NAME CHANGE'),
]


@pytest.mark.parametrize('desc,exists,reg_id', TEST_DATA_REG_ID)
def test_find_by_id(session, desc, exists, reg_id):
    """Assert that find client party code registration by id works as expected."""
    if exists:
        reg: ClientCodeRegistration = ClientCodeRegistration(id=reg_id,
                                                             user_id='TEST123',
                                                             create_ts=model_utils.now_ts(),
                                                             request_data=TEST_CODE_NEW,
                                                             client_code_type=ClientCodeTypes.CREATE_CODE)
        reg.save()
    test_reg: ClientCodeRegistration = ClientCodeRegistration.find_by_id(reg_id)
    if exists:
        assert test_reg
        assert test_reg.id == reg_id
        assert test_reg.create_ts
        assert test_reg.client_code_type == ClientCodeTypes.CREATE_CODE
        assert test_reg.user_id == 'TEST123'
        assert test_reg.request_data
        assert not test_reg.pay_invoice_id
        assert not test_reg.pay_path
        assert not test_reg.previous_registration_id
    else:
        assert not test_reg


def test_client_code_registration_json(session):
    """Assert that the client party model renders to a json format correctly."""
    code: ClientCode = ClientCode(
        id=79910001,
        head_id=7991,
        name='BUSINESS NAME',
        contact_name='CONTACT',
        contact_area_cd='250',
        contact_phone_number='1234567',
        email_id='test@gmail.com',
        account_id='1234'
    )
    reg: ClientCodeRegistration = ClientCodeRegistration(id=200000100,
                                                         user_id='TEST123',
                                                         create_ts=model_utils.now_ts(),
                                                         request_data=TEST_CODE_NEW,
                                                         client_code_type=ClientCodeTypes.CREATE_CODE)
    reg.client_code = code
    code_json = {
        'code': code.format_party_code(),
        'headOfficeCode': code.format_head_office_code(),
        'accountId': '1234',
        'businessName': code.name,
        'contact': {
            'name': code.contact_name,
            'phoneNumber': code.contact_phone_number,
            'areaCode': code.contact_area_cd
        },
        'emailAddress': code.email_id
    }
    reg_json = {
        'createDateTime': model_utils.format_ts(reg.create_ts),
        'clientCodeRegistrationType': reg.client_code_type.value,
        'clientCode': code_json
    }
    assert reg.json == reg_json


def test_create_new_from_json(session):
    """Assert that creating a client party code registration from json is working correctly."""
    reg: ClientCodeRegistration = ClientCodeRegistration.create_new_from_json(TEST_CODE_NEW,
                                                                              TEST_CODE_NEW.get("accountId"),
                                                                              "TEST-USER")
    reg.save()
    assert reg.id
    assert reg.create_ts
    assert reg.client_code_type == ClientCodeTypes.CREATE_CODE
    assert reg.user_id == 'TEST-USER'
    assert reg.request_data
    assert not reg.pay_invoice_id
    assert not reg.pay_path
    assert not reg.previous_registration_id
    assert reg.client_code
    code: ClientCode = reg.client_code
    assert code.id
    assert code.head_id
    assert code.account_id == TEST_CODE_NEW.get("accountId")
    assert code.name == TEST_CODE_NEW.get("businessName")
    assert code.email_id == TEST_CODE_NEW.get("emailAddress")
    assert code.contact_name == TEST_CODE_NEW["contact"].get("name")
    assert code.contact_phone_number == TEST_CODE_NEW["contact"].get("phoneNumber")
    assert code.contact_area_cd == TEST_CODE_NEW["contact"].get("areaCode")
    assert code.address
    request_address = TEST_CODE_NEW.get("address")
    assert request_address == code.address.json
    assert code.client_code_registration_id == reg.id


def test_create_branch_from_json(session):
    """Assert that creating a client party code branch registration from json is working correctly."""
    account_id: str = TEST_CODE_NEW.get("accountId")
    user_id: str = "TEST-USER"
    reg: ClientCodeRegistration = ClientCodeRegistration.create_new_from_json(TEST_CODE_NEW, account_id, user_id)
    reg.save()
    assert reg.id
    assert reg.create_ts
    assert reg.client_code_type == ClientCodeTypes.CREATE_CODE
    assert reg.user_id == user_id
    assert reg.request_data
    assert not reg.pay_invoice_id
    assert not reg.pay_path
    assert not reg.previous_registration_id
    assert reg.client_code
    code: ClientCode = reg.client_code
    code_json = copy.deepcopy(TEST_CODE_NEW_BRANCH)
    code_json["headOfficeCode"] = code.format_head_office_code()

    reg2: ClientCodeRegistration = ClientCodeRegistration.create_new_from_json(code_json, account_id, user_id)
    assert reg2.client_code
    branch: ClientCode = reg2.client_code
    branch.save()
    # logger.info(f"saved address {address.json}")
    assert branch.id
    assert code.head_id == branch.head_id
    assert branch.account_id == TEST_CODE_NEW_BRANCH.get("accountId")
    assert branch.name == TEST_CODE_NEW_BRANCH.get("businessName")
    assert branch.email_id == TEST_CODE_NEW_BRANCH.get("emailAddress")
    assert branch.contact_name == TEST_CODE_NEW_BRANCH["contact"].get("name")
    assert branch.contact_phone_number == TEST_CODE_NEW_BRANCH["contact"].get("phoneNumber")
    assert branch.contact_area_cd == TEST_CODE_NEW_BRANCH["contact"].get("areaCode")
    assert branch.address
    request_address = TEST_CODE_NEW_BRANCH.get("address")
    assert request_address == branch.address.json
    assert branch.client_code_registration_id == reg2.id


@pytest.mark.parametrize('code,head_code,reg_id,new_name', TEST_DATA_NAME_CHANGE)
def test_create_name_change_from_json(session, code, head_code, reg_id, new_name):
    """Assert that creating a client party code name changeregistration from json is working correctly."""
    user_id: str = "TEST-USER"
    client_code: ClientCode = ClientCode.find_by_code(code, False)
    test_json = {
        "code": code,
        "headOfficeCode": head_code,
        "businessName": new_name
    }
    reg: ClientCodeRegistration = ClientCodeRegistration.create_name_change_from_json(test_json, user_id, client_code)
    reg.id = reg_id
    reg.save()
    assert reg.id
    assert reg.create_ts
    assert reg.client_code_type == ClientCodeTypes.CHANGE_NAME
    assert reg.user_id == user_id
    assert reg.request_data
    assert not reg.pay_invoice_id
    assert not reg.pay_path
    assert not reg.previous_registration_id
    assert reg.client_code
