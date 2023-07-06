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
"""This module holds common statement registration data."""
from flask import current_app
from sqlalchemy.sql import text

from mhr_api.exceptions import DatabaseException
from mhr_api.models import Db2Manuhome, Db2Document, utils as model_utils, registration_utils as reg_utils
from mhr_api.models.registration_utils import AccountRegistrationParams
from mhr_api.models.type_tables import MhrDocumentType, MhrDocumentTypes, MhrRegistrationTypes, MhrNoteStatusTypes
from mhr_api.models.db import db
from mhr_api.models.db2.queries import (
    UPDATE_LTSA_PID,
    QUERY_LTSA_PID,
    QUERY_ACCOUNT_MHR_LEGACY,
    QUERY_ACCOUNT_REGISTRATIONS_SUMMARY,
    QUERY_MHR_NUMBER_LEGACY,
    DOC_ID_COUNT_QUERY,
    QUERY_ACCOUNT_ADD_REGISTRATION,
    QUERY_ACCOUNT_ADD_REGISTRATION_DOC,
    QUERY_ACCOUNT_REGISTRATIONS,
    QUERY_ACCOUNT_REGISTRATIONS_SORT,
    PERMIT_COUNT_QUERY,
    REG_ORDER_BY_DATE,
    REG_ORDER_BY_MHR_NUMBER,
    REG_ORDER_BY_REG_TYPE,
    REG_ORDER_BY_STATUS,
    REG_ORDER_BY_SUBMITTING_NAME,
    REG_ORDER_BY_CLIENT_REF,
    REG_ORDER_BY_USERNAME,
    REG_ORDER_BY_OWNER_NAME,
    REG_ORDER_BY_EXPIRY_DAYS,
    REG_FILTER_REG_TYPE,
    REG_FILTER_REG_TYPE_COLLAPSE,
    REG_FILTER_STATUS,
    REG_FILTER_SUBMITTING_NAME,
    REG_FILTER_SUBMITTING_NAME_COLLAPSE,
    REG_FILTER_CLIENT_REF,
    REG_FILTER_CLIENT_REF_COLLAPSE,
    REG_FILTER_USERNAME,
    REG_FILTER_USERNAME_COLLAPSE,
    REG_FILTER_DATE,
    REG_FILTER_DATE_COLLAPSE,
    SORT_DESCENDING,
    SORT_ASCENDING,
    DEFAULT_SORT_ORDER,
    NEXT_MHR_NUM_SELECT_FOR_UPDATE,
    NEXT_MHR_NUM_UPDATE
)


FROM_LEGACY_REGISTRATION_TYPE = {
    '101': 'MHREG',
    'TRAN': 'TRANS',
    'DEAT': 'TRAND',
    'AFFE': 'TRANS_AFFIDAVIT',
    'LETA': 'TRANS_ADMIN',
    'WILL': 'TRANS_WILL',
    '102': 'DECAL_REPLACE',
    '103': 'PERMIT',
    '103E': 'PERMIT_EXTENSION',
    'EXRS': 'EXEMPTION_RES',
    'EXNR': 'EXEMPTION_NON_RES'
}
FROM_LEGACY_NOTE_REG_TYPE = {
    'CAU': 'REG_STAFF_ADMIN',
    'CAUC': 'REG_STAFF_ADMIN',
    'CAUE': 'REG_STAFF_ADMIN',
    'NCAN': 'REG_STAFF_ADMIN',
    'NCON': 'REG_STAFF_ADMIN',
    'NPUB': 'REG_STAFF_ADMIN',
    'REST': 'REG_STAFF_ADMIN',
    'TAXN': 'REG_STAFF_ADMIN',
    'REGC': 'REG_STAFF_ADMIN',
    '102': 'REG_STAFF_ADMIN'
}
FROM_LEGACY_DOC_TYPE = {
    '101': 'REG_101',
    '102': 'REG_102',
    '103': 'REG_103',
    '103E': 'REG_103E'
}
TO_LEGACY_DOC_TYPE = {
    'MHREG': '101 ',
    'CONV': 'CONV',
    'TRANS': 'TRAN',
    'TRAND': 'DEAT',
    'TRANS_AFFIDAVIT': 'AFFE',
    'TRANS_ADMIN': 'LETA',
    'TRANS_WILL': 'WILL',
    'EXEMPTION_RES': 'EXRS',
    'EXEMPTION_NON_RES': 'EXNR',
    'PERMIT': '103 ',
    'DECAL_REPLACE': '102 ',
    'PERMIT_EXTENSION': '103E',
    'REG_101': '101 ',
    'REG_102': '102 ',
    'REG_103': '103 ',
    'REG_103E': '103E'
}
TO_REGISTRATION_TYPE = {
    '101': 'MHREG',
    'CONV': 'MHREG_CONVERSION',
    'TRAN': 'TRANS',
    'DEAT': 'TRAND',
    'AFFE': 'TRANS_AFFIDAVIT',
    'LETA': 'TRANS_ADMIN',
    'WILL': 'TRANS_WILL',
    'EXRS': 'EXEMPTION_RES',
    'EXNR': 'EXEMPTION_NON_RES',
    '103': 'PERMIT',
    '102': 'DECAL_REPLACE',
    '103E': 'PERMIT_EXTENSION',
    'REG_101': 'MHREG',
    'REG_102': 'DECAL_REPLACE',
    'REG_103': 'PERMIT',
    'REG_103E': 'PERMIT_EXTENSION',
    'DEFAULT': 'REG_STAFF_ADMIN'
}
UPDATE_PID_STATUS_SUCCESS = 'A'
UPDATE_PID_STATUS_ERROR = 'E'
DEFAULT_REG_TYPE_FILTER = "'101 '"
QUERY_ACCOUNT_FILTER_BY = {
    reg_utils.STATUS_PARAM: REG_FILTER_STATUS,
    reg_utils.REG_TYPE_PARAM: REG_FILTER_REG_TYPE,
    reg_utils.SUBMITTING_NAME_PARAM: REG_FILTER_SUBMITTING_NAME,
    reg_utils.CLIENT_REF_PARAM: REG_FILTER_CLIENT_REF,
    reg_utils.USER_NAME_PARAM: REG_FILTER_USERNAME,
    reg_utils.START_TS_PARAM: REG_FILTER_DATE
}
QUERY_ACCOUNT_FILTER_BY_COLLAPSE = {
    reg_utils.STATUS_PARAM: REG_FILTER_STATUS,
    reg_utils.REG_TYPE_PARAM: REG_FILTER_REG_TYPE_COLLAPSE,
    reg_utils.SUBMITTING_NAME_PARAM: REG_FILTER_SUBMITTING_NAME_COLLAPSE,
    reg_utils.CLIENT_REF_PARAM: REG_FILTER_CLIENT_REF_COLLAPSE,
    reg_utils.USER_NAME_PARAM: REG_FILTER_USERNAME_COLLAPSE,
    reg_utils.START_TS_PARAM: REG_FILTER_DATE_COLLAPSE
}
QUERY_ACCOUNT_ORDER_BY = {
    reg_utils.REG_TS_PARAM: REG_ORDER_BY_DATE,
    reg_utils.MHR_NUMBER_PARAM: REG_ORDER_BY_MHR_NUMBER,
    reg_utils.STATUS_PARAM: REG_ORDER_BY_STATUS,
    reg_utils.REG_TYPE_PARAM: REG_ORDER_BY_REG_TYPE,
    reg_utils.SUBMITTING_NAME_PARAM: REG_ORDER_BY_SUBMITTING_NAME,
    reg_utils.CLIENT_REF_PARAM: REG_ORDER_BY_CLIENT_REF,
    reg_utils.OWNER_NAME_PARAM: REG_ORDER_BY_OWNER_NAME,
    reg_utils.EXPIRY_DAYS_PARAM: REG_ORDER_BY_EXPIRY_DAYS,
    reg_utils.USER_NAME_PARAM: REG_ORDER_BY_USERNAME
}
REGISTRATION_DESC_NEW = 'MANUFACTURED HOME REGISTRATION'
LEGACY_STATUS_DESCRIPTION = {
    'R': 'ACTIVE',
    'E': 'EXEMPT',
    'D': 'DRAFT',
    'C': 'HISTORICAL'
}
TO_LEGACY_STATUS = {
    'ACTIVE': 'R',
    'EXEMPT': 'E',
    'HISTORICAL': 'C'
}
LEGACY_REGISTRATION_DESCRIPTION = {
    '101': REGISTRATION_DESC_NEW,
    'CONV': REGISTRATION_DESC_NEW
}
DOCUMENT_TYPE_REG = '101'
DOCUMENT_TYPE_AFFIDAVIT = 'AFFE'
REG_STATUS_FROZEN = 'FROZEN'
OWNER_TYPE_INDIVIDUAL = 'I'
REGISTRATION_PATH = '/mhr/api/v1/registrations/'
DOCUMENT_PATH = '/mhr/api/v1/documents/'
CAUTION_CANCELLED_DAYS: int = -9999
CAUTION_INDEFINITE_DAYS: int = 9999


def find_by_id(registration_id: int, search: bool = False):
    """Return the legacy registration matching the id."""
    if registration_id:
        return Db2Manuhome.find_by_id(registration_id, search)
    return None


def find_summary_by_mhr_number(account_id: str, mhr_number: str, staff: bool):
    """Return the MHR registration summary parent-child information matching the registration number."""
    registrations = []
    try:
        query = text(QUERY_ACCOUNT_ADD_REGISTRATION)
        result = db.get_engine(current_app, 'db2').execute(query, {'query_mhr_number': mhr_number})
        rows = result.fetchall()
        if rows is not None:
            for row in rows:
                registrations.append(__build_summary(row, True, None))
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('DB2 find_summary_by_mhr_number exception: ' + str(db_exception))
        raise DatabaseException(db_exception)

    if registrations:
        try:
            query = text(QUERY_MHR_NUMBER_LEGACY)
            result = db.session.execute(query, {'query_value': account_id, 'query_value2': mhr_number})
            row = result.first()
            reg_count = int(row[0])
            extra_count = int(row[1])
            reg_account_id = str(row[2])
            lien_registration_type: str = str(row[3]) if row[3] else ''
            current_app.logger.debug(f'reg_count={reg_count}, extra_count={extra_count}, staff={staff}')
            # Set inUserList to true if MHR number already added to account extra registrations.
            for registration in registrations:
                if reg_count > 0 or extra_count > 0:
                    registration['inUserList'] = True
                __update_summary_info(registration, registrations, None, staff, account_id)
                if registration['documentType'] in \
                        (Db2Document.DocumentTypes.CONV, Db2Document.DocumentTypes.MHREG_TRIM):
                    registration['lienRegistrationType'] = lien_registration_type
            # Path to download report only available for staff and registrations created by the account.
            if reg_count > 0 and (staff or account_id == reg_account_id):
                for reg in registrations:
                    if reg['documentType'] in (Db2Document.DocumentTypes.CONV, Db2Document.DocumentTypes.MHREG_TRIM):
                        reg['path'] = REGISTRATION_PATH + mhr_number
                    else:
                        reg['path'] = DOCUMENT_PATH + reg.get('documentId')
            registrations = __collapse_results(registrations)
            return registrations[0]
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('find_summary_by_mhr_number mhr extra check exception: ' + str(db_exception))
            raise DatabaseException(db_exception)
    return registrations


def find_summary_by_doc_reg_number(account_id: str, doc_reg_number: str, staff: bool):
    """Return the MHR registration summary parent-child information matching the document registration number."""
    registrations = []
    mhr_number: str = None
    try:
        query = text(QUERY_ACCOUNT_ADD_REGISTRATION_DOC)
        result = db.get_engine(current_app, 'db2').execute(query, {'query_value': doc_reg_number})
        rows = result.fetchall()
        if rows is not None:
            for row in rows:
                if not mhr_number:
                    mhr_number = str(row[0])
                registrations.append(__build_summary(row, True, None))
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('DB2 find_summary_by_mhr_number exception: ' + str(db_exception))
        raise DatabaseException(db_exception)

    if registrations and mhr_number:
        try:
            query = text(QUERY_MHR_NUMBER_LEGACY)
            result = db.session.execute(query, {'query_value': account_id, 'query_value2': mhr_number})
            row = result.first()
            reg_count = int(row[0])
            extra_count = int(row[1])
            reg_account_id = str(row[2])
            lien_registration_type: str = str(row[3]) if row[3] else ''
            current_app.logger.debug(f'reg_count={reg_count}, extra_count={extra_count}, staff={staff}')
            # Set inUserList to true if MHR number already added to account extra registrations.
            for registration in registrations:
                if reg_count > 0 or extra_count > 0:
                    registration['inUserList'] = True
                __update_summary_info(registration, registrations, None, staff, account_id)
                if registration['documentType'] in \
                        (Db2Document.DocumentTypes.CONV, Db2Document.DocumentTypes.MHREG_TRIM):
                    registration['lienRegistrationType'] = lien_registration_type
            # Path to download report only available for staff and registrations created by the account.
            if reg_count > 0 and (staff or account_id == reg_account_id):
                for reg in registrations:
                    if reg['documentType'] in (Db2Document.DocumentTypes.CONV, Db2Document.DocumentTypes.MHREG_TRIM):
                        reg['path'] = REGISTRATION_PATH + mhr_number
                    else:
                        reg['path'] = DOCUMENT_PATH + reg.get('documentId')
            registrations = __collapse_results(registrations)
            return registrations[0]
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('find_summary_by_mhr_number mhr extra check exception: ' + str(db_exception))
            raise DatabaseException(db_exception)
    return registrations


def find_all_by_account_id(params: AccountRegistrationParams):
    """Return a summary list of recent MHR registrations belonging to an account."""
    results = []
    # 1. get account and extra registrations from the Posgres table, then query DB2 by set of mhr numbers.
    mhr_list = __get_mhr_list(params.account_id)
    # 2 Get summary list of new application registrations.
    reg_summary_list = __get_reg_summary_list(params.account_id)
    doc_types = MhrDocumentType.find_all()
    if mhr_list:
        # 3. Get the summary info from DB2.
        try:
            result = None
            mhr_numbers: str = ''
            count = 0
            for mhr in mhr_list:
                mhr_number = mhr['mhr_number']
                count += 1
                if count > 1:
                    mhr_numbers += ','
                mhr_numbers += f"'{mhr_number}'"
            query = text(build_account_query(params, mhr_numbers, doc_types))
            if params.has_filter() and params.filter_reg_start_date and params.filter_reg_end_date:
                start_ts = model_utils.search_ts_local(params.filter_reg_start_date, True)
                end_ts = model_utils.search_ts_local(params.filter_reg_end_date, False)
                result = db.get_engine(current_app, 'db2').execute(query,
                                                                   {'query_start': start_ts, 'query_end': end_ts})
            else:
                result = db.get_engine(current_app, 'db2').execute(query)
            rows = result.fetchall()
            if rows is not None:
                for row in rows:
                    results.append(__build_summary(row, False, mhr_list))
            for result in results:
                __update_summary_info(result, results, reg_summary_list, params.sbc_staff, params.account_id)
                if not params.collapse:
                    del result['documentType']  # Not in the schema.
            if results and params.collapse:
                results = __collapse_results(results)
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB2 find_all_by_account_id exception: ' + str(db_exception))
            raise DatabaseException(db_exception)
    return results


def get_doc_id_count(doc_id: str) -> int:
    """Execute a query to count existing document id (must not exist check)."""
    try:
        query = text(DOC_ID_COUNT_QUERY)
        result = db.get_engine(current_app, 'db2').execute(query, {'query_value': doc_id})
        row = result.first()
        exist_count = int(row[0])
        current_app.logger.debug(f'Existing doc id count={exist_count}.')
        return exist_count
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('DB2 get_doc_id_count exception: ' + str(db_exception))
        raise DatabaseException(db_exception)


def get_db2_permit_count(mhr_number: str, name: str) -> int:
    """Execute a query to count existing transport permit registrations on a home."""
    try:
        query = text(PERMIT_COUNT_QUERY)
        query_name = name[0:40]
        result = db.get_engine(current_app, 'db2').execute(query,
                                                           {'query_value1': mhr_number, 'query_value2': query_name})
        row = result.first()
        exist_count = int(row[0])
        current_app.logger.debug(f'Existing transport permit count={exist_count}.')
        return exist_count
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('DB2 get_permit_count exception: ' + str(db_exception))
        raise DatabaseException(db_exception)


def find_by_mhr_number(mhr_number: str):
    """Return the registration matching the MHR number."""
    return Db2Manuhome.find_by_mhr_number(mhr_number)


def find_original_by_mhr_number(mhr_number: str):
    """Return the registration matching the MHR number."""
    return Db2Manuhome.find_original_by_mhr_number(mhr_number)


def find_by_document_id(document_id: str):
    """Return the registration matching the MHR number."""
    return Db2Manuhome.find_by_document_id(document_id)


def build_account_query(params: AccountRegistrationParams, mhr_numbers: str, doc_types) -> str:
    """Build the account registration summary query."""
    query_text: str = QUERY_ACCOUNT_REGISTRATIONS
    if not params.has_filter() and not params.has_sort():
        query_text = query_text.replace('?', mhr_numbers)
        current_app.logger.info('Executing query for mhr numbers=' + mhr_numbers)
    else:
        query_text = QUERY_ACCOUNT_REGISTRATIONS_SORT
        order_clause: str = ''
        if params.has_filter():
            query_text = build_account_query_filter(query_text, params, mhr_numbers, doc_types)
        else:
            query_text = query_text.replace('?', mhr_numbers)
        if params.has_sort():
            order_clause = QUERY_ACCOUNT_ORDER_BY.get(params.sort_criteria)
            if params.sort_criteria == reg_utils.REG_TS_PARAM:
                if params.sort_direction and params.sort_direction == reg_utils.SORT_ASCENDING:
                    order_clause = order_clause.replace(SORT_DESCENDING, SORT_ASCENDING)
            elif params.sort_direction and params.sort_direction == reg_utils.SORT_ASCENDING:
                order_clause += SORT_ASCENDING
            else:
                order_clause += SORT_DESCENDING
            query_text += order_clause
        else:  # Default sort order if filter but no sorting specified.
            query_text += DEFAULT_SORT_ORDER
    # current_app.logger.info(query_text)
    return query_text


def get_multiple_filters(params: AccountRegistrationParams) -> dict:
    """Build the list of all applied filters as a key/value dictionary."""
    filters = []
    if params.filter_mhr_number:
        filters.append(('mhrNumber', params.filter_mhr_number))
    if params.filter_registration_type:
        filters.append(('registrationType', params.filter_registration_type))
    if params.filter_reg_start_date:
        filters.append(('startDateTime', params.filter_reg_start_date))
    if params.filter_status_type:
        filters.append(('statusType', params.filter_status_type))
    if params.filter_client_reference_id:
        filters.append(('clientReferenceId', params.filter_client_reference_id))
    if params.filter_submitting_name:
        filters.append(('submittingName', params.filter_submitting_name))
    if params.filter_username:
        filters.append(('username', params.filter_username))
    if filters:
        return filters
    return None


def build_account_query_filter(query_text: str, params: AccountRegistrationParams, mhr_numbers: str, doc_types) -> str:
    """Build the account registration summary query filter clause."""
    filter_clause: str = ''
    # Get all selected filters and loop through, applying them
    filters = get_multiple_filters(params)
    for filter in filters:
        filter_type = filter[0]
        filter_value = filter[1]
        if filter_type and filter_value:
            if filter_type == reg_utils.MHR_NUMBER_PARAM:
                query_text = query_text.replace('?', f"'{filter_value}'")
            else:
                query_text = query_text.replace('?', mhr_numbers)
                # Filter may exclude parent MH registrations, so use a different query to include base registrations.
                filter_clause = QUERY_ACCOUNT_FILTER_BY_COLLAPSE.get(filter_type)
                if not params.collapse:
                    filter_clause = QUERY_ACCOUNT_FILTER_BY.get(filter_type)
                if filter_clause:
                    if filter_type == reg_utils.REG_TYPE_PARAM:
                        filter_clause = __get_reg_type_filter(filter_value, params.collapse, doc_types)
                    elif filter_type == reg_utils.STATUS_PARAM:
                        filter_clause = filter_clause.replace('?', TO_LEGACY_STATUS.get(filter_value, 'R'))
                    elif filter_type != reg_utils.START_TS_PARAM:
                        filter_clause = filter_clause.replace('?', filter_value)
                    query_text += filter_clause
    return query_text


def __get_reg_type_filter(filter_value: str, collapse: bool, doc_types) -> dict:
    """Get the legacy document type from the filter value."""
    new_doc_type: str = 'REG_101'
    for doc_rec in doc_types:
        if filter_value == doc_rec.document_type_desc:
            new_doc_type = doc_rec.document_type
            break
    doc_type: str = TO_LEGACY_DOC_TYPE.get(new_doc_type, new_doc_type)
    if len(doc_type) == 3:
        doc_type += ' '
    if collapse:
        return REG_FILTER_REG_TYPE_COLLAPSE.replace('?', doc_type)
    return REG_FILTER_REG_TYPE.replace('?', doc_type)


def __get_mhr_list(account_id: str) -> dict:
    """Build a list of mhr numbers associated with the account."""
    mhr_list = []
    try:
        query = text(QUERY_ACCOUNT_MHR_LEGACY)
        result = db.session.execute(query, {'query_value': account_id})
        rows = result.fetchall()
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('get_mhr_list db exception: ' + str(db_exception))
        raise DatabaseException(db_exception)
    if rows is not None:
        for row in rows:
            reg = {
                'mhr_number': str(row[0]),
                'account_reg': str(row[1]),
                'lien_registration_type': str(row[2]) if row[2] else ''
            }
            mhr_list.append(reg)
    return mhr_list


def __get_reg_summary_list(account_id: str) -> dict:
    """Build a registration summary list of new application registrations associated with the account."""
    summary_list = []
    try:
        query = text(QUERY_ACCOUNT_REGISTRATIONS_SUMMARY)
        result = db.session.execute(query, {'query_value': account_id})
        rows = result.fetchall()
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('__get_summary_list db exception: ' + str(db_exception))
        raise DatabaseException(db_exception)
    if rows is not None:
        # SELECT mr.id, mr.registration_ts, mr.account_id, mr.registration_type, mr.mhr_number, mr.document_id,
        #       mrr.create_ts as doc_ts, mrr.doc_storage_url, mrt.registration_type_desc
        for row in rows:
            reg = {
                'id': int(row[0]),
                'create_ts': row[1],
                'account_id': str(row[2]),
                'registration_type': str(row[3]),
                'mhr_number': str(row[4]),
                'document_id': str(row[5]),
                'report_ts': row[6],
                'report_url': str(row[7]),
                'reg_description': str(row[8]),
                'username': str(row[9])
            }
            summary_list.append(reg)
    return summary_list


def __get_owner_names(result, results) -> str:
    """Get owner names from the most recent registration matching the mhr number."""
    names = ''
    for reg in results:
        if reg['mhrNumber'] == result['mhrNumber'] and reg['documentId'] != result['documentId'] and \
                reg.get('ownerNames'):
            return reg['ownerNames']
    return names


def __get_summary_result(result, reg_summary_list) -> dict:
    """Get a new appliction summary result that matches on mhr number and docment id."""
    match = {}
    if not reg_summary_list:
        return match
    mhr_num = result.get('mhrNumber')
    doc_id = str(result.get('documentId')).strip()
    for reg in reg_summary_list:
        reg_mhr_num = reg.get('mhr_number')
        reg_doc_id = reg.get('document_id')
        if reg_mhr_num == mhr_num and reg_doc_id == doc_id:
            match = reg
            break
    return match


def __update_summary_info(result, results, reg_summary_list, staff, account_id):
    """Update summary information with new application matches."""
    # Some registrations may have no owner change: use the previous owner names.
    if not result.get('ownerNames'):
        result['ownerNames'] = __get_owner_names(result, results)
    summary_result = __get_summary_result(result, reg_summary_list)
    if not summary_result:
        doc_type = result.get('documentType')
        if FROM_LEGACY_DOC_TYPE.get(doc_type):
            doc_type = FROM_LEGACY_DOC_TYPE[doc_type]
        result['registrationDescription'] = get_doc_desc(doc_type)
        if TO_REGISTRATION_TYPE.get(doc_type):
            result['registrationType'] = TO_REGISTRATION_TYPE.get(doc_type)
        else:
            result['registrationType'] = TO_REGISTRATION_TYPE.get('DEFAULT')
    else:
        result['registrationType'] = summary_result.get('registration_type')
        if result['registrationType'] == MhrRegistrationTypes.REG_NOTE:
            doc_type = result.get('documentType')
            if FROM_LEGACY_DOC_TYPE.get(doc_type):
                doc_type = FROM_LEGACY_DOC_TYPE[doc_type]
            result['registrationDescription'] = get_doc_desc(doc_type)
        else:
            result['registrationDescription'] = summary_result.get('reg_description')
        # result['username'] = summary_result.get('username')  # Sorting by username does not work with this.
        if staff or account_id == summary_result.get('account_id'):
            if summary_result.get('report_url') or model_utils.report_retry_elapsed(summary_result.get('report_ts')):
                if summary_result.get('registration_type') == MhrRegistrationTypes.MHREG:
                    result['path'] = REGISTRATION_PATH + result.get('mhrNumber')
                else:
                    result['path'] = DOCUMENT_PATH + result.get('documentId')


def __build_summary(row, add_in_user_list: bool = True, mhr_list=None):
    """Build registration summary from query result."""
    mhr_number = str(row[0])
    # current_app.logger.info(f'summary mhr#={mhr_number}')
    timestamp = row[2]
    owners = str(row[6]) if row[6] else None
    owner_names = ''
    if owners:
        owners = owners.replace('<owner>', '')
        owners = owners.replace('</owner>', '\n')
        owner_list = owners.split('\n')
        for name in owner_list:
            if name.strip() != '':
                if name[0:1] == OWNER_TYPE_INDIVIDUAL:
                    owner_names += __get_summary_name(name[1:]) + ',\n'
                else:
                    owner_names += name[1:] + ',\n'
        # remove comma if exists at end of str
        if owner_names[-2] == ',':
            owner_names = owner_names[:-2]
    summary = {
        'mhrNumber': mhr_number,
        'registrationDescription': LEGACY_REGISTRATION_DESCRIPTION.get(str(row[5]),
                                                                       REGISTRATION_DESC_NEW),
        'username': str(row[7]),
        'statusType': LEGACY_STATUS_DESCRIPTION.get(str(row[1])),
        'createDateTime': model_utils.format_local_ts(timestamp),
        'submittingParty': str(row[3]),
        'clientReferenceId': str(row[4]),
        'ownerNames': owner_names,
        'path': '',
        'documentId': str(row[8]),
        'documentRegistrationNumber': str(row[9]),
        'documentType': str(row[5])
    }
    last_doc_type: str = str(row[10])
    if last_doc_type == DOCUMENT_TYPE_AFFIDAVIT:
        summary['statusType'] = REG_STATUS_FROZEN
    if add_in_user_list:
        summary['inUserList'] = False
    if mhr_list and summary['documentType'] in (Db2Document.DocumentTypes.CONV, Db2Document.DocumentTypes.MHREG_TRIM):
        summary['lienRegistrationType'] = __get_lien_registration_type(mhr_number, mhr_list)
    elif summary['documentType'] == MhrDocumentTypes.NCAN:
        summary = __get_cancel_info(summary, row)
    elif summary['documentType'] in (MhrDocumentTypes.CAU, MhrDocumentTypes.CAUC, MhrDocumentTypes.CAUE):
        summary = __get_caution_info(summary, row)
    return summary


def __get_caution_info(summary: dict, row) -> dict:
    """Add expireDays to summary for CAU, CAUC, CAUE document types."""
    status: str = str(row[11]) if row[11] else None
    if status and status == 'C':
        summary['expireDays'] = CAUTION_CANCELLED_DAYS  # Cancelled.
    else:
        expiry = row[12] if row[12] else None
        if (not expiry or expiry.isoformat() == '0001-01-01') and \
                summary.get('documentType') == MhrDocumentTypes.CAUC:
            summary['expireDays'] = CAUTION_INDEFINITE_DAYS  # Indefinite expiry.
        elif expiry and expiry.isoformat() != '0001-01-01':
            summary['expireDays'] = model_utils.expiry_date_days(expiry)
    return summary


def __get_cancel_info(summary: dict, row) -> dict:
    """For registrations with the NCAN document type get the cancelled note type and description."""
    doc_type: str = str(row[13]) if row[13] else None
    if doc_type:
        summary['cancelledDocumentType'] = doc_type.strip()
        summary['cancelledDocumentDescription'] = get_doc_desc(doc_type.strip())
    return summary


def __collapse_results(results):
    """Organized reults as parent-children mh registration-change registrations."""
    registrations = []
    for result in results:
        if result['documentType'] in (Db2Document.DocumentTypes.CONV, Db2Document.DocumentTypes.MHREG_TRIM):
            registrations.append(result)
    for reg in registrations:
        del reg['documentType']
        has_caution: bool = False
        changes = []
        for result in results:
            if result['mhrNumber'] == reg['mhrNumber'] and result['documentId'] != reg['documentId']:
                del result['documentType']
                if result.get('expireDays') and result.get('expireDays') >= 0:
                    has_caution = True
                changes.append(result)
        if changes:
            reg['changes'] = changes
        reg['hasCaution'] = has_caution
    return registrations


def __get_summary_name(db2_name: str):
    """Get an individual name json from a DB2 legacy name."""
    last = db2_name[0:24].strip()
    first = db2_name[25:].strip()
    middle = None
    if len(db2_name) > 40:
        first = db2_name[25:38].strip()
        middle = db2_name[39:].strip()
    if middle:
        return first + ' ' + middle + ' ' + last
    return first + ' ' + last


def __get_lien_registration_type(mhr_number: str, mhr_list) -> str:
    """Get the PPR registration type for the mhr number if an outstanding lien exists."""
    if not mhr_number or not mhr_list:
        return ''
    for reg in mhr_list:
        if mhr_number == reg.get('mhr_number'):
            return reg.get('lien_registration_type')
    return ''


def get_pid_list() -> dict:
    """Build a list of pid numbers for active registrations with no existing legal description."""
    pid_list = []
    try:
        query = text(QUERY_LTSA_PID)
        result = db.get_engine(current_app, 'db2').execute(query)
        rows = result.fetchall()
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('get_pid_list db exception: ' + str(db_exception))
        raise DatabaseException(db_exception)
    if rows is not None:
        for row in rows:
            pid = {
                'pidNumber': str(row[0])
            }
            pid_list.append(pid)
    return pid_list


def update_pid_list(pid_list, status: str):
    """Mark a pid numbers to be excluded in future queries by assigning a status."""
    if not pid_list or not status:
        return
    try:
        pid_numbers: str = ''
        count = 0
        for pid in pid_list:
            pid_number = pid['pidNumber']
            count += 1
            if count > 1:
                pid_numbers += ','
            pid_numbers += f"'{pid_number}'"
        query_text: str = UPDATE_LTSA_PID.replace('?', pid_numbers)
        # current_app.logger.info('update query=' + query_text)
        query = text(query_text)
        db.get_engine(current_app, 'db2').execute(query, {'status_value': status})
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('update_pid_list db exception: ' + str(db_exception))
        raise DatabaseException(db_exception)


def get_doc_desc(doc_type) -> str:
    """Try to find the document description by document type."""
    if doc_type:
        doc_type_info: MhrDocumentType = MhrDocumentType.find_by_doc_type(doc_type)
        if doc_type_info:
            return doc_type_info.document_type_desc
    return ''


def get_registration_json(registration):
    """Build the registration json from bot DB2 and PosgreSQL."""
    reg_json = registration.manuhome.json
    doc_type = reg_json.get('documentType')
    if FROM_LEGACY_NOTE_REG_TYPE.get(doc_type):
        reg_json['registrationType'] = FROM_LEGACY_NOTE_REG_TYPE.get(doc_type)
    elif FROM_LEGACY_REGISTRATION_TYPE.get(doc_type):
        reg_json['registrationType'] = FROM_LEGACY_REGISTRATION_TYPE.get(doc_type)
    if FROM_LEGACY_DOC_TYPE.get(doc_type):
        doc_type = FROM_LEGACY_DOC_TYPE.get(doc_type)
    reg_json['documentDescription'] = get_doc_desc(doc_type)
    reg_json = registration.set_submitting_json(reg_json)  # For MHR registrations use MHR submitting party data.
    reg_json = registration.set_location_json(reg_json, False)   # For MHR registrations use MHR location data.
    reg_json = registration.set_description_json(reg_json, False)  # For MHR registrations use MHR description data.
    if reg_json.get('documentType'):
        del reg_json['documentType']
    current_app.logger.debug('Built JSON from DB2 and PostgreSQL')
    if registration.pay_invoice_id and registration.pay_invoice_id > 0:  # Legacy will have no payment info.
        return registration.set_payment_json(reg_json)
    return reg_json


def get_search_json(registration):
    """Build the search version of the registration as a json object."""
    reg_json = registration.manuhome.registration_json
    if reg_json and reg_json.get('notes'):
        updated_notes = []
        for note in reg_json.get('notes'):
            include: bool = True
            doc_type = note.get('documentType', '')
            current_app.logger.debug('updating doc type=' + doc_type)
            if doc_type in ('103', '103E', 'STAT'):  # Always exclude
                include = False
            elif not registration.staff and doc_type in ('102', 'NCON'):  # Always exclude for non-staff
                include = False
            elif not registration.staff and doc_type == 'FZE':  # Only staff can see remarks.
                note['remarks'] = ''
            elif not registration.staff and doc_type == 'REGC' and note.get('remarks') and \
                    note['remarks'] != 'MANUFACTURED HOME REGISTRATION CANCELLED':
                # Only staff can see remarks if not default.
                note['remarks'] = 'MANUFACTURED HOME REGISTRATION CANCELLED'
            elif doc_type in ('TAXN', 'EXNR', 'EXRS', 'NPUB', 'REST', 'CAU', 'CAUC', 'CAUE') and \
                    note.get('status') != MhrNoteStatusTypes.ACTIVE:  # Exclude if not active.
                include = False
            elif doc_type in ('CAU', 'CAUC', 'CAUE') and note.get('expiryDateTime') and \
                    model_utils.date_elapsed(note.get('expiryDateTime')):  # Exclude if expiry elapsed.
                include = reg_utils.include_caution_note(reg_json.get('notes'), note.get('documentId'))
            if doc_type == 'FZE':  # Do not display contact info.
                if note.get('givingNoticeParty'):
                    del note['givingNoticeParty']
            if include:
                if FROM_LEGACY_DOC_TYPE.get(doc_type):
                    doc_type = FROM_LEGACY_DOC_TYPE.get(doc_type)
                note['documentDescription'] = get_doc_desc(doc_type)
                note = update_note_json(registration, note)
                updated_notes.append(note)
        reg_json['notes'] = updated_notes
    reg_json = registration.set_location_json(reg_json, True)
    reg_json = registration.set_description_json(reg_json, True)
    current_app.logger.debug('Built JSON from DB2 and PostgreSQL')
    return reg_json


def get_new_registration_json(registration):
    """Build the new registration version of the registration as a json object."""
    registration.manuhome.current_view = registration.current_view
    registration.manuhome.staff = registration.staff
    reg_json = registration.manuhome.new_registration_json
    reg_doc = None
    doc_type = ''
    for doc in registration.manuhome.reg_documents:
        if registration.manuhome.reg_document_id and registration.manuhome.reg_document_id == doc.id:
            reg_doc = doc
    if reg_doc:
        doc_type = reg_doc.document_type
        if FROM_LEGACY_NOTE_REG_TYPE.get(doc_type):
            reg_json['registrationType'] = FROM_LEGACY_NOTE_REG_TYPE.get(doc_type)
        elif FROM_LEGACY_REGISTRATION_TYPE.get(doc_type):
            reg_json['registrationType'] = FROM_LEGACY_REGISTRATION_TYPE.get(doc_type)
        if FROM_LEGACY_DOC_TYPE.get(doc_type):
            doc_type = FROM_LEGACY_DOC_TYPE.get(doc_type)
    reg_json['documentDescription'] = get_doc_desc(doc_type)
    reg_json = registration.set_submitting_json(reg_json)
    reg_json = registration.set_location_json(reg_json, False)
    reg_json = registration.set_description_json(reg_json, False)
    if reg_json.get('notes'):
        for note in reg_json.get('notes'):
            note_doc_type: str = note.get('documentType')
            if FROM_LEGACY_DOC_TYPE.get(note_doc_type):
                note_doc_type = FROM_LEGACY_DOC_TYPE.get(note_doc_type)
                note['documentType'] = note_doc_type
            note['documentDescription'] = get_doc_desc(note_doc_type)
            if note.get('cancelledDocumentType'):
                note['cancelledDocumentDescription'] = get_doc_desc(note.get('cancelledDocumentType'))
            note = update_note_json(registration, note)
    current_app.logger.debug('Built JSON from DB2 and PostgreSQL')
    return registration.set_payment_json(reg_json)


def get_next_mhr_number() -> str:
    """Get next MHR number from the legacy number series."""
    try:
        query1 = text(NEXT_MHR_NUM_SELECT_FOR_UPDATE)
        result = db.get_engine(current_app, 'db2').execute(query1)
        #                                                   {'query_value1': mhr_number, 'query_value2': query_name})
        row = result.first()
        next_mhr: int = int(row[0]) + 1
        query2 = text(NEXT_MHR_NUM_UPDATE)
        result = db.get_engine(current_app, 'db2').execute(query2, {'query_val': next_mhr})
        db.session.commit()
        mhr_number: str = str(next_mhr)
        current_app.logger.debug(f'New MHR number={mhr_number}.')
        return mhr_number
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('DB2 get_next_mhr_number exception: ' + str(db_exception))
        raise DatabaseException(db_exception)


def update_note_json(registration, note_json: dict) -> dict:
    """Conditionally update the note json with new registration data if available."""
    if not registration.change_registrations:
        return note_json
    for reg in registration.change_registrations:
        if reg.notes:
            doc = reg.documents[0]
            if doc.document_id == note_json.get('documentId'):
                note_json['createDateTime'] = model_utils.format_ts(reg.registration_ts)
                note = reg.notes[0]
                if note.expiry_date:
                    note_json['expiryDateTime'] = model_utils.format_ts(note.expiry_date)
                if note.effective_ts:
                    note_json['effectiveDateTime'] = model_utils.format_ts(note.effective_ts)
                if note.document_type == MhrDocumentTypes.NCAN:
                    note_json['remarks'] = note.remarks
    return note_json
