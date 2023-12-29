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
"""This module holds utilities for batch processes."""
import copy
from http import HTTPStatus

from flask import current_app
from sqlalchemy.sql import text

from mhr_api.models import EventTracking, utils as model_utils, MhrRegistration
from mhr_api.models.db import db
from mhr_api.models.type_tables import MhrDocumentTypes, MhrRegistrationStatusTypes
from mhr_api.resources import registration_utils as reg_utils
from mhr_api.services.document_storage.storage_service import DocumentTypes, GoogleStorageService


DEFAULT_DOWNLOAD_DAYS: int = 7
QUERY_BATCH_NOC_LOCATION_DEFAULT = """
select r.id, rr.id, rr.batch_report_data, rr.batch_storage_url
  from mhr_registrations r, mhr_registration_reports rr, mhr_documents d
 where r.id = rr.registration_id
   and r.id = d.registration_id
   and d.document_type in ('REG_103', 'STAT', 'PUBA', 'REGC', 'AMEND_PERMIT', 'CANCEL_PERMIT')
   and rr.batch_report_data is not null
   and json_typeof(rr.batch_report_data) != 'null'
   and r.registration_ts between ((now() at time zone 'utc') - interval '1 days') and (now() at time zone 'utc')
  order by r.id
 """
QUERY_BATCH_NOC_LOCATION = """
select r.id, rr.id, rr.batch_report_data, rr.batch_storage_url
  from mhr_registrations r, mhr_registration_reports rr, mhr_documents d
 where r.id = rr.registration_id
   and r.id = d.registration_id
   and d.document_type in ('REG_103', 'STAT', 'PUBA', 'REGC', 'AMEND_PERMIT', 'CANCEL_PERMIT')
   and rr.batch_report_data is not null
   and json_typeof(rr.batch_report_data) != 'null'
   and r.registration_ts between to_timestamp(:query_val1, 'YYYY-MM-DD HH24:MI:SS')
                             and to_timestamp(:query_val2, 'YYYY-MM-DD HH24:MI:SS')
  order by r.id
"""
UPDATE_BATCH_REG_REPORT = """
update mhr_registration_reports
   set batch_storage_url = '{batch_url}'
 where id in ({report_ids})
"""
QUERY_BATCH_REGISTRATION_DEFAULT = """
select rr.batch_registration_data
  from mhr_registration_reports rr
 where rr.create_ts between ((now() at time zone 'utc') - interval '7 days') and (now() at time zone 'utc')
   and rr.batch_registration_data is not null
   and json_typeof(rr.batch_registration_data) != 'null'
  order by rr.create_ts
 """
QUERY_BATCH_REGISTRATION = """
select rr.batch_registration_data
  from mhr_registration_reports rr
 where rr.create_ts between to_timestamp(:query_val1, 'YYYY-MM-DD HH24:MI:SS') and
                            to_timestamp(:query_val2, 'YYYY-MM-DD HH24:MI:SS')
   and rr.batch_registration_data is not null
   and json_typeof(rr.batch_registration_data) != 'null'
  order by rr.create_ts
 """
BATCH_DOC_NAME_NOC_LOCATION = 'batch-noc-location-report-{time}.pdf'
BATCH_DOC_TYPES = [
    MhrDocumentTypes.ABAN.value,
    MhrDocumentTypes.REG_101.value,
    MhrDocumentTypes.REG_103.value,
    MhrDocumentTypes.REGC.value,
    MhrDocumentTypes.AFFE.value,
    MhrDocumentTypes.TRAN.value,
    MhrDocumentTypes.DEAT.value,
    MhrDocumentTypes.LETA.value,
    MhrDocumentTypes.WILL.value,
    MhrDocumentTypes.AMEND_PERMIT.value,
    MhrDocumentTypes.CANCEL_PERMIT.value,
    MhrDocumentTypes.TRANS_FAMILY_ACT.value,
    MhrDocumentTypes.TRANS_INFORMAL_SALE.value,
    MhrDocumentTypes.TRANS_LAND_TITLE.value,
    MhrDocumentTypes.TRANS_QUIT_CLAIM.value,
    MhrDocumentTypes.TRANS_RECEIVERSHIP.value,
    MhrDocumentTypes.TRANS_SEVER_GRANT.value,
    MhrDocumentTypes.TRANS_WRIT_SEIZURE.value,
    MhrDocumentTypes.EXNR.value,
    MhrDocumentTypes.EXRE.value,
    MhrDocumentTypes.EXRS.value,
    MhrDocumentTypes.PUBA.value,
    MhrDocumentTypes.STAT.value,
    MhrDocumentTypes.BANK.value,
    MhrDocumentTypes.COU.value,
    MhrDocumentTypes.FORE.value,
    MhrDocumentTypes.GENT.value,
    MhrDocumentTypes.REIV.value,
    MhrDocumentTypes.REPV.value,
    MhrDocumentTypes.SZL.value,
    MhrDocumentTypes.TAXS.value,
    MhrDocumentTypes.VEST.value,
    MhrDocumentTypes.ADDI.value,
    MhrDocumentTypes.ATTA.value,
    MhrDocumentTypes.COMP.value,
    MhrDocumentTypes.CONF.value,
    MhrDocumentTypes.DNCH.value,
    MhrDocumentTypes.MAID.value,
    MhrDocumentTypes.MAIL.value,
    MhrDocumentTypes.MARR.value,
    MhrDocumentTypes.MEAM.value,
    MhrDocumentTypes.NAMV.value,
    MhrDocumentTypes.REBU.value
]
PREVIOUS_OWNER_DOC_TYPES = [
    MhrDocumentTypes.PUBA.value,
    MhrDocumentTypes.REGC.value,
    MhrDocumentTypes.AFFE.value,
    MhrDocumentTypes.TRAN.value,
    MhrDocumentTypes.DEAT.value,
    MhrDocumentTypes.LETA.value,
    MhrDocumentTypes.WILL.value,
    MhrDocumentTypes.TRANS_FAMILY_ACT.value,
    MhrDocumentTypes.TRANS_INFORMAL_SALE.value,
    MhrDocumentTypes.TRANS_LAND_TITLE.value,
    MhrDocumentTypes.TRANS_QUIT_CLAIM.value,
    MhrDocumentTypes.TRANS_RECEIVERSHIP.value,
    MhrDocumentTypes.TRANS_SEVER_GRANT.value,
    MhrDocumentTypes.TRANS_WRIT_SEIZURE.value,
    MhrDocumentTypes.COMP.value,
    MhrDocumentTypes.ABAN.value,
    MhrDocumentTypes.BANK.value,
    MhrDocumentTypes.COU.value,
    MhrDocumentTypes.FORE.value,
    MhrDocumentTypes.GENT.value,
    MhrDocumentTypes.REIV.value,
    MhrDocumentTypes.REPV.value,
    MhrDocumentTypes.SZL.value,
    MhrDocumentTypes.TAXS.value,
    MhrDocumentTypes.VEST.value,
    MhrDocumentTypes.MAID.value,
    MhrDocumentTypes.MAIL.value,
    MhrDocumentTypes.MARR.value,
    MhrDocumentTypes.MEAM.value,
    MhrDocumentTypes.NAMV.value
]
PREVIOUS_LOCATION_DOC_TYPES = [
    MhrDocumentTypes.REG_103.value,
    MhrDocumentTypes.AMEND_PERMIT.value,
    MhrDocumentTypes.CANCEL_PERMIT.value,
    MhrDocumentTypes.PUBA.value,
    MhrDocumentTypes.REGC.value,
    MhrDocumentTypes.CONF.value,
    MhrDocumentTypes.STAT.value
]


def update_reg_report_batch_url(json_data: dict, batch_url: str) -> int:
    """Set the mhr registration reports batch storage url for the recent registrations in json_data."""
    update_count: int = 0
    if not json_data:
        return update_count
    query_s = UPDATE_BATCH_REG_REPORT
    report_ids: str = ''
    for report in json_data:
        update_count += 1
        if report_ids != '':
            report_ids += ','
        report_ids += str(report.get('reportId'))
    query_s = query_s.format(batch_url=batch_url, report_ids=report_ids)
    current_app.logger.debug(f'Executing update query {query_s}')
    query = text(query_s)
    result = db.session.execute(query)
    db.session.commit()
    if result:
        current_app.logger.debug(f'Updated {update_count} report registrations batch url to {batch_url}.')
    return update_count


def get_batch_storage_name_noc_location():
    """Get the current day document storage name for the batch noc location report as YYYY/MM/DD/report-name.pdf."""
    now_ts = model_utils.now_ts()
    name = now_ts.isoformat()[:10]
    time = str(now_ts.hour) + '_' + str(now_ts.minute)
    name = name.replace('-', '/') + '/' + BATCH_DOC_NAME_NOC_LOCATION.format(time=time)
    return name


def get_batch_location_report_data(start_ts: str = None, end_ts: str = None) -> dict:
    """Get recent noc location with PPR lien registration report data for a batch report."""
    results_json = []
    query_s = QUERY_BATCH_NOC_LOCATION_DEFAULT
    if start_ts and end_ts:
        query_s = QUERY_BATCH_NOC_LOCATION
        current_app.logger.debug(f'Using timestamp range {start_ts} to {end_ts}.')
    else:
        current_app.logger.debug('Using a default timestamp range of within the previous day.')
    query = text(query_s)
    result = None
    if start_ts and end_ts:
        start: str = start_ts[:19].replace('T', ' ')
        end: str = end_ts[:19].replace('T', ' ')
        current_app.logger.debug(f'start={start} end={end}')
        result = db.session.execute(query, {'query_val1': start, 'query_val2': end})
    else:
        result = db.session.execute(query)
    rows = result.fetchall()
    if rows is not None:
        for row in rows:
            batch_url = str(row[3]) if row[3] else ''
            result_json = {
                'registrationId': int(row[0]),
                'reportId': int(row[1]),
                'reportData': row[2],
                'batchStorageUrl': batch_url
            }
            results_json.append(result_json)
    if results_json:
        current_app.logger.debug(f'Found {len(results_json)} NOC location registrations.')
    else:
        current_app.logger.debug('No NOC location registrations found within the timestamp range.')
    return results_json


def batch_location_report_empty(notify: bool, start_ts: str, end_ts: str):
    """Create response when no noc location registrations exist."""
    message: str = 'No noc location registrations found for default timestamp range of last 24 hours.'
    if start_ts and end_ts:
        message = f'No noc location registrations found for timestamp range {start_ts} to {end_ts}'
    current_app.logger.info(message)
    if notify:
        current_app.logger.debug('Sending notify with no noc location registrations.')
        reg_utils.email_batch_location_staff(None)
    EventTracking.create(reg_utils.EVENT_KEY_BATCH_LOCATION,
                         EventTracking.EventTrackingTypes.MHR_REGISTRATION_REPORT,
                         HTTPStatus.NO_CONTENT,
                         message)
    return '', HTTPStatus.NO_CONTENT


def batch_location_report_response(raw_data, report_url: str, notify: bool):
    """Create response when noc location registrations exist and report generated."""
    message: str = report_url if report_url else 'Batch noc location report returned in response.'
    if notify:
        current_app.logger.debug(f'Sending noc location notify message with download link to {report_url}')
        reg_utils.email_batch_location_staff(report_url)
    if not report_url:
        headers = {'Content-Type': 'application/pdf'}
        return raw_data, HTTPStatus.OK, headers
    headers = {'Content-Type': 'application/json'}
    response_json = {'reportDownloadUrl': report_url}
    EventTracking.create(reg_utils.EVENT_KEY_BATCH_LOCATION,
                         EventTracking.EventTrackingTypes.MHR_REGISTRATION_REPORT,
                         HTTPStatus.OK,
                         message)
    return response_json, HTTPStatus.OK, headers


def batch_location_report_exists(batch_storage_url: str, notify: bool, return_link: bool):
    """Create response when batch manufacturer registration report already exists."""
    report_url: str = None
    raw_data = None
    current_app.logger.info(f'Fetching batch noc location registration report for: {batch_storage_url}.')
    if return_link:
        report_url = GoogleStorageService.get_document_link(batch_storage_url,
                                                            DocumentTypes.BATCH_REGISTRATION,
                                                            DEFAULT_DOWNLOAD_DAYS)
    else:
        raw_data = GoogleStorageService.get_document(batch_storage_url, DocumentTypes.BATCH_REGISTRATION)
    return batch_location_report_response(raw_data, report_url, notify)


def save_batch_location_report(registrations, raw_data, return_link: bool) -> str:
    """Save the batch noc location registration report to document storage."""
    link: str = None
    batch_storage_url = get_batch_storage_name_noc_location()
    current_app.logger.info(f'Saving batch noc location registration report to: {batch_storage_url}.')
    if return_link:
        link = GoogleStorageService.save_document_link(batch_storage_url,
                                                       raw_data,
                                                       DocumentTypes.BATCH_REGISTRATION,
                                                       DEFAULT_DOWNLOAD_DAYS)
    else:
        GoogleStorageService.save_document(batch_storage_url, raw_data, DocumentTypes.BATCH_REGISTRATION)
    update_reg_report_batch_url(registrations, batch_storage_url)
    return link


def is_batch_doc_type(doc_type: str) -> bool:
    """Determine if the registration document type is a batch document type."""
    return bool(doc_type in BATCH_DOC_TYPES)


def is_previous_location_doc_type(doc_type: str, json_data: dict) -> bool:
    """Determine if the registration document type is a change of location document type."""
    if doc_type in (MhrDocumentTypes.REGC, MhrDocumentTypes.PUBA) and not json_data.get('location'):
        return False
    return bool(doc_type in PREVIOUS_LOCATION_DOC_TYPES)


def is_previous_owner_doc_type(doc_type: str, json_data: dict) -> bool:
    """Determine if the registration document type is a change of owners document type."""
    if doc_type in (MhrDocumentTypes.REGC, MhrDocumentTypes.PUBA) and not json_data.get('ownerGroups'):
        return False
    return bool(doc_type in PREVIOUS_OWNER_DOC_TYPES)


def get_batch_registration_json(registration: MhrRegistration, json_data: dict, current_json: dict = None) -> dict:
    """Generate the batch version of the registration as JSON."""
    reg_json = copy.deepcopy(json_data)
    doc_type: str = reg_json.get('documentType')
    if not doc_type:
        doc_type = registration.documents[0].document_type
        reg_json['documentType'] = doc_type
    reg_json = batch_json_cleanup(reg_json)
    if not current_json or doc_type == MhrDocumentTypes.REG_101:
        return reg_json
    reg_json = set_batch_json_description(reg_json, current_json)
    reg_json = set_batch_json_location(reg_json, current_json, doc_type)
    reg_json = set_batch_json_owners(reg_json, current_json, doc_type)
    if reg_json.get('status') == model_utils.STATUS_FROZEN:
        reg_json['status'] = MhrRegistrationStatusTypes.ACTIVE.value
    return reg_json


def set_batch_json_description(reg_json: dict, current_json: dict) -> dict:
    """Update the batch JSON: add the current description."""
    if not reg_json.get('description') and current_json:
        reg_json['description'] = current_json.get('description')
    if reg_json.get('description') and reg_json['description'].get('status'):
        del reg_json['description']['status']
    return reg_json


def set_batch_json_location(reg_json: dict, current_json: dict, doc_type: str) -> dict:
    """Update the batch JSON: add the current location and conditionally the previous location."""
    if is_previous_location_doc_type(doc_type, reg_json) and current_json:
        current_app.logger.debug(f'Setting up previous location for doc type={doc_type}.')
        reg_json['previousLocation'] = current_json.get('location')
    if reg_json.get('newLocation'):
        reg_json['location'] = copy.deepcopy(reg_json.get('newLocation'))
        del reg_json['newLocation']
    elif not reg_json.get('location') and current_json:
        reg_json['location'] = current_json.get('location')
    return reg_json


def set_batch_json_owners(reg_json: dict, current_json: dict, doc_type: str) -> dict:
    """Update the batch JSON: add the current owner groups and conditionally the previous owner groups."""
    if is_previous_owner_doc_type(doc_type, reg_json) and current_json:
        current_app.logger.debug(f'Setting up previous owners for doc type={doc_type}.')
        reg_json['previousOwnerGroups'] = current_json.get('ownerGroups')
        if reg_json.get('deleteOwnerGroups'):
            del reg_json['deleteOwnerGroups']
    if reg_json.get('addOwnerGroups'):
        reg_json['ownerGroups'] = copy.deepcopy(reg_json.get('addOwnerGroups'))
        del reg_json['addOwnerGroups']
    elif not reg_json.get('ownerGroups') and current_json:
        reg_json['ownerGroups'] = current_json.get('ownerGroups')
    return reg_json


def batch_json_cleanup(reg_json: dict) -> dict:
    """Remove properties not in the requirements (used interally for reports)."""
    if reg_json.get('payment'):
        del reg_json['payment']
    if reg_json.get('usergroup'):
        del reg_json['usergroup']
    if reg_json.get('username'):
        del reg_json['username']
    if reg_json.get('affirmByName'):
        del reg_json['affirmByName']
    if reg_json.get('permitDateTime'):
        del reg_json['permitDateTime']
    if reg_json.get('permitExpiryDateTime'):
        del reg_json['permitExpiryDateTime']
    if reg_json.get('permitRegistrationNumber'):
        del reg_json['permitRegistrationNumber']
    if reg_json.get('permitStatus'):
        del reg_json['permitStatus']
    if reg_json.get('amendment'):
        del reg_json['amendment']
    return reg_json


def get_batch_registration_data(start_ts: str = None, end_ts: str = None):
    """Get recent registrations as JSON in a batch by timestamp range."""
    results_json = []
    query_s = QUERY_BATCH_REGISTRATION_DEFAULT
    if start_ts and end_ts:
        query_s = QUERY_BATCH_REGISTRATION
        current_app.logger.debug(f'Using timestamp range {start_ts} to {end_ts}.')
    else:
        current_app.logger.debug('Using a default timestamp range of within the previous 7 days.')
    query = text(query_s)
    result = None
    if start_ts and end_ts:
        start: str = start_ts[:19].replace('T', ' ')
        end: str = end_ts[:19].replace('T', ' ')
        current_app.logger.debug(f'start={start} end={end}')
        result = db.session.execute(query, {'query_val1': start, 'query_val2': end})
    else:
        result = db.session.execute(query)
    rows = result.fetchall()
    if rows is not None:
        for row in rows:
            results_json.append(row[0])
    if results_json:
        current_app.logger.debug(f'Found {len(results_json)} batch registrations.')
    else:
        current_app.logger.debug('No batch registrations found within the timestamp range.')
    return results_json
