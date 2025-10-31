# Copyright © 2022 Province of British Columbia
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
import json
from http import HTTPStatus

# Don't need GCP tokens until completetly off of OpenShift
# import google.auth.transport.requests
# import google.oauth2.id_token
import requests
from flask import current_app

from mhr_api.models import EventTracking
from mhr_api.services.payment.client import SBCPaymentClient
from mhr_api.utils.logging import logger

EMAIL_DATA_TEMPLATE = {"recipients": "", "content": {"subject": "", "body": ""}}
EVENT_KEY_NOTIFY_REVIEW: int = 98000001
NOTIFY_REVIEW_CONFIG: str = "NOTIFY_REVIEW_CONFIG"


class Notify:
    """Notify calls the GCNotify service."""

    def __init__(self, **kwargs):
        """Create the notify service."""
        if kwargs:
            self.setup(**kwargs)

    def setup(self, **kwargs):
        """Configure the minimum properties required for notify to work."""
        self.notify_url = kwargs.get("url")
        notify_review_var: str = current_app.config.get(NOTIFY_REVIEW_CONFIG, None)
        if notify_review_var:
            self.notify_review_config = json.loads(notify_review_var)
            if not self.notify_url:
                self.notify_url = self.notify_review_config.get("url")
        else:
            self.notify_review_config = None

    def send_email(self, payload: dict, track: bool = False) -> HTTPStatus:
        """Create and send the email payload to the Notify service."""
        # auth_req = google.auth.transport.requests.Request()
        # id_token = google.oauth2.id_token.fetch_id_token(auth_req, self.notify_url)
        id_token = SBCPaymentClient.get_sa_token()  # Use the PPR/MHR service account to create a JWT.
        # logger.info(f"Sending to url {self.notify_url} with token {id_token}")
        logger.info(json.dumps(payload))
        headers = {"Authorization": "Bearer " + id_token, "Content-Type": "application/json"}
        res = requests.post(url=self.notify_url, headers=headers, json=payload, timeout=30.0)
        if track:
            if res.status_code == HTTPStatus.OK or not res.text:
                EventTracking.create(
                    EVENT_KEY_NOTIFY_REVIEW,
                    EventTracking.EventTrackingTypes.EMAIL,
                    res.status_code,
                    json.dumps(payload),
                )
            else:
                logger.warning(f"Notify response not OK: {res.text}")
                EventTracking.create(
                    EVENT_KEY_NOTIFY_REVIEW, EventTracking.EventTrackingTypes.EMAIL, res.status_code, res.text
                )
        return res.status_code

    def send_review_declined(self, reg_data: dict, reason: str) -> HTTPStatus:
        """Send a Staff review declined email to the registering party email address."""
        mhr_number: str = reg_data.get("mhrNumber")
        if not self.notify_review_config or not self.notify_review_config.get("bodyDecline"):
            msg: str = f"Configuration not set up: sending declined staff review email skipped for {mhr_number}."
            logger.warning(msg)
            EventTracking.create(
                EVENT_KEY_NOTIFY_REVIEW, EventTracking.EventTrackingTypes.EMAIL, HTTPStatus.SERVICE_UNAVAILABLE, msg
            )
            return HTTPStatus.SERVICE_UNAVAILABLE
        recipient: str = None
        if reg_data.get("submittingParty") and reg_data["submittingParty"].get("emailAddress"):
            recipient = reg_data["submittingParty"].get("emailAddress")
        if not recipient:
            msg: str = f"No submitting party email for staff review of {mhr_number}: sending declined email skipped."
            logger.warning(msg)
            EventTracking.create(
                EVENT_KEY_NOTIFY_REVIEW, EventTracking.EventTrackingTypes.EMAIL, HTTPStatus.BAD_REQUEST, msg
            )
            return HTTPStatus.BAD_REQUEST
        doc_desc: str = reg_data.get("documentDescription")
        if doc_desc:
            doc_desc = doc_desc.title()
        subject: str = str(self.notify_review_config.get("subjectDecline")).format(mhr_number=mhr_number)
        invoice_id: str = reg_data["payment"].get("invoiceId")
        body: str = str(self.notify_review_config.get("bodyDecline")).format(
            reg_type=doc_desc, mhr_number=mhr_number, reason=reason, invoice_id=invoice_id
        )
        body = body.replace("$", "\n")
        payload = copy.deepcopy(EMAIL_DATA_TEMPLATE)
        payload["recipients"] = recipient
        payload["content"]["subject"] = subject
        payload["content"]["body"] = body
        status_code = self.send_email(payload, True)
        logger.info(f"Review declined email sent to {self.notify_url} response status code={status_code}")
        return status_code

    def send_review_approved(self, reg_data: dict, verification_url: str) -> HTTPStatus:
        """Send a Staff review approved email to the registering party email address."""
        mhr_number: str = reg_data.get("mhrNumber")
        if not self.notify_review_config or not self.notify_review_config.get("bodyApprove"):
            msg: str = f"Configuration not set up: sending approved staff review email skipped for {mhr_number}."
            logger.warning(msg)
            EventTracking.create(
                EVENT_KEY_NOTIFY_REVIEW, EventTracking.EventTrackingTypes.EMAIL, HTTPStatus.SERVICE_UNAVAILABLE, msg
            )
            return HTTPStatus.SERVICE_UNAVAILABLE
        recipient: str = None
        if reg_data.get("submittingParty") and reg_data["submittingParty"].get("emailAddress"):
            recipient = reg_data["submittingParty"].get("emailAddress")
        if not recipient:
            msg: str = f"No submitting party email for staff review of {mhr_number}: sending approved email skipped."
            logger.warning(msg)
            EventTracking.create(
                EVENT_KEY_NOTIFY_REVIEW, EventTracking.EventTrackingTypes.EMAIL, HTTPStatus.BAD_REQUEST, msg
            )
            return HTTPStatus.BAD_REQUEST
        doc_desc: str = reg_data.get("documentDescription")
        if doc_desc:
            doc_desc = doc_desc.title()
        subject: str = str(self.notify_review_config.get("subjectApprove")).format(mhr_number=mhr_number)
        body: str = str(self.notify_review_config.get("bodyApprove")).format(
            reg_type=doc_desc, mhr_number=mhr_number, verification_url=verification_url
        )
        body = body.replace("$", "\n")
        payload = copy.deepcopy(EMAIL_DATA_TEMPLATE)
        payload["recipients"] = recipient
        payload["content"]["subject"] = subject
        payload["content"]["body"] = body
        status_code = self.send_email(payload, True)
        logger.info(f"Review approved email sent to {self.notify_url} response status code={status_code}")
        return status_code

    @staticmethod
    def is_staff_review_configured() -> bool:
        """Allow caller to verify staff review notifications are enabled."""
        return current_app.config.get(NOTIFY_REVIEW_CONFIG, "") != ""
