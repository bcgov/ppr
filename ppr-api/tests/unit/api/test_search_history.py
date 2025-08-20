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
from ppr_api.utils.logging import logger
from tests.unit.services.utils import create_header_account, create_header

FILTER_TYPE: str = "?type=REGISTRATION_NUMBER&sortCriteriaName=type&sortDirection=ascending"
FILTER_CLIENT_REF: str = "?clientReferenceId=UT-SQ-RG-001&sortCriteriaName=clientReferenceId&sortDirection=descending"
FILTER_USERNAME: str = "?fromUI=true&username=BOB&sortCriteriaName=username&sortDirection=ascending"
FILTER_DATE: str = "?startDateTime=2025-08-01&endDateTime=2025-08-14&sortCriteriaName=searchDateTime"
FILTER_IS_CRITERIA: str = "?type=INDIVIDUAL_DEBTOR&criteria=IND TEST"
FILTER_MI_CRITERIA: str = "?type=MHR_OWNER_NAME&criteria=TEST&sortCriteriaName=criteria"

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
# testdata pattern is ({desc}, {roles}, {status}, {account}, {page_num}, {has_results}, {params})
TEST_GET_DATA_FILTER = [
    ("Filter by search type", [PPR_ROLE], HTTPStatus.OK, "PS12345", None, True, FILTER_TYPE),
    ("Filter by client ref", [PPR_ROLE], HTTPStatus.OK, "PS12345", None, True, FILTER_CLIENT_REF),
    ("Filter by username", [PPR_ROLE], HTTPStatus.OK, "PS12345", None, False, FILTER_USERNAME),
    ("Filter by date", [PPR_ROLE], HTTPStatus.OK, "PS12345", None, False, FILTER_DATE),
    ("Filter by IS both names", [PPR_ROLE], HTTPStatus.OK, "PS12345", None, False, FILTER_IS_CRITERIA),
    ("Filter by MI last name", [PPR_ROLE], HTTPStatus.OK, "PS12345", None, False, FILTER_MI_CRITERIA),
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


@pytest.mark.parametrize('desc,roles,status,account,page_num,has_results,params', TEST_GET_DATA_FILTER)
def test_get_search_history_filter(session, client, jwt, desc, roles, status, account, page_num, has_results, params):
    """Assert that account get search history with filtering and sorting works as expected."""
    headers = None
    if account:
        headers = create_header_account(jwt, roles, 'test-user', account)
    else:
        headers = create_header(jwt, roles)
    path = "/api/v1/search-history" + params
    if page_num:
        path += f"&pageNumber={page_num}"
    # test
    rv = client.get(path, headers=headers)
    # check
    assert rv.status_code == status
    if status == HTTPStatus.OK:
        if has_results:
            # logger.info(rv.json)
            assert rv.json
        else:
            assert not rv.json
