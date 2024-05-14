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

"""Tests to assure the SecuritiesActNotice Model.

Test-Suite to ensure that the SecuritiesActNotice Model is working as expected.
"""
import pytest

from ppr_api.models import SecuritiesActNotice, utils as model_utils


# testdata pattern is ({description}, {exists}, {sec_act_id}, {sec_act_type}, {type_desc})
TEST_DATA_ID = [
    ('Exists', True, 200000000, 'PRESERVATION', 'PRESERVATION ORDER'),
    ('Does not exist', False, 300000000, None, None)
]
# testdata pattern is ({description}, {exists}, {id}, {sec_act_type}, {type_desc})
TEST_DATA_REG_ID = [
    ('Exists', True, 200000038, 'PRESERVATION', 'PRESERVATION ORDER'),
    ('Does not exist', False, 300000000, None, None)
]


@pytest.mark.parametrize('desc,exists,sec_act_id,sec_act_type, type_desc', TEST_DATA_ID)
def test_find_by_id(session, desc, exists, sec_act_id, sec_act_type, type_desc):
    """Assert that find securities act by id contains all expected elements."""
    sec_act: SecuritiesActNotice = SecuritiesActNotice.find_by_id(sec_act_id)
    if exists:
        assert sec_act
        assert sec_act.id == sec_act_id
        assert sec_act.registration_id
        assert sec_act.effective_ts
        assert sec_act.detail_description
        assert sec_act.securities_act_type == sec_act_type
        assert sec_act.sec_act_type
        assert sec_act.securities_act_orders
        sec_act_json = sec_act.json
        assert sec_act_json.get('securitiesActNoticeType') == sec_act_type
        assert sec_act_json.get('effectiveDateTime')
        assert sec_act_json.get('description')
        assert sec_act_json.get('registrationDescription') == type_desc
        assert sec_act_json.get('securitiesActOrders')
    else:
        assert not sec_act


@pytest.mark.parametrize('desc,exists,reg_id,sec_act_type,type_desc', TEST_DATA_REG_ID)
def test_find_by_registration_id(session, desc, exists, reg_id, sec_act_type, type_desc):
    """Assert that find securities act by registration id contains all expected elements."""
    sec_acts = SecuritiesActNotice.find_by_registration_id(reg_id)
    if exists:
        assert sec_acts
        assert sec_acts[0].registration_id == reg_id
        assert sec_acts[0].id
        assert sec_acts[0].effective_ts
        assert sec_acts[0].securities_act_type == sec_act_type
        assert sec_acts[0].sec_act_type
        assert sec_acts[0].securities_act_orders
        sec_act_json = sec_acts[0].json
        assert sec_act_json.get('securitiesActNoticeType') == sec_act_type
        assert sec_act_json.get('effectiveDateTime')
        assert sec_act_json.get('registrationDescription') == type_desc
        assert sec_act_json.get('securitiesActOrders')
    else:
        assert not sec_acts


def test_securities_act_json(session):
    """Assert that the securities act model renders to a json format correctly."""
    sec_id: int = 10001
    now = model_utils.now_ts()
    sec_act_type = 'LIEN'
    sec_act = SecuritiesActNotice(
        id=sec_id,
        securities_act_type=sec_act_type,
        effective_ts = now
    )

    sec_act_json = {
        'noticeId': sec_id,
        'securitiesActNoticeType': sec_act_type,
        'effectiveDateTime': model_utils.format_ts(now)
    }
    assert sec_act.json == sec_act_json
