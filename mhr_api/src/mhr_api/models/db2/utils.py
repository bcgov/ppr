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
from mhr_api.models import Db2Manuhome, Db2Document, utils as model_utils
from mhr_api.models.type_tables import MhrDocumentType, MhrRegistrationTypes
from mhr_api.models.db import db


FROM_LEGACY_DOC_TYPE = {
    '101': 'REG_101',
    '102': 'REG_102',
    '103': 'REG_103',
    '103E': 'REG_103E'
}

QUERY_ACCOUNT_MHR_LEGACY = """
SELECT DISTINCT mer.mhr_number, 'N' AS account_reg
 FROM mhr_extra_registrations mer
WHERE account_id = :query_value
  AND (removed_ind IS NULL OR removed_ind != 'Y')
UNION (
SELECT DISTINCT mr.mhr_number, 'Y' AS account_reg
  FROM mhr_registrations mr
WHERE account_id = :query_value
  AND mr.registration_type = 'MHREG'
)
"""
QUERY_ACCOUNT_REGISTRATIONS_SUMMARY = """
SELECT mr.id, mr.registration_ts, mr.account_id, mr.registration_type, mr.mhr_number, mr.document_id,
       mrr.create_ts as doc_ts, mrr.doc_storage_url, mrt.registration_type_desc,
       (SELECT CASE WHEN mr.user_id IS NULL THEN ''
          ELSE (SELECT u.firstname || ' ' || u.lastname FROM users u WHERE u.username = mr.user_id)
           END) AS username
  FROM mhr_registrations mr, mhr_registration_reports mrr, mhr_registration_types mrt
 WHERE mr.mhr_number IN (SELECT DISTINCT mer.mhr_number
                           FROM mhr_extra_registrations mer
                          WHERE account_id = :query_value
                            AND (removed_ind IS NULL OR removed_ind != 'Y')
                          UNION (
                         SELECT DISTINCT mr.mhr_number
                           FROM mhr_registrations mr
                          WHERE account_id = :query_value
                            AND mr.registration_type = 'MHREG'))
  and mr.id = mrr.registration_id
  and mrt.registration_type = mr.registration_type
order by mr.id desc
"""
QUERY_MHR_NUMBER_LEGACY = """
SELECT (SELECT COUNT(mr.id)
           FROM mhr_registrations mr
          WHERE mr.account_id = :query_value
            AND mr.mhr_number = :query_value2
            AND mr.registration_type IN ('MHREG')) AS reg_count,
       (SELECT COUNT(mer.id)
           FROM mhr_extra_registrations mer
          WHERE mer.account_id = :query_value
            AND mer.mhr_number = :query_value2) as extra_reg_count,
       (SELECT  mr.account_id
           FROM mhr_registrations mr
          WHERE mr.account_id = :query_value
            AND mr.mhr_number = :query_value2
            AND mr.registration_type IN ('MHREG'))
"""
DOC_ID_COUNT_QUERY = """
SELECT COUNT(documtid)
  FROM document
 WHERE documtid = :query_value
"""
QUERY_ACCOUNT_ADD_REGISTRATION = """
SELECT mh.mhregnum, mh.mhstatus, d.regidate, TRIM(d.name), TRIM(d.olbcfoli), TRIM(d.docutype),
       (SELECT XMLSERIALIZE(XMLAGG ( XMLELEMENT ( NAME "owner", o2.ownrtype || TRIM(o2.ownrname))) AS CLOB)
          FROM owner o2, owngroup og2
         WHERE o2.manhomid = mh.manhomid
           AND og2.manhomid = mh.manhomid
           AND og2.owngrpid = o2.owngrpid
           AND og2.status IN ('3', '4')) as owner_names,
       TRIM(d.bcolacct),
       d.documtid as document_id
  FROM manuhome mh, document d
 WHERE mh.mhregnum = :query_mhr_number
   AND mh.mhregnum = d.mhregnum
   AND mh.regdocid = d.documtid
"""
QUERY_ACCOUNT_REGISTRATIONS = """
SELECT mh.mhregnum, mh.mhstatus, d.regidate, TRIM(d.name), TRIM(d.olbcfoli), TRIM(d.docutype),
       (SELECT XMLSERIALIZE(XMLAGG ( XMLELEMENT ( NAME "owner", o2.ownrtype || TRIM(o2.ownrname))) AS CLOB)
          FROM owner o2, owngroup og2
         WHERE o2.manhomid = mh.manhomid
           AND og2.manhomid = mh.manhomid
           AND og2.owngrpid = o2.owngrpid
           AND og2.regdocid = d.documtid) as owner_names,
       TRIM(d.affirmby),
       d.documtid as document_id
  FROM manuhome mh, document d
 WHERE mh.mhregnum IN (?)
   AND mh.mhregnum = d.mhregnum
ORDER BY mh.updateda DESC, mh.updateti DESC, d.regidate DESC
"""
REGISTRATION_DESC_NEW = 'REGISTER NEW UNIT'
LEGACY_STATUS_DESCRIPTION = {
    'R': 'ACTIVE',
    'E': 'EXEMPT',
    'D': 'DRAFT',
    'C': 'HISTORICAL'
}
LEGACY_REGISTRATION_DESCRIPTION = {
    '101': REGISTRATION_DESC_NEW,
    'CONV': REGISTRATION_DESC_NEW
}
DOCUMENT_TYPE_REG = '101'
OWNER_TYPE_INDIVIDUAL = 'I'
REGISTRATION_PATH = '/mhr/api/v1/registrations/'
DOCUMENT_PATH = '/mhr/api/v1/documents/'


def find_by_id(registration_id: int):
    """Return the legacy registration matching the id."""
    if registration_id:
        return Db2Manuhome.find_by_id(registration_id)
    return None


def find_summary_by_mhr_number(account_id: str, mhr_number: str, staff: bool):
    """Return the MHR registration summary information matching the registration number."""
    registration = None
    try:
        query = text(QUERY_ACCOUNT_ADD_REGISTRATION)
        result = db.get_engine(current_app, 'db2').execute(query, {'query_mhr_number': mhr_number})
        rows = result.fetchall()
        if rows is not None:
            for row in rows:
                registration = __build_summary(row, True)
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('DB2 find_summary_by_mhr_number exception: ' + str(db_exception))
        raise DatabaseException(db_exception)

    if registration:
        try:
            query = text(QUERY_MHR_NUMBER_LEGACY)
            result = db.session.execute(query, {'query_value': account_id, 'query_value2': mhr_number})
            row = result.first()
            reg_count = int(row[0])
            extra_count = int(row[1])
            reg_account_id = str(row[2])
            current_app.logger.debug(f'reg_count={reg_count}, extra_count={extra_count}, staff={staff}')
            # Set inUserList to true if MHR number already added to account extra registrations.
            if reg_count > 0 or extra_count > 0:
                registration['inUserList'] = True
            # Path to download report only available for staff and registrations created by the account.
            if reg_count > 0 and (staff or account_id == reg_account_id):
                registration['path'] = REGISTRATION_PATH + mhr_number
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('find_summary_by_mhr_number mhr extra check exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

    return registration


def find_all_by_account_id(account_id: str, staff: bool, collapse: bool = False):
    """Return a summary list of recent MHR registrations belonging to an account."""
    results = []
    # 1. get account and extra registrations from the Posgres table, then query DB2 by set of mhr numbers.
    mhr_list = __get_mhr_list(account_id)
    # 2 Get summary list of new application registrations.
    reg_summary_list = __get_reg_summary_list(account_id)
    doc_types = MhrDocumentType.find_all()
    if mhr_list:
        # 3. Get the summary info from DB2.
        try:
            mhr_numbers: str = ''
            count = 0
            for mhr in mhr_list:
                mhr_number = mhr['mhr_number']
                count += 1
                if count > 1:
                    mhr_numbers += ','
                mhr_numbers += f"'{mhr_number}'"
            query_text = QUERY_ACCOUNT_REGISTRATIONS.replace('?', mhr_numbers)
            current_app.logger.info('Executing query for mhr numbers=' + mhr_numbers)
            query = text(query_text)
            result = db.get_engine(current_app, 'db2').execute(query)
            rows = result.fetchall()
            if rows is not None:
                for row in rows:
                    results.append(__build_summary(row, False))
            for result in results:
                __update_summary_info(result, results, reg_summary_list, doc_types, staff, account_id)
                if not collapse:
                    del result['documentType']  # Not in the schema.
            if results and collapse:
                results = __collapse_results(results)
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB2 find_all_by_account_id exception: ' + str(db_exception))
            raise DatabaseException(db_exception)
    return results


def get_doc_id_count(doc_id: str):
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


def find_by_mhr_number(mhr_number: str):
    """Return the registration matching the MHR number."""
    return Db2Manuhome.find_by_mhr_number(mhr_number)


def find_original_by_mhr_number(mhr_number: str):
    """Return the registration matching the MHR number."""
    return Db2Manuhome.find_original_by_mhr_number(mhr_number)


def find_by_document_id(document_id: str):
    """Return the registration matching the MHR number."""
    return Db2Manuhome.find_by_document_id(document_id)


def __get_mhr_list(account_id: str) -> dict:
    """Build a list of mhr numbers associated with the account."""
    mhr_list = []
    try:
        query = text(QUERY_ACCOUNT_MHR_LEGACY)
        result = db.session.execute(query, {'query_value': account_id})
        rows = result.fetchall()
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('__get_mhr_list db exception: ' + str(db_exception))
        raise DatabaseException(db_exception)
    if rows is not None:
        for row in rows:
            reg = {
                'mhr_number': str(row[0]),
                'account_reg': str(row[1])
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
        if reg['mhrNumber'] == result['mhrNumber'] and reg['documentId'] != result['documentId']:
            return result['ownerNames']
    return names


def __get_summary_result(result, reg_summary_list) -> dict:
    """Get a new appliction summary result that matches on mhr number and docment id."""
    match = {}
    if not reg_summary_list:
        return match
    mhr_num = result.get('mhrNumber')
    doc_id = result.get('documentId')
    for reg in reg_summary_list:
        reg_mhr_num = reg.get('mhr_number')
        reg_doc_id = reg.get('document_id')
        if reg_mhr_num == mhr_num and reg.get('registration_type') == MhrRegistrationTypes.MHREG:
            match = reg
            break
        if reg_mhr_num == mhr_num and reg_doc_id == doc_id:
            match = reg
            break
    return match


def __update_summary_info(result, results, reg_summary_list, doc_types, staff, account_id):
    """Update summary information with new application matches."""
    # Some registrations may have no owner change: use the previous owner names.
    if not result.get('ownerNames'):
        result['ownerNames'] = __get_owner_names(result, results)
    summary_result = __get_summary_result(result, reg_summary_list)
    if not summary_result:
        doc_type = result.get('documentType')
        if FROM_LEGACY_DOC_TYPE.get(doc_type):
            doc_type = FROM_LEGACY_DOC_TYPE[doc_type]
        for doc_rec in doc_types:
            if doc_type == doc_rec.document_type:
                result['registrationDescription'] = doc_rec.document_type_desc
                break
    else:
        result['registrationDescription'] = summary_result.get('reg_description')
        result['username'] = summary_result.get('username')
        if staff or account_id == summary_result.get('account_id'):
            if summary_result.get('report_url') or model_utils.report_retry_elapsed(summary_result.get('report_ts')):
                if summary_result.get('registration_type') == MhrRegistrationTypes.MHREG:
                    result['path'] = REGISTRATION_PATH + result.get('mhrNumber')
                else:
                    result['path'] = DOCUMENT_PATH + result.get('documentId')


def __build_summary(row, add_in_user_list: bool = True):
    """Build registration summary from query result."""
    mhr_number = str(row[0])
    # current_app.logger.info(f'summary mhr#={mhr_number}')
    timestamp = row[2]
    owners = str(row[6])
    owner_names = ''
    if owners:
        owners = owners.replace('<owner>', '')
        owners = owners.replace('</owner>', '\n')
        owner_list = owners.split('\n')
        for name in owner_list:
            if name.strip() != '':
                if name[0:1] == OWNER_TYPE_INDIVIDUAL:
                    owner_names += __get_summary_name(name[1:]) + '\n'
                else:
                    owner_names += name[1:] + '\n'
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
        'documentType': str(row[5]),
    }
    if add_in_user_list:
        summary['inUserList'] = False
    return summary


def __collapse_results(results):
    """Organized reults as parent-children mh registration-change registrations."""
    registrations = []
    for result in results:
        if result['documentType'] in (Db2Document.DocumentTypes.CONV, Db2Document.DocumentTypes.MHREG_TRIM):
            registrations.append(result)
    for reg in registrations:
        del reg['documentType']
        changes = []
        for result in results:
            if result['mhrNumber'] == reg['mhrNumber'] and result['documentId'] != reg['documentId']:
                del result['documentType']
                changes.append(result)
        if changes:
            reg['changes'] = changes
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
