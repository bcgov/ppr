# Copyright © 2025 Province of British Columbia
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
"""This module contains the services used by the Delivery Service."""
import copy

# Don't need GCP tokens until completetly off of OpenShift
# import google.auth.transport.requests
# import google.oauth2.id_token
import json
from http import HTTPStatus

import requests

from secured_party_notification.config import Config
from secured_party_notification.utils.logging import logger

EMAIL_DATA_TEMPLATE = {"recipients": "", "content": {"subject": "", "body": ""}}
STATUS_ERROR_BODY = "Job failed with error {err_msg}."


class Notify:
    """Notify calls the GCNotify service to email the status of the job run."""

    def __init__(self, config: Config):
        """Create the notify service."""
        self.notify_url: str = config.NOTIFY_SVC_URL
        self.status_recipients: str = config.NOTIFY_STATUS_RECIPIENTS
        self.status_subject: str = config.NOTIFY_STATUS_SUBJECT
        self.status_body: str = config.NOTIFY_STATUS_BODY
        self.jwt = get_sa_token(config)

    def send_status(self, status_data: dict) -> HTTPStatus:
        """Send a job status email."""
        body: str = self.status_body.format(
            batch_job_id=status_data.get("batch_job_id"),
            total_count=status_data.get("total_count"),
            missing_count=status_data.get("missing_count"),
            batch_file_name=status_data.get("delivery_zip_file_name"),
            zip_file_count=status_data.get("zip_file_count"),
            zip_file_error_count=status_data.get("zip_file_error_count"),
            csv_file_url=status_data.get("csv_file_url"),
        )
        body = body.replace("$", "\n")
        payload = copy.deepcopy(EMAIL_DATA_TEMPLATE)
        payload["recipients"] = self.status_recipients
        payload["content"]["subject"] = self.status_subject
        payload["content"]["body"] = body
        logger.info(f"Sending status email {payload}")
        self.send_email(payload)

    def send_status_error(self, error_msg: str) -> HTTPStatus:
        """Send a job error status email."""
        body: str = STATUS_ERROR_BODY.format(err_msg=error_msg)
        payload = copy.deepcopy(EMAIL_DATA_TEMPLATE)
        payload["recipients"] = self.status_recipients
        payload["content"]["subject"] = self.status_subject
        payload["content"]["body"] = body
        self.send_email(payload)

    def send_email(self, payload: dict) -> HTTPStatus:
        """Create and send the email payload to the Notify service."""
        headers = {"Authorization": "Bearer " + self.jwt, "Content-Type": "application/json"}
        res = requests.post(url=self.notify_url, headers=headers, json=payload, timeout=30.0)
        logger.info(f"Email sent to {self.notify_url} response status code={res.status_code}")
        return res.status_code


def get_sa_token(config: Config):
    """Common notification service requires a Registries issued JWT. Request one from the OIDC service."""
    oidc_token_url = config.JWT_OIDC_TOKEN_URL
    client_id = config.ACCOUNT_SVC_CLIENT_ID
    client_secret = config.ACCOUNT_SVC_CLIENT_SECRET
    logger.info(f"Calling OIDC api to get token: URL = {oidc_token_url}, client_id={client_id}.")
    try:
        headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
        data = f"grant_type=client_credentials&scope=openid&client_id={client_id}&client_secret={client_secret}"
        response = requests.post(url=oidc_token_url, data=data, params=None, headers=headers, timeout=30.0)
        if not response or not response.ok:
            logger.info(f"Get SA token failed {response.status_code} {response.text}")
            return None
        response_json = json.loads(response.text)
        token = response_json["access_token"]
        logger.info("Have new sa token from OIDC.")
        return token
    except Exception as err:
        logger.error(f"get_sa_token error: {str(err)}")
        return None
