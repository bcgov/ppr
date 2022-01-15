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
from http import HTTPStatus
from logging import getLogger

from simple_cloudevent import SimpleCloudEvent

from document_delivery_service.services.iam import IAMError, JWTService
from document_delivery_service.services.documents import deliver_verification_document
from document_delivery_service.services.sftp import SftpConnection
from document_delivery_service.services.storage import GoogleCloudStorage


from .config import Config
from .services.logging import logging


def doc_service_callback(ce: SimpleCloudEvent, alt: str) -> HTTPStatus:
    """Generate and deliver the documents for the given event."""
    try:

        if ce:
            print(f'Ignoring: got a CloudEvent message: {ce}')
            return HTTPStatus.OK

        if not alt:
            print(f'Ignoring: Got nothing to do.')
            return HTTPStatus.OK

        config = Config()
        jwt_service = JWTService(config.OIDC_TOKEN_URL, config.OIDC_SA_CLIENT_ID, config.OIDC_SA_CLIENT_SECRET)
        token = jwt_service.get_token()

        sftp_connection = SftpConnection(username=config.SFTP_USERNAME,
                                         host=config.SFTP_HOST,
                                         port=config.SFTP_PORT,
                                         password=config.SFTP_PASSWORD,
                                         private_key=config.SFTP_PRIVATE_KEY,
                                         private_key_passphrase=config.SFTP_KEY_PASSPHRASE)

        gcs = GoogleCloudStorage(config)

        status = deliver_verification_document(alt, token, config, sftp_connection, gcs)
        
        return status
    except Exception as err:
        print(err)  
        return HTTPStatus.INTERNAL_SERVER_ERROR
