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
"""This class enqueues messages for the PPR API asynchronous events."""
import json

from flask import current_app
from google.cloud import pubsub_v1

from mhr_api.services.gcp_auth.auth_service import GoogleAuthService


class GoogleQueueService():
    """Google Pub/Sub implementation to publish/enqueue events.

    Publish aync messages for downstream processing.
    """

    def __init__(self):
        """Initialize the publisher."""
        credentials = GoogleAuthService.get_credentials()
        self.publisher = pubsub_v1.PublisherClient(credentials=credentials)
        self.project_id = str(current_app.config.get('GCP_PS_PROJECT_ID'))
        self.search_report_topic = str(current_app.config.get('GCP_PS_SEARCH_REPORT_TOPIC'))
        self.registration_report_topic = str(current_app.config.get('GCP_PS_REGISTRATION_REPORT_TOPIC'))
        self.search_report_topic_name = f'projects/{self.project_id}/topics/{self.search_report_topic}'
        self.registration_report_topic_name = f'projects/{self.project_id}/topics/{self.registration_report_topic}'

    def publish_search_report(self, payload):
        """Publish the search report request json payload to the Queue Service."""
        try:
            self.publish(self.search_report_topic_name, payload)
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            current_app.logger.error('Error publish_search_report: ' + str(err))
            raise err

    def publish_registration_report(self, payload):
        """Publish the API registration verification request json payload to the Queue Service."""
        try:
            self.publish(self.registration_report_topic_name, payload)
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            current_app.logger.error('Error publish_registration_report: ' + str(err))
            raise err

    def publish(self, topic_name, payload_json):
        """Publish the payload to the specified topic."""
        payload = json.dumps(payload_json).encode('utf-8')
        current_app.logger.info('Publishing topic=' + topic_name + ', payload=' + json.dumps(payload_json))
        future = self.publisher.publish(topic_name, payload)
        future.result()
