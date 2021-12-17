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
from ppr_api.services.queue_service import GoogleQueueService


TEST_PAYLOAD = {
    'searchId': 999999999
}


def test_publish_search_report(session):
    """Assert that enqueuing/publishing a search report event works as expected."""
    GoogleQueueService().publish_search_report(TEST_PAYLOAD)


def test_publish_api_notification(session):
    """Assert that enqueuing/publishing an api notification event works as expected."""
    GoogleQueueService().publish_notification(TEST_PAYLOAD)
