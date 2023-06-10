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

# pylint: disable=too-few-public-methods

"""This module holds methods to support registration model updates - mostly account registration summary."""
from flask import current_app
from sqlalchemy.sql import text

from mhr_api.exceptions import DatabaseException
from mhr_api.models import utils as model_utils
from mhr_api.models.db import db
from mhr_api.models.type_tables import MhrRegistrationTypes
from mhr_api.services.authz import MANUFACTURER_GROUP, QUALIFIED_USER_GROUP, GENERAL_USER_GROUP, BCOL_HELP
from mhr_api.services.authz import GOV_ACCOUNT_ROLE


# Account registration request parameters to support sorting and filtering.
CLIENT_REF_PARAM = 'clientReferenceId'
PAGE_NUM_PARAM = 'pageNumber'
SORT_DIRECTION_PARAM = 'sortDirection'
SORT_CRITERIA_PARAM = 'sortCriteriaName'
MHR_NUMBER_PARAM = 'mhrNumber'
DOC_REG_NUMBER_PARAM = 'documentRegistrationNumber'
REG_TYPE_PARAM = 'registrationType'
REG_TS_PARAM = 'createDateTime'
START_TS_PARAM = 'startDateTime'
END_TS_PARAM = 'endDateTime'
STATUS_PARAM = 'statusType'
SUBMITTING_NAME_PARAM = 'submittingName'
OWNER_NAME_PARAM = 'ownerName'
USER_NAME_PARAM = 'username'
EXPIRY_DAYS_PARAM = 'expiryDays'
SORT_ASCENDING = 'ascending'
SORT_DESCENDING = 'descending'

QUERY_BATCH_MANUFACTURER_MHREG_DEFAULT = """
select r.id, r.account_id, r.registration_ts, rr.id, rr.report_data, rr.batch_storage_url
  from mhr_registrations r, mhr_manufacturers m, mhr_registration_reports rr
 where r.id = rr.registration_id
   and r.account_id = m.account_id
   and r.registration_type = 'MHREG'
   and r.registration_ts between (now() - interval '1 days') and now()
"""
QUERY_BATCH_MANUFACTURER_MHREG = """
select r.id, r.account_id, r.registration_ts, rr.id, rr.report_data, rr.batch_storage_url
  from mhr_registrations r, mhr_manufacturers m, mhr_registration_reports rr
 where r.id = rr.registration_id
   and r.account_id = m.account_id
   and r.registration_type = 'MHREG'
   and r.registration_ts between to_timestamp(:query_val1, 'YYYY-MM-DD HH24:MI:SS')
                             and to_timestamp(:query_val2, 'YYYY-MM-DD HH24:MI:SS')
"""
UPDATE_BATCH_REG_REPORT = """
update mhr_registration_reports
   set batch_storage_url = '{batch_url}'
 where id in ({report_ids})
"""
QUERY_PPR_LIEN_COUNT = """
SELECT COUNT(base_registration_num)
  FROM mhr_lien_check_vw
 WHERE mhr_number = :query_value
"""
QUERY_PKEYS = """
select nextval('mhr_registration_id_seq') AS reg_id,
       nextval('mhr_document_id_seq') AS doc_id,
       get_mhr_number() AS mhr_number,
       get_mhr_doc_reg_number() AS doc_reg_id,
       get_mhr_draft_number() AS draft_num,
       nextval('mhr_draft_id_seq') AS draft_id
"""
QUERY_PKEYS_NO_DRAFT = """
select nextval('mhr_registration_id_seq') AS reg_id,
       nextval('mhr_document_id_seq') AS doc_id,
       get_mhr_number() AS mhr_number,
       get_mhr_doc_reg_number() AS doc_reg_id
"""
CHANGE_QUERY_PKEYS = """
select nextval('mhr_registration_id_seq') AS reg_id,
       nextval('mhr_document_id_seq') AS doc_id,
       get_mhr_doc_reg_number() AS doc_reg_id,
       get_mhr_draft_number() AS draft_num,
       nextval('mhr_draft_id_seq') AS draft_id
"""
CHANGE_QUERY_PKEYS_NO_DRAFT = """
select nextval('mhr_registration_id_seq') AS reg_id,
       nextval('mhr_document_id_seq') AS doc_id,
       get_mhr_doc_reg_number() AS doc_reg_id
"""
DOC_ID_QUALIFIED_CLAUSE = ',  get_mhr_doc_qualified_id() AS doc_id'
DOC_ID_MANUFACTURER_CLAUSE = ',  get_mhr_doc_manufacturer_id() AS doc_id'
DOC_ID_GOV_AGENT_CLAUSE = ',  get_mhr_doc_gov_agent_id() AS doc_id'
BATCH_DOC_NAME_MANUFACTURER_MHREG = 'batch-manufacturer-mhreg-report-{time}.pdf'


class AccountRegistrationParams():
    """Contains parameter values to use when sorting and filtering account summary registration information."""

    account_id: str
    collapse: bool = False
    sbc_staff: bool = False
    from_ui: bool = False
    sort_direction: str = SORT_DESCENDING
    page_number: int = 1
    sort_criteria: str = None
    filter_mhr_number: str = None
    filter_registration_type: str = None
    filter_registration_date: str = None
    filter_reg_start_date: str = None
    filter_reg_end_date: str = None
    filter_status_type: str = None
    filter_client_reference_id: str = None
    filter_submitting_name: str = None
    filter_username: str = None

    def __init__(self, account_id, collapse: bool = False, sbc_staff: bool = False):
        """Set common base initialization."""
        self.account_id = account_id
        self.collapse = collapse
        self.sbc_staff = sbc_staff

    def has_sort(self) -> bool:
        """Check if sort criteria provided."""
        if self.sort_criteria:
            if self.sort_criteria == MHR_NUMBER_PARAM or self.sort_criteria == REG_TYPE_PARAM or \
                    self.sort_criteria == REG_TS_PARAM or self.sort_criteria == CLIENT_REF_PARAM:
                return True
            if self.sort_criteria == SUBMITTING_NAME_PARAM or self.sort_criteria == OWNER_NAME_PARAM or \
                    self.sort_criteria == USER_NAME_PARAM or self.sort_criteria == STATUS_PARAM or \
                    self.sort_criteria == EXPIRY_DAYS_PARAM:
                return True
        return False

    def has_filter(self) -> bool:
        """Check if filter criteria provided."""
        return self.filter_client_reference_id or self.filter_mhr_number or self.filter_registration_type or \
            self.filter_reg_start_date or self.filter_status_type or self.filter_submitting_name or \
            self.filter_username

    def get_filter_values(self):  # pylint: disable=too-many-return-statements
        """Provide optional filter name and value if available."""
        if self.filter_mhr_number:
            return MHR_NUMBER_PARAM, self.filter_mhr_number
        if self.filter_registration_type:
            return REG_TYPE_PARAM, self.filter_registration_type
        if self.filter_reg_start_date:
            return START_TS_PARAM, self.filter_reg_start_date
        if self.filter_status_type:
            return STATUS_PARAM, self.filter_status_type
        if self.filter_client_reference_id:
            return CLIENT_REF_PARAM, self.filter_client_reference_id
        if self.filter_submitting_name:
            return SUBMITTING_NAME_PARAM, self.filter_submitting_name
        if self.filter_username:
            return USER_NAME_PARAM, self.filter_username
        return None, None

    def get_page_size(self) -> int:
        """Provide account registrations query page size."""
        if self.has_filter():
            return model_utils.MAX_ACCOUNT_REGISTRATIONS_DEFAULT
        return model_utils.get_max_registrations_size()

    def get_page_offset(self) -> int:
        """Provide account registrations query page offset."""
        page_offset: int = self.page_number
        if page_offset <= 1:
            return 0
        return (page_offset - 1) * self.get_page_size()


def get_ppr_lien_count(mhr_number: str) -> int:
    """Execute a query to count existing PPR liens on the MH (must not exist check)."""
    try:
        query = text(QUERY_PPR_LIEN_COUNT)
        result = db.session.execute(query, {'query_value': mhr_number})
        row = result.first()
        lien_count = int(row[0])
        return lien_count
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('get_ppr_lien_count exception: ' + str(db_exception))
        raise DatabaseException(db_exception)


def get_owner_group_count(base_reg) -> int:
    """Derive the next owner group sequence number from the number of existing groups."""
    count: int = len(base_reg.owner_groups)
    for reg in base_reg.change_registrations:
        if reg.owner_groups:
            count += len(reg.owner_groups)
    return count


def is_transfer_due_to_death(reg_type: str) -> bool:
    """Return if the registration type is a type of Transfer Due to Death."""
    return reg_type and reg_type in (MhrRegistrationTypes.TRANS_ADMIN,
                                     MhrRegistrationTypes.TRANS_AFFIDAVIT,
                                     MhrRegistrationTypes.TRANS_WILL,
                                     MhrRegistrationTypes.TRAND)


def is_transfer_due_to_death_staff(reg_type: str) -> bool:
    """Return if the registration type is a type of Transfer Due to Death."""
    return reg_type and reg_type in (MhrRegistrationTypes.TRANS_ADMIN,
                                     MhrRegistrationTypes.TRANS_AFFIDAVIT,
                                     MhrRegistrationTypes.TRANS_WILL)


def get_generated_values(registration, draft, user_group: str = None):
    """Get db generated identifiers that are in more than one table.

    Get registration_id, mhr_number, and optionally draft_number.
    """
    # generate reg id, MHR number. If not existing draft also generate draft number
    query = QUERY_PKEYS
    gen_doc_id: bool = False
    if draft:
        query = QUERY_PKEYS_NO_DRAFT
    if user_group and user_group in (QUALIFIED_USER_GROUP, GENERAL_USER_GROUP, BCOL_HELP):
        query += DOC_ID_QUALIFIED_CLAUSE
        gen_doc_id = True
        current_app.logger.debug('Updating query to generate qualified user document id.')
    elif user_group and user_group == MANUFACTURER_GROUP:
        query += DOC_ID_MANUFACTURER_CLAUSE
        gen_doc_id = True
        current_app.logger.debug('Updating query to generate manufacturer document id.')
    elif user_group and user_group == GOV_ACCOUNT_ROLE:
        query += DOC_ID_GOV_AGENT_CLAUSE
        gen_doc_id = True
        current_app.logger.debug('Updating query to generate government agent document id.')
    result = db.session.execute(query)
    row = result.first()
    registration.id = int(row[0])
    registration.doc_pkey = int(row[1])
    registration.mhr_number = str(row[2])
    registration.doc_reg_number = str(row[3])
    if not draft:
        registration.draft_number = str(row[4])
        registration.draft_id = int(row[5])
    if gen_doc_id and not draft:
        registration.doc_id = str(row[4])
    elif gen_doc_id and draft:
        registration.doc_id = str(row[6])
    return registration


def get_change_generated_values(registration, draft, user_group: str = None):
    """Get db generated identifiers that are in more than one table.

    Get registration_id, mhr_number, and optionally draft_number.
    """
    # generate reg id, MHR number. If not existing draft also generate draft number
    query = CHANGE_QUERY_PKEYS
    if draft:
        query = CHANGE_QUERY_PKEYS_NO_DRAFT
    if user_group and user_group in (QUALIFIED_USER_GROUP, GENERAL_USER_GROUP, BCOL_HELP):
        query += DOC_ID_QUALIFIED_CLAUSE
    elif user_group and user_group == MANUFACTURER_GROUP:
        query += DOC_ID_MANUFACTURER_CLAUSE
    # elif user_group and user_group == GOV_ACCOUNT_ROLE:
    else:
        query += DOC_ID_GOV_AGENT_CLAUSE
    result = db.session.execute(query)
    row = result.first()
    registration.id = int(row[0])
    registration.doc_pkey = int(row[1])
    registration.doc_reg_number = str(row[2])
    if not draft:
        registration.draft_number = str(row[3])
        registration.draft_id = int(row[4])
    # if user_group and user_group in (QUALIFIED_USER_GROUP, MANUFACTURER_GROUP, GOV_ACCOUNT_ROLE,
    #                                 GENERAL_USER_GROUP, BCOL_HELP):
    if draft:
        registration.doc_id = str(row[3])
    else:
        registration.doc_id = str(row[5])
    return registration


def update_deceased(owners_json, owner):
    """Set deceased information for transfer due to death registrations."""
    existing_json = owner.json
    match_json = None
    for owner_json in owners_json:
        if owner_json.get('organizationName') and existing_json.get('organizationName') and \
                owner_json.get('organizationName') == existing_json.get('organizationName'):
            match_json = owner_json
            break
        elif owner_json.get('individualName') and existing_json.get('individualName') and \
                owner_json.get('individualName') == existing_json.get('individualName'):
            match_json = owner_json
            break
    if match_json:
        if match_json.get('deathCertificateNumber'):
            owner.death_cert_number = str(match_json.get('deathCertificateNumber')).strip()
        if match_json.get('deathDateTime'):
            owner.death_ts = model_utils.ts_from_iso_format(match_json.get('deathDateTime'))


def include_caution_note(notes, document_id: str) -> bool:
    """Include expired caution note if subsequent continue or extend caution has not expired."""
    latest_caution = None
    for note in notes:
        if not latest_caution and note.get('documentType', '') in ('CAUC', 'CAUE', 'CAU '):
            latest_caution = note
        if note.get('documentId') == document_id:
            break
        elif latest_caution and note.get('documentType', '') not in ('CAUC', 'CAUE', 'CAU '):
            return False
    return latest_caution and not model_utils.date_elapsed(latest_caution.get('expiryDate'))


def get_batch_manufacturer_reg_report_data(start_ts: str = None, end_ts: str = None) -> dict:
    """Get recent manufacturer MHREG registration report data for a batch report."""
    results_json = []
    query_s = QUERY_BATCH_MANUFACTURER_MHREG_DEFAULT
    if start_ts and end_ts:
        query_s = QUERY_BATCH_MANUFACTURER_MHREG
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
            batch_url = str(row[5]) if row[5] else ''
            result_json = {
                'registrationId': int(row[0]),
                'accountId': str(row[1]),
                'reportId': int(row[3]),
                'reportData': row[4],
                'batchStorageUrl': batch_url
            }
            results_json.append(result_json)
    if results_json:
        current_app.logger.debug(f'Found {len(results_json)} manufacturer MHREG registrations.')
    else:
        current_app.logger.debug('No manufacturer MHREG registrations found within the timestamp range.')
    return results_json


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
        current_app.logger.debug(f'Updated {update_count} manufacturer report registrations batch url to {batch_url}.')
    return update_count


def get_batch_storage_name_manufacturer_mhreg():
    """Get a search document storage name in the format YYYY/MM/DD/batch-manufacturer-mhreg-report-time.pdf."""
    now_ts = model_utils.now_ts()
    name = now_ts.isoformat()[:10]
    time = str(now_ts.hour) + '_' + str(now_ts.minute)
    name = name.replace('-', '/') + '/' + BATCH_DOC_NAME_MANUFACTURER_MHREG.format(time=time)
    return name
