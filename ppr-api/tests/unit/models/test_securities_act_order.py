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

"""Tests to assure the SecuritiesActOrder Model.

Test-Suite to ensure that the SecuritiesActOrder Model is working as expected.
"""
import pytest

from ppr_api.models import SecuritiesActOrder, utils as model_utils


# testdata pattern is ({description}, {exists}, {order_id}, {name}, {registry}, {file}, {effect}, {order_ind})
TEST_DATA_ID = [
    ('Exists', True, 200000000, 'COURT NAME', 'COURT REGISTRY', 'FILE# 00001', 'UNIT TEST', 'Y'),
    ('Does not exist', False, 300000000, None, None, None, None, None)
]
# testdata pattern is ({description}, {exists}, {notice_id}, {name}, {registry}, {file}, {effect}, {order_ind})
TEST_DATA_NOTICE_ID = [
    ('Exists', True, 200000000, 'COURT NAME', 'COURT REGISTRY', 'FILE# 00001', 'UNIT TEST', 'Y'),
    ('Does not exist', False, 300000000, None, None, None, None, None)
]


@pytest.mark.parametrize('desc,exists,order_id,name,registry,file,effect,order_ind', TEST_DATA_ID)
def test_find_by_id(session, desc, exists, order_id, name, registry, file, effect, order_ind):
    """Assert that find securities act order by id contains all expected elements."""
    order: SecuritiesActOrder = SecuritiesActOrder.find_by_id(order_id)
    if exists:
        assert order
        assert order.id == order_id
        assert order.securities_act_notice_id
        assert order.registration_id
        assert order.court_name == name
        assert order.court_registry == registry
        assert order.order_date
        assert order.file_number == file
        assert order.effect_of_order == effect
        assert order.court_order_ind == order_ind
        order_json = order.json
        assert order_json.get('courtOrder')
        assert order_json.get('orderDate')
        assert order_json.get('courtName') == name
        assert order_json.get('courtRegistry') == registry
        assert order_json.get('fileNumber') == file
        assert order_json.get('effectOfOrder') == effect
    else:
        assert not order


@pytest.mark.parametrize('desc,exists,notice_id,name,registry,file,effect,order_ind', TEST_DATA_NOTICE_ID)
def test_find_by_notice_id(session, desc, exists, notice_id, name, registry, file, effect, order_ind):
    """Assert that find securities act order by notice id contains all expected elements."""
    orders = SecuritiesActOrder.find_by_notice_id(notice_id)
    if exists:
        assert orders
        assert orders[0].id
        assert orders[0].securities_act_notice_id == notice_id
        assert orders[0].registration_id
        assert orders[0].court_name == name
        assert orders[0].court_registry == registry
        assert orders[0].order_date
        assert orders[0].file_number == file
        assert orders[0].effect_of_order == effect
        assert orders[0].court_order_ind == order_ind
        order_json = orders[0].json
        assert order_json.get('courtOrder')
        assert order_json.get('orderDate')
        assert order_json.get('courtName') == name
        assert order_json.get('courtRegistry') == registry
        assert order_json.get('fileNumber') == file
        assert order_json.get('effectOfOrder') == effect
    else:
        assert not orders


def test_securities_act_json(session):
    """Assert that the securities act model renders to a json format correctly."""
    now = model_utils.now_ts()
    name = 'name'
    registry = 'registry'
    file = 'file'
    effect = 'effect'
    order = SecuritiesActOrder(
        id=10001,
        securities_act_notice_id=10001,
        court_order_ind='Y',
        court_name=name,
        order_date = now,
        court_registry = registry,
        file_number=file,
        effect_of_order=effect
    )

    order_json = {
        'courtOrder': True,
        'courtName': name,
        'courtRegistry': registry,
        'fileNumber': file,
        'orderDate': model_utils.format_ts(now),
        'effectOfOrder': effect
    }
    assert order.json == order_json
