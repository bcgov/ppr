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
from ppr_api.callback.document_storage.storage_service import DocumentTypes, GoogleStorageService


TEST_DOC_NAME = 'financing-statements_100348B.pdf'
TEST_DATAFILE = 'tests/unit/callback/financing-statements_100348B.pdf'
TEST_SAVE_DOC_NAME = 'search-results-report-200000008.pdf'
TEST_VERIFICATION_DOC_NAME = 'verification-mail-discharge-example.pdf'
TEST_VERIFICATION_DATAFILE = 'tests/unit/callback/verification-mail-discharge-example.pdf'
TEST_VERIFICATION_SAVE_DOC_NAME = 'PPRVER.999999.111111.04.01.2022.PDF'
TEST_REGISTRATION_DOC_NAME = '2022/02/financing-200000000-TEST0001.pdf'
TEST_REGISTRATION_DATAFILE = 'tests/unit/callback/ut-financing-200000000-TEST0001.pdf'
TEST_REGISTRATION_SAVE_DOC_NAME = '2022/02/16/ut-verification-financing.pdf'


def test_cs_get_document(session):
    """Assert that getting a document from google cloud storage works as expected."""
    raw_data = GoogleStorageService.get_document(TEST_DOC_NAME)
    assert raw_data
    assert len(raw_data) > 0
    with open(TEST_DATAFILE, "wb") as pdf_file:
        pdf_file.write(raw_data)
        pdf_file.close()


def test_cs_save_document(session):
    """Assert that saving a document to google cloud storage works as expected."""
    raw_data = None
    with open(TEST_DATAFILE, 'rb') as data_file:
        raw_data = data_file.read()
        data_file.close()

    response = GoogleStorageService.save_document(TEST_SAVE_DOC_NAME, raw_data)
    print(response)
    assert response
    assert response['name'] == TEST_SAVE_DOC_NAME


def test_cs_get_verification_document(session):
    """Assert that getting a mail verification statement document from google cloud storage works as expected."""
    raw_data = GoogleStorageService.get_document(TEST_VERIFICATION_DOC_NAME, DocumentTypes.VERIFICATION_MAIL)
    assert raw_data
    assert len(raw_data) > 0
    with open(TEST_VERIFICATION_DATAFILE, "wb") as pdf_file:
        pdf_file.write(raw_data)
        pdf_file.close()


def test_cs_save_verification_document(session):
    """Assert that saving a mail verification statement document to google cloud storage works as expected."""
    raw_data = None
    with open(TEST_VERIFICATION_DATAFILE, 'rb') as data_file:
        raw_data = data_file.read()
        data_file.close()

    response = GoogleStorageService.save_document(TEST_VERIFICATION_SAVE_DOC_NAME, raw_data,
                                                  DocumentTypes.VERIFICATION_MAIL)
    print(response)
    assert response
    assert response['name'] == TEST_VERIFICATION_SAVE_DOC_NAME


def test_cs_get_registration_document(session):
    """Assert that getting a registration verification statement from google cloud storage works as expected."""
    raw_data = GoogleStorageService.get_document(TEST_REGISTRATION_DOC_NAME, DocumentTypes.REGISTRATION)
    assert raw_data
    assert len(raw_data) > 0
    with open(TEST_REGISTRATION_DATAFILE, "wb") as pdf_file:
        pdf_file.write(raw_data)
        pdf_file.close()


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
    assert response['name'] == TEST_REGISTRATION_SAVE_DOC_NAME
