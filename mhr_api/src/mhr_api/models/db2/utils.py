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
from mhr_api.models import Db2Manuhome, utils as model_utils
from mhr_api.models.db import db


QUERY_ACCOUNT_MHR_LEGACY = """
SELECT mer.mhr_number, 'N' AS account_reg,
       (SELECT COUNT(mrr.id)
           FROM mhr_registrations mr, mhr_registration_reports mrr
          WHERE mr.mhr_number = mer.mhr_number
            AND mr.id = mrr.registration_id
            AND mrr.doc_storage_url IS NOT NULL) AS report_count,
      null as registration_ts
 FROM mhr_extra_registrations mer
WHERE account_id = :query_value
  AND (removed_ind IS NULL OR removed_ind != 'Y')
UNION (
SELECT mr.mhr_number, 'Y' AS account_reg,
       (SELECT COUNT(mrr.id)
           FROM mhr_registration_reports mrr
          WHERE mr.id = mrr.registration_id
            AND mrr.doc_storage_url IS NOT NULL) AS report_count,
       mr.registration_ts
  FROM mhr_registrations mr
WHERE account_id = :query_value
)
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
            AND mer.mhr_number = :query_value2) as extra_reg_count
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
       TRIM(d.bcolacct)
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
           AND og2.status IN ('3', '4')) as owner_names,
       TRIM(d.bcolacct)
  FROM manuhome mh, document d
 WHERE mh.mhregnum IN (?)
   AND mh.mhregnum = d.mhregnum
   AND mh.regdocid = d.documtid
ORDER BY d.regidate DESC
"""
REGISTRATION_DESC_NEW = 'Manufactured Home Registration'
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
                registration = __build_summary(row, staff, None, True)
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
            current_app.logger.debug(f'reg_count={reg_count}, extra_cout={extra_count}, staff={staff}')
            # Set inUserList to true if MHR number already added to account extra registrations.
            if reg_count > 0 or extra_count > 0:
                registration['inUserList'] = True
            # Path to download report only available for staff and registrations created by the account.
            if staff or reg_count > 0:
                registration['path'] = REGISTRATION_PATH + mhr_number
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('find_summary_by_mhr_number mhr extra check exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

    return registration


def find_all_by_account_id(account_id: str, staff: bool):
    """Return a summary list of recent MHR registrations belonging to an account."""
    results = []
    # 1. get account and extra registrations from the Posgres table, then query DB2 by set of mhr numbers.
    try:
        query = text(QUERY_ACCOUNT_MHR_LEGACY)
        result = db.session.execute(query, {'query_value': account_id})
        rows = result.fetchall()
    except Exception as db_exception:   # noqa: B902; return nicer error
        current_app.logger.error('find_all_by_account_id mhr list exception: ' + str(db_exception))
        raise DatabaseException(db_exception)
    mhr_list = []
    if rows is not None:
        for row in rows:
            reg = {
                'mhr_number': str(row[0]),
                'account_reg': str(row[1]),
                'rep_count': int(row[2]),
                'reg_ts': row[3]
            }
            mhr_list.append(reg)
    if mhr_list:
        # 2. Get the summary info from DB2.
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
            # current_app.logger.debug('Executing query=' + query_text)
            query = text(query_text)
            result = db.get_engine(current_app, 'db2').execute(query)
            rows = result.fetchall()
            if rows is not None:
                for row in rows:
                    results.append(__build_summary(row, staff, mhr_list, False))
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


def find_by_document_id(document_id: str):
    """Return the registration matching the MHR number."""
    return Db2Manuhome.find_by_document_id(document_id)


def __build_summary(row, staff: bool, mhr_list: dict, add_in_user_list: bool = True):
    """Build registration summary from query result."""
    mhr_number = str(row[0])
    # current_app.logger.info(f'summary mhr#={mhr_number}')
    timestamp = row[2]
    owners = str(row[6])
    owners = owners.replace('<owner>', '')
    owners = owners.replace('</owner>', '\n')
    owner_list = owners.split('\n')
    owner_names = ''
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
        'path': ''
    }
    if add_in_user_list:
        summary['inUserList'] = False
    # Update report path if report generated: staff can always access.
    if mhr_list:
        for reg in mhr_list:
            if reg['mhr_number'] == summary.get('mhrNumber') and (staff or reg.get('account_reg') == 'Y'):
                # Either reg report exists or enough time has elapsed to retry.
                if reg.get('rep_count') > 0 or \
                        (reg.get('reg_ts') and model_utils.report_retry_elapsed(reg.get('reg_ts'))):
                    summary['path'] = REGISTRATION_PATH + summary.get('mhrNumber')
    return summary


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
