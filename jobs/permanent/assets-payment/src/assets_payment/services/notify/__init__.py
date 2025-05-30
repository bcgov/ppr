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
# Don't need GCP tokens until completetly off of OpenShift
# import google.auth.transport.requests
# import google.oauth2.id_token
import copy
from http import HTTPStatus

import requests

from assets_payment.config import Config
from assets_payment.utils.logging import logger

EMAIL_DATA_TEMPLATE = {"recipients": "", "content": {"subject": "", "body": ""}}
STATUS_ERROR_BODY = "Job failed with error {err_msg}."


class Notify:
    """Notify calls the GCNotify service."""

    def __init__(self, config: Config, jwt: str):
        """Create the notify service."""
        self.notify_url: str = config.NOTIFY_SVC_URL
        self.status_recipients: str = config.NOTIFY_STATUS_RECIPIENTS
        self.status_subject: str = config.NOTIFY_STATUS_SUBJECT
        self.status_body: str = config.NOTIFY_STATUS_BODY
        self.jwt = jwt

    def send_status(self, status_data: dict) -> HTTPStatus:
        """Send a job status email."""
        body: str = self.status_body.format(
            ppr_complete=status_data.get("ppr_complete"),
            ppr_errors=status_data.get("ppr_errors"),
            ppr_expired=status_data.get("ppr_expired"),
            mhr_complete=status_data.get("mhr_complete"),
            mhr_errors=status_data.get("mhr_errors"),
            mhr_expired=status_data.get("mhr_expired"),
        )
        body = body.replace("$", "\n")
        if status_data.get("mhr_invoice_ids"):
            body += "\n\nMHR cancelled invoices:\n" + status_data.get("mhr_invoice_ids")
        else:
            body += "\n\nMHR cancelled invoices: none"
        if status_data.get("mhr_draft_ids"):
            body += "\n\nMHR updated draft IDs:\n" + status_data.get("mhr_draft_ids")
        else:
            body += "\n\nMHR updated draft IDs: none"
        if status_data.get("ppr_invoice_ids"):
            body += "\n\nPPR cancelled invoices:\n" + status_data.get("ppr_invoice_ids")
        else:
            body += "\n\nPPR cancelled invoices: none"
        if status_data.get("ppr_draft_ids"):
            body += "\n\nPPR updated draft IDs:\n" + status_data.get("ppr_draft_ids")
        else:
            body += "\n\nPPR updated draft IDs: none"
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
