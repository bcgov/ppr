# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
"""Merge individual secured party notification reports into a single batch report."""
from http import HTTPStatus

import requests

from secured_party_notification.config import Config
from secured_party_notification.services.gcp_auth.auth_service import GoogleAuthService
from secured_party_notification.utils.logging import logger

MERGE_URI = "/forms/pdfengines/merge"
RS_TIMEOUT = 1800.0


class Report:  # pylint: disable=too-few-public-methods
    """Service to create report outputs."""

    GCP_TOKEN = None
    HEADER_AUTH = None
    MERGE_URL = None

    @staticmethod
    def init_app(config: Config):
        """Set up the service"""
        Report.GCP_TOKEN = GoogleAuthService.get_report_api_token()
        Report.HEADER_AUTH = "Bearer {}".format(Report.GCP_TOKEN)
        Report.MERGE_URL = config.REPORT_API_URL + MERGE_URI

    @staticmethod
    def get_headers() -> dict:
        """Build the report service request headers."""
        headers = {"Authorization": Report.HEADER_AUTH}
        return headers

    @staticmethod
    def batch_merge(pdf_list: dict):
        """Merge a list of pdf files into a single pdf."""
        if not pdf_list:
            return None
        logger.debug(f"Setting up batch merge for {len(pdf_list)} files.")
        count: int = 0
        files = {}
        for pdf in pdf_list:
            count += 1
            filename = "file" + str(count) + ".pdf"
            files[filename] = pdf
        headers = Report.get_headers()
        response = requests.post(url=Report.MERGE_URL, headers=headers, files=files, timeout=RS_TIMEOUT)
        logger.debug(f"Batch merge reports response status: {response.status_code}.")
        if response.status_code != HTTPStatus.OK:
            content = response.content.decode("ascii")
            logger.error(f"Batch merge response status: {response.status_code} error: {content}.")
        return response.content, response.status_code
