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

"""Tests to assure the MHR Type Table Models.

Test-Suite to ensure that the MHR Type Table Models are working as expected.
"""

from mhr_api.models import type_tables

import pytest


# testdata pattern is ({result_count}, {model_class}, {enum_class})
TEST_TYPE_TABLES = [
    (4, type_tables.MhrNoteStatusType, type_tables.MhrNoteStatusTypes),
    (3, type_tables.MhrOwnerStatusType, type_tables.MhrOwnerStatusTypes),
    (4, type_tables.MhrRegistrationStatusType, type_tables.MhrRegistrationStatusTypes),
    (3, type_tables.MhrStatusType, type_tables.MhrStatusTypes)
]


@pytest.mark.parametrize('result_count, model_class, enum_class', TEST_TYPE_TABLES)
def test_status_find_all(session, result_count, model_class, enum_class):
    """Assert that MHR status type tables find_all() method contains all expected elements."""
    results = model_class.find_all()
    assert results
    assert len(results) == result_count
    for result in results:
        assert result.status_type in enum_class
        assert result.status_type_desc
        assert result.legacy_status_type


def test_mhr_tenancy_type(session):
    """Assert that MhrTenancyType.find_all() contains all expected elements."""
    results = type_tables.MhrTenancyType.find_all()
    assert results
    assert len(results) == 4
    for result in results:
        assert result.tenancy_type in type_tables.MhrTenancyTypes
        assert result.tenancy_type_desc
        if result.tenancy_type != type_tables.MhrTenancyTypes.NA:
            assert result.legacy_tenancy_type


def test_mhr_registration_type(session):
    """Assert that MhrRegistrationType.find_all() contains all expected elements."""
    results = type_tables.MhrRegistrationType.find_all()
    assert results
    assert len(results) >= 1
    for result in results:
        assert result.registration_type in type_tables.MhrRegistrationTypes
        assert result.registration_type_desc
        assert result.legacy_registration_type


def test_mhr_party_type(session):
    """Assert that MhrPartyType.find_all() contains all expected elements."""
    results = type_tables.MhrPartyType.find_all()
    assert results
    assert len(results) == 7
    for result in results:
        assert result.party_type in type_tables.MhrPartyTypes
        assert result.party_type_desc


def test_mhr_document_type(session):
    """Assert that MhrDocumentType.find_all() and find_by_doc_type() contains all expected elements."""
    results = type_tables.MhrDocumentType.find_all()
    assert results
    assert len(results) >= 55
    for result in results:
        assert result.document_type in type_tables.MhrDocumentTypes
        assert result.document_type_desc

    doc_result = type_tables.MhrDocumentType.find_by_doc_type(type_tables.MhrDocumentTypes.REG_101.value)
    assert doc_result
    assert doc_result.document_type == type_tables.MhrDocumentTypes.REG_101.value
    assert doc_result.document_type_desc == 'MANUFACTURED HOME REGISTRATION'
    assert doc_result.legacy_fee_code == 'MHR400'
    doc_result = type_tables.MhrDocumentType.find_by_doc_type('XXX')
    assert not doc_result


def test_mhr_location_type(session):
    """Assert that MhrLocationType.find_all() contains all expected elements."""
    results = type_tables.MhrLocationType.find_all()
    assert results
    assert len(results) >= 5
    for result in results:
        assert result.location_type in type_tables.MhrLocationTypes
        assert result.location_type_desc
