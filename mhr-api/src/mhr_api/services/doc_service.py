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
"""This manages all of the BC Registries document service integration for the application: document IDlookup."""
import json

import requests
from flask import current_app

from mhr_api.utils.logging import logger

SEARCH_DOC_ID = "/searches/MHR?consumerDocumentId="


def doc_id_lookup(document_id: str, auth_header: str = None) -> dict:
    """Doc service document lookup by consumer document_id."""
    response = None
    if not document_id:
        return response
    service_url: str = current_app.config.get("DOC_SERVICE_URL")
    apikey: str = current_app.config.get("DOC_SERVICE_KEY")
    account_id = current_app.config.get("DOC_SERVICE_ACCOUNT_ID")
    if not service_url or not apikey or not account_id:
        logger.info(f"Missing required service config var url={service_url} apikey={apikey} acount={account_id}")
        return response
    api_url: str = service_url + SEARCH_DOC_ID + document_id
    try:
        headers = {"x-apikey": apikey, "Account-Id": account_id, "Content-Type": "application/json"}
        logger.info(f"Doc service document_id lookup url={api_url}")
        response = requests.request("get", api_url, params=None, headers=headers, timeout=30.0)
        if response:
            logger.info(f"Doc service api response status={response.status_code} body={response.text}")
        if not response.ok:
            return None
        return json.loads(response.text)
    except (
        requests.exceptions.ConnectionError,  # pylint: disable=broad-except
        requests.exceptions.Timeout,
        ValueError,
        Exception,
    ) as err:
        logger.error(f"Doc service doc id lookup failure url={api_url}", err)
    return None


def doc_id_lookup_staff(document_id: str, account_id: str, auth_header: str = None) -> dict:
    """Doc service document lookup by consumer document_id as staff."""
    response = {}
    if not document_id:
        return response
    service_url: str = current_app.config.get("DOC_SERVICE_URL")
    apikey: str = current_app.config.get("DOC_SERVICE_KEY")
    if not service_url or not apikey:
        logger.info(f"Missing required service config var url={service_url} apikey={apikey}")
        return response
    api_url: str = service_url + SEARCH_DOC_ID + document_id
    try:
        headers = {"x-apikey": apikey, "Account-Id": account_id, "Content-Type": "application/json"}
        if auth_header:
            headers["Authorization"] = auth_header
        logger.info(f"Doc service document_id lookup url={api_url}")
        response = requests.request("get", api_url, params=None, headers=headers, timeout=30.0)
        if response:
            logger.info(f"Doc service api response status={response.status_code} body={response.text}")
        if not response.ok:
            return {}
        return json.loads(response.text)
    except (
        requests.exceptions.ConnectionError,  # pylint: disable=broad-except
        requests.exceptions.Timeout,
        ValueError,
        Exception,
    ) as err:
        logger.error(f"Doc service doc id lookup failure url={api_url}", err)
    return None
