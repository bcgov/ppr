from __future__ import annotations

import datetime
import json
from http import HTTPStatus
from io import BytesIO
from typing import Final, Tuple

import pytz
import requests
from PyPDF2 import PdfFileMerger, PdfFileReader

from document_delivery_service.config import BaseConfig
from document_delivery_service.services.storage import AbstractStorageService, StorageServiceError, StorageDocumentTypes
from document_delivery_service.services.sftp import SftpConnection


def DocumentDeliveryError(Exception):
    pass


def deliver_verification_document(data: dict,
                                  token: str,
                                  config: BaseConfig,
                                  sftp_connection: SftpConnection,
                                  storage_service: AbstractStorageService
                                ) -> HTTPStatus:

    # get document data
    VERIFICATION_CALLBACK: Final = '/financing-statements/verification-callback'
    document_data, status = _get_document_data(data, token, config, VERIFICATION_CALLBACK)
    if status != HTTPStatus.CREATED:
        return status

    # get document pdf
    document_pdf, status = _get_document_pdf(document_data, token, config)
    if status not in (HTTPStatus.OK, HTTPStatus.CREATED):
        return status
    
    # create a filename
    file_name = get_filename(registration_id=data['registrationId'], party_id=data['partyId'])

    # save document to storage
    storage_service.connect()
    storage_filepath = file_name
    if hasattr(config, 'STORAGE_FILEPATH') and config.STORAGE_FILEPATH:
        storage_filepath = f'{config.STORAGE_FILEPATH}/{file_name}'
    storage_service.save_document(bucket_name=config.STORAGE_BUCKET_NAME,
                                    filename=storage_filepath,
                                    raw_data=document_pdf,
                                    doc_type=StorageDocumentTypes.BINARY.value)

    # upload document to sftp
    sftp_connection.connect()
    remote_path = f'{config.SFTP_STORAGE_DIRECTORY}/{file_name}'
    sftp_connection.put_buffer(document_pdf, remote_path)
    
    return HTTPStatus.CREATED


def _get_document_data(data: dict, token: str, config: BaseConfig, end_point: str) -> Tuple[dict, HTTPStatus]:
    """Retrieve the document data from the API.
    
    Args:
        data: The data to send to the API.
        token: The token to access the API.
        config: The application config data.
        end_point: The end point to call on the API.
    
    Returns:
        The document data and the status code.
    """
    headers = { 
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    url = f'{config.PPR_API_URL}{end_point}'
    rv = requests.post(url=url,
                       headers=headers,
                       data=json.dumps(data))

    # check
    if rv.status_code == HTTPStatus.CREATED \
        and (json_data := rv.json()) \
            and json_data.get('coverLetterData') and json_data.get('verificationData'):
        return rv.json(), rv.status_code
    
    return None, HTTPStatus.BAD_REQUEST


def _get_document_pdf(data: dict, token: str, config: BaseConfig) -> Tuple[bytes, HTTPStatus]:
    """Retrieve the document pdf from the Reports API.
    
    Args:
        data: The data to send to the API.
        token: The token to access the API.
        config: The application config data.
        end_point: The end point to call on the API.

    Returns:
        The pdf data and the status code.
    """
    headers = { 
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    url = config.REPORT_SVC_URL

    # get cover letter
    response = requests.post(url=url, headers=headers, data=json.dumps(data['coverLetterData']))
    if response.status_code not in (HTTPStatus.OK, HTTPStatus.CREATED):
        return None, response.status_code

    coverLetter = response.content

    # get verification
    response = requests.post(url=url, headers=headers, data=json.dumps(data['verificationData']))
    if response.status_code not in (HTTPStatus.OK, HTTPStatus.CREATED):
        return None, response.status_code

    verification = response.content

    if coverLetter and verification and isinstance(coverLetter, bytes) and isinstance(verification, bytes):
        merger = PdfFileMerger()

        merger.append(BytesIO(coverLetter))
        merger.append(BytesIO(verification))

        out_final = BytesIO()

        merger.write(out_final)

        return out_final.getvalue(), HTTPStatus.CREATED
    
    return None, HTTPStatus.BAD_REQUEST


def get_filename(registration_id, party_id) -> str:
    """Build a correctly formatted unique name."""
    FILENAME_TEMPLATE = 'PPRVER.{statement_key}.{day}.{month}.{year}.PDF'
    today_utc = datetime.datetime.now(pytz.utc)
    today_local = today_utc.astimezone(pytz.timezone('Canada/Pacific'))

    reg_key = str(registration_id) + '.' + str(party_id)
    reg_key = reg_key[:13]

    filename = FILENAME_TEMPLATE.format(statement_key=reg_key,
                                                    day=str(today_local.day),
                                                    month=str(today_local.month),
                                                    year=str(today_local.year))
    return filename
