# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Google Storage token tests."""
from mhr_api.services.document_storage.storage_service import DocumentTypes, GoogleStorageService


TEST_DOC_NAME = 'test_search_doc.pdf'
TEST_DATAFILE = 'tests/unit/services/test_search_doc.pdf'
TEST_SAVE_DOC_NAME = '2022/05/06/search-results-report-ut-001.pdf'
TEST_SAVE_DOC_NAME2 = '2022/05/06/search-results-report-ut-002.pdf'
TEST_REGISTRATION_DOC_NAME = 'test_reg_doc.pdf'
TEST_REGISTRATION_DATAFILE = 'tests/unit/services/test_reg_doc.pdf'
TEST_REGISTRATION_SAVE_DOC_NAME = '2022/05/06/registration-ut-001.pdf'


def test_cs_save_search_document_http(session):
    """Assert that saving a search bucket document to google cloud storage works as expected."""
    raw_data = None
    with open(TEST_DATAFILE, 'rb') as data_file:
        raw_data = data_file.read()
        data_file.close()

    response = GoogleStorageService.save_document_http(TEST_SAVE_DOC_NAME, raw_data)
    print(response)
    assert response
    assert response['name'] == TEST_SAVE_DOC_NAME


def test_cs_save_search_document(session):
    """Assert that saving a search bucket document to google cloud storage works as expected."""
    raw_data = None
    with open(TEST_DATAFILE, 'rb') as data_file:
        raw_data = data_file.read()
        data_file.close()

    response = GoogleStorageService.save_document(TEST_SAVE_DOC_NAME2, raw_data)
    assert response


def test_cs_save_registration_document(session):
    """Assert that saving a registration verification statement to google cloud storage works as expected."""
    raw_data = None
    with open(TEST_REGISTRATION_DATAFILE, 'rb') as data_file:
        raw_data = data_file.read()
        data_file.close()

    response = GoogleStorageService.save_document(TEST_REGISTRATION_SAVE_DOC_NAME, raw_data,
                                                  DocumentTypes.REGISTRATION)
    print(response)
    assert response


def test_cs_get_search_document_http(session):
    """Assert that getting a search bucket document from google cloud storage works as expected."""
    raw_data = GoogleStorageService.get_document_http(TEST_SAVE_DOC_NAME)
    assert raw_data
    assert len(raw_data) > 0
    with open(TEST_DATAFILE, "wb") as pdf_file:
        pdf_file.write(raw_data)
        pdf_file.close()


def test_cs_get_search_document(session):
    """Assert that getting a search bucket document from google cloud storage works as expected."""
    raw_data = GoogleStorageService.get_document(TEST_SAVE_DOC_NAME2, DocumentTypes.SEARCH_RESULTS)
    assert raw_data
    assert len(raw_data) > 0
    with open(TEST_DATAFILE, "wb") as pdf_file:
        pdf_file.write(raw_data)
        pdf_file.close()


def test_cs_get_registration_document(session):
    """Assert that getting a registration verification statement from google cloud storage works as expected."""
    raw_data = GoogleStorageService.get_document(TEST_REGISTRATION_SAVE_DOC_NAME, DocumentTypes.REGISTRATION)
    assert raw_data
    assert len(raw_data) > 0
    with open(TEST_REGISTRATION_DATAFILE, "wb") as pdf_file:
        pdf_file.write(raw_data)
        pdf_file.close()


def test_cs_delete_search_document(session):
    """Assert that deleting a search bucket document from google cloud storage works as expected."""
    response = GoogleStorageService.delete_document(TEST_SAVE_DOC_NAME2, DocumentTypes.SEARCH_RESULTS)
    assert response
