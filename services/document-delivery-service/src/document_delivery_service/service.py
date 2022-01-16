# Copyright © 2021 Province of British Columbia
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
"""This module contains the service."""
from __future__ import annotations

from http import HTTPStatus

from simple_cloudevent import SimpleCloudEvent

from document_delivery_service.services.documents import deliver_verification_document  # noqa: I001
from document_delivery_service.services.iam import JWTService
from document_delivery_service.services.sftp import SftpConnection
from document_delivery_service.services.storage import GoogleCloudStorage

from .config import Config
from .services.logging import logging

DOC_DELIVERY_FUNCTION = {
    'verification': deliver_verification_document,
}


def doc_service_callback(ce: SimpleCloudEvent, alt: str) -> HTTPStatus:
    """Generate and deliver the documents for the given event."""
    try:

        if ce:
            logging.info(f'Ignoring: got a CloudEvent message: {ce}')
            return HTTPStatus.OK

        if not alt:
            logging.info('Ignoring: Got nothing to do.')
            return HTTPStatus.OK

        config = Config()
        jwt_service = JWTService(config.OIDC_TOKEN_URL, config.OIDC_SA_CLIENT_ID, config.OIDC_SA_CLIENT_SECRET)

        sftp_service = SftpConnection(username=config.SFTP_USERNAME,
                                      host=config.SFTP_HOST,
                                      port=config.SFTP_PORT,
                                      password=config.SFTP_PASSWORD,
                                      private_key=config.SFTP_PRIVATE_KEY,
                                      private_key_algorithm=config.SFTP_PRIVATE_KEY_ALGORITHM,
                                      private_key_passphrase=config.SFTP_PRIVATE_KEY_PASSPHRASE)

        gcs = GoogleCloudStorage(config)

        event_type = 'verification'

        if delivery_func := get_document_delivery_function(event_type):
            status = delivery_func(alt, config, jwt_service, sftp_service, gcs)
            return status

        logging.info(f'Ignoring: Got nothing to do for ce: {ce} and alt: {alt}')
        return HTTPStatus.OK

    except Exception as err:  # noqa: B902
        logging.error(err)
        return HTTPStatus.INTERNAL_SERVER_ERROR


def get_document_delivery_function(event_type: str) -> callable:
    """Get the document delivery function for the given event type."""
    return DOC_DELIVERY_FUNCTION.get(event_type)
