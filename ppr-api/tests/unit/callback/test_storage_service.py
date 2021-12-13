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
from ppr_api.callback.document_storage.storage_service import GoogleStorageService


TEST_DOC_NAME = 'financing-statements_100348B.pdf'
TEST_DATAFILE = 'tests/unit/callback/financing-statements_100348B.pdf'
TEST_SAVE_DOC_NAME = 'search-results-report-200000008.pdf'


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
