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

from google.cloud import pubsub_v1

from mhr_api.services.gcp_auth.auth_service import GoogleAuthService
from mhr_api.utils.logging import logger


class GoogleQueueService:
    """Google Pub/Sub implementation to publish/enqueue events.

    Publish aync messages for downstream processing.
    """

    publisher = None
    search_report_topic_name = None
    registration_report_topic_name = None
    doc_create_record_topic_name = None

    @staticmethod
    def init_app(app):
        """Initialize the publisher."""
        credentials = GoogleAuthService.get_credentials()
        GoogleQueueService.publisher = pubsub_v1.PublisherClient(credentials=credentials)
        project_id = str(app.config.get("GCP_PS_PROJECT_ID"))
        search_report_topic = str(app.config.get("GCP_PS_SEARCH_REPORT_TOPIC"))
        registration_report_topic = str(app.config.get("GCP_PS_REGISTRATION_REPORT_TOPIC"))
        GoogleQueueService.search_report_topic_name = f"projects/{project_id}/topics/{search_report_topic}"
        GoogleQueueService.registration_report_topic_name = f"projects/{project_id}/topics/{registration_report_topic}"
        GoogleQueueService.doc_create_record_topic_name = app.config.get("DOC_CREATE_REC_TOPIC")

    def publish_search_report(self, payload):
        """Publish the search report request json payload to the Queue Service."""
        try:
            self.publish(GoogleQueueService.search_report_topic_name, payload)
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            logger.error("Error publish_search_report: " + str(err))
            raise err

    def publish_registration_report(self, payload):
        """Publish the API registration verification request json payload to the Queue Service."""
        try:
            self.publish(GoogleQueueService.registration_report_topic_name, payload)
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            logger.error("Error publish_registration_report: " + str(err))
            raise err

    def publish_create_doc_record(self, payload):
        """Publish the DRS create document record request json payload to the Queue Service."""
        try:
            if GoogleQueueService.doc_create_record_topic_name:
                self.publish(GoogleQueueService.doc_create_record_topic_name, payload)
            else:
                logger.info("Skipping publishing of DRS create record event: topic not configured.")
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            logger.error("Error publish_create_doc_record: " + str(err))
            raise err

    def publish(self, topic_name, payload_json):
        """Publish the payload to the specified topic."""
        payload = json.dumps(payload_json).encode("utf-8")
        logger.info("Publishing topic=" + topic_name + ", payload=" + json.dumps(payload_json))
        future = GoogleQueueService.publisher.publish(topic_name, payload)
        future.result()
