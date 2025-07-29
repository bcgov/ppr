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

"""Tests to verify the search history endpoint.

Test-Suite to ensure that the /search-history endpoint is working as expected.
"""

from http import HTTPStatus

import pytest

from ppr_api.services.authz import COLIN_ROLE, PPR_ROLE, STAFF_ROLE
from tests.unit.services.utils import create_header_account, create_header


# testdata pattern is ({desc}, {roles}, {status}, {account}, {from_ui}, {page_num}, {has_results})
TEST_GET_DATA = [
    ("Missing account", [PPR_ROLE], HTTPStatus.BAD_REQUEST, None, None, None, False),
    ("Missing account staff", [PPR_ROLE, STAFF_ROLE], HTTPStatus.BAD_REQUEST, None, None, None, False),
    ("Invalid role", [COLIN_ROLE], HTTPStatus.UNAUTHORIZED, "PS12345", None, None, False),
    ("Valid", [PPR_ROLE], HTTPStatus.OK, "PS12345", None, None, True),
    ("Valid from UI", [PPR_ROLE], HTTPStatus.OK, "PS12345", True, None, True),
    ("Valid from UI page num", [PPR_ROLE], HTTPStatus.OK, "PS12345", True, 1, True),
    ("Valid no results", [PPR_ROLE], HTTPStatus.OK, "PS12345", None, 2, False),
]


@pytest.mark.parametrize('desc,roles,status,account, from_ui, page_num, has_results', TEST_GET_DATA)
def test_get_search_history(session, client, jwt, desc, roles, status, account, from_ui, page_num, has_results):
    """Assert that account get search history works as expected."""
    headers = None
    if account:
        headers = create_header_account(jwt, roles, 'test-user', account)
    else:
        headers = create_header(jwt, roles)
    path = "/api/v1/search-history"
    if from_ui:
        path += "?fromUI=true"
        if page_num:
            path += f"&pageNumber={page_num}"
    elif page_num:
        path += f"?pageNumber={page_num}"
    # test
    rv = client.get(path, headers=headers)
    # check
    assert rv.status_code == status
    if status == HTTPStatus.OK:
        if has_results:
            assert rv.json
        else:
            assert not rv.json
