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
from http import HTTPStatus

from flask import current_app
from sqlalchemy.sql import text

from mhr_api.models import EventTracking, utils as model_utils
from mhr_api.models.db import db
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
BATCH_DOC_NAME_NOC_LOCATION = 'batch-noc-location-report-{time}.pdf'


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
