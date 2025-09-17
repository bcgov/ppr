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
"""This module holds PostgreSQL query strings."""


DOC_ID_COUNT_QUERY = """
SELECT COUNT(document_id)
  FROM mhr_documents
 WHERE document_id = :query_value
"""
MHR_CHECK_QUERY = """
SELECT MAX(mhr_number),
       (SELECT COUNT(id) FROM mhr_registrations WHERE mhr_number = :query_value)
  FROM mhr_registrations
 WHERE registration_type NOT IN ('MANUFACTURER')
"""
QUERY_BATCH_MANUFACTURER_MHREG_DEFAULT = """
select r.id, r.account_id, r.registration_ts, rr.id, rr.report_data, rr.batch_storage_url
  from mhr_registrations r, mhr_manufacturers m, mhr_registration_reports rr
 where r.id = rr.registration_id
   and r.account_id = m.account_id
   and r.registration_type = 'MHREG'
   and r.registration_ts between (now() - interval '1 days') and now()
  order by r.account_id, r.mhr_number
 """
QUERY_BATCH_MANUFACTURER_MHREG = """
select r.id, r.account_id, r.registration_ts, rr.id, rr.report_data, rr.batch_storage_url
  from mhr_registrations r, mhr_manufacturers m, mhr_registration_reports rr
 where r.id = rr.registration_id
   and r.account_id = m.account_id
   and r.registration_type = 'MHREG'
   and r.registration_ts between to_timestamp(:query_val1, 'YYYY-MM-DD HH24:MI:SS')
                             and to_timestamp(:query_val2, 'YYYY-MM-DD HH24:MI:SS')
  order by r.account_id, r.mhr_number
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
QUERY_PPR_REGISTRATION_TYPE = """
SELECT DISTINCT registration_type
  FROM mhr_lien_check_vw
 WHERE mhr_number = :query_value
"""
QUERY_PERMIT_COUNT = """
SELECT COUNT(r.id) AS permit_count
  FROM mhr_registrations r, mhr_parties p
 WHERE r.mhr_number = :query_value1
   AND r.registration_type = 'PERMIT'
   AND r.id = p.registration_id
   AND p.party_type = 'SUBMITTING'
   AND p.business_name = :query_value2
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
QUERY_REG_ID_PKEY = """
select nextval('mhr_registration_id_seq') AS reg_id
"""
QUERY_ACCOUNT_REG_BASE = """
SELECT arv.mhr_number, status_type, registration_ts, submitting_name, client_reference_id, registration_type,
       owner_names,
       registering_name, document_id, document_registration_number, last_doc_type, note_status, note_expiry,
       cancel_doc_type, frozen_doc_type, arv.account_id, document_type_desc, ppr_lien_type, document_type,
       doc_storage_url,
       (SELECT COUNT(mer.id)
          FROM mhr_extra_registrations mer
         WHERE mer.mhr_number = arv.mhr_number
           AND mer.account_id = arv.account_id
           AND (mer.removed_ind IS NOT NULL AND mer.removed_ind = 'Y')) AS removed_count,
       (SELECT COUNT(mer.id)
          FROM mhr_extra_registrations mer
         WHERE mer.mhr_number = arv.mhr_number
           AND mer.account_id = :query_value1
           AND mer.account_id != arv.account_id
           AND (mer.removed_ind IS NULL OR mer.removed_ind != 'Y')) AS extra_reg_count,
       location_type, affirm_by, report_count,
       CASE WHEN arv.account_id IN ('ppr_staff', 'helpdesk')
            THEN (SELECT u.account_id
                   FROM users u, mhr_registrations r
                  WHERE arv.registration_id = r.id
                    AND r.user_id = u.username
                 ORDER BY u.id DESC
                 FETCH FIRST 1 ROWS ONLY)
            ELSE NULL END staff_account_id,
       CASE WHEN arv.account_id != '0'
            THEN (SELECT d.draft_number
                   FROM mhr_drafts d, mhr_registrations r
                  WHERE arv.registration_id = r.id
                    AND r.draft_id = d.id)
            ELSE NULL END draft_number,
      manufacturer_name,
      civic_address
  FROM mhr_account_reg_vw arv
"""

QUERY_ACCOUNT_ADD_REG_MHR = (
    QUERY_ACCOUNT_REG_BASE
    + """
 WHERE mhr_number = :query_value2
ORDER BY registration_ts
"""
)
QUERY_ACCOUNT_ADD_REG_DOC = (
    QUERY_ACCOUNT_REG_BASE
    + """
 WHERE mhr_number = (SELECT r.mhr_number
                       FROM mhr_registrations r, mhr_documents d
                      WHERE r.id = d.registration_id
                        AND d.document_registration_number = :query_value2)
ORDER BY registration_ts
"""
)
QUERY_ACCOUNT_DEFAULT = (
    "SELECT * FROM ("
    + QUERY_ACCOUNT_REG_BASE
    + """ LEFT JOIN mhr_extra_registrations mer on mer.mhr_number = arv.mhr_number
 WHERE (:query_value1 = mer.account_id AND mer.mhr_number = arv.mhr_number AND mer.removed_ind IS NULL)
UNION ("""
    + QUERY_ACCOUNT_REG_BASE
    + """
 WHERE arv.account_id = :query_value1
    AND arv.mhr_number in (SELECT DISTINCT mr.mhr_number
                           FROM mhr_registrations mr
                          WHERE mr.account_id = :query_value1
                            AND mr.registration_type = 'MHREG'
                            AND NOT EXISTS (select mer2.id
                                             from mhr_extra_registrations mer2
                                            where mer2.mhr_number = mr.mhr_number
                                              AND mer2.account_id = mr.account_id
                                              AND mer2.removed_ind = 'Y'))
)) as q WHERE q.mhr_number IS NOT NULL """
)
QUERY_ACCOUNT_DEFAULT2 = (
    QUERY_ACCOUNT_REG_BASE
    + """
 WHERE mhr_number IN (SELECT DISTINCT mer.mhr_number
                           FROM mhr_extra_registrations mer
                          WHERE account_id = :query_value1
                            AND (removed_ind IS NULL OR removed_ind != 'Y')
                          UNION (
                         SELECT DISTINCT mr.mhr_number
                           FROM mhr_registrations mr
                          WHERE account_id = :query_value1
                            AND mr.registration_type IN ('MHREG', 'MHREG_CONVERSION')
                            AND NOT EXISTS (SELECT mer.id
                                              FROM mhr_extra_registrations mer
                                             WHERE mer.account_id = mr.account_id
                                               AND mer.mhr_number = mr.mhr_number
                                               AND mer.removed_ind = 'Y')))
"""
)
REG_ORDER_BY_DATE = " ORDER BY q.registration_ts DESC"
REG_ORDER_BY_MHR_NUMBER = " ORDER BY q.mhr_number"
REG_ORDER_BY_REG_TYPE = " ORDER BY q.document_type"
REG_ORDER_BY_STATUS = " ORDER BY q.status_type"
REG_ORDER_BY_SUBMITTING_NAME = " ORDER BY q.submitting_name"
REG_ORDER_BY_CLIENT_REF = " ORDER BY q.client_reference_id"
REG_ORDER_BY_USERNAME = " ORDER BY q.registering_name"
REG_ORDER_BY_OWNER_NAME = " ORDER BY q.owner_names"
REG_ORDER_BY_EXPIRY_DAYS = " ORDER BY q.mhr_number"
REG_ORDER_BY_DOCUMENT_ID = " ORDER BY q.document_id"
REG_ORDER_BY_MANUFACTURER_NAME = " ORDER BY q.manufacturer_name"
REG_ORDER_BY_CIVIC_ADDRESS = " ORDER BY q.civic_address"
REG_FILTER_REG_TYPE = " AND q.document_type = '?'"
REG_FILTER_REG_TYPE_COLLAPSE = """
 AND q.mhr_number IN (SELECT DISTINCT r2.mhr_number
                        FROM mhr_registrations r2, mhr_documents d2
                       WHERE r2.id = d2.registration_id
                         AND r2.mhr_number = q.mhr_number
                         AND d2.document_type = '?')
"""
REG_FILTER_MHR = " AND q.mhr_number = '?'"
REG_FILTER_STATUS = " AND q.status_type = '?'"
REG_FILTER_STATUS_COLLAPSE = """
 AND q.mhr_number IN (SELECT DISTINCT r2.mhr_number
                        FROM mhr_registrations r2
                       WHERE q.mhr_number = r2.mhr_number
                         AND r2.registration_type IN ('MHREG', 'MHREG_CONVERSION')
                         AND r2.status_type = '?')
"""
REG_FILTER_SUBMITTING_NAME = " AND position('?' in q.submitting_name) > 0"
REG_FILTER_SUBMITTING_NAME_COLLAPSE = """
 AND q.mhr_number IN (SELECT DISTINCT arv2.mhr_number
                        FROM mhr_account_reg_vw arv2
                       WHERE q.mhr_number = arv2.mhr_number
                         AND position('?' in arv2.submitting_name) > 0)
"""
REG_FILTER_CLIENT_REF = " AND position('?' in UPPER(q.client_reference_id)) > 0"
REG_FILTER_CLIENT_REF_COLLAPSE = """
 AND q.mhr_number IN (SELECT DISTINCT r2.mhr_number
                        FROM mhr_registrations r2
                       WHERE q.mhr_number = r2.mhr_number
                         AND position('?' in UPPER(r2.client_reference_id)) > 0)
"""
REG_FILTER_USERNAME = " AND position('?' in q.registering_name) > 0"
REG_FILTER_USERNAME_COLLAPSE = """
 AND q.mhr_number IN (SELECT r2.mhr_number
                        FROM mhr_registrations r2, users u
                       WHERE r2.mhr_number = q.mhr_number
                         AND r2.user_id IS NOT NULL
                         AND r2.user_id != ''
                         AND r2.user_id = u.username
                         AND u.firstname IS NOT NULL AND u.lastname IS NOT NULL
                         AND position('?' in TRIM(UPPER(u.firstname || ' ' || u.lastname))) > 0)
"""
REG_FILTER_DATE = " AND registration_ts BETWEEN :query_start AND :query_end"
REG_FILTER_DATE_COLLAPSE = """
 AND q.mhr_number IN (SELECT DISTINCT r2.mhr_number
                        FROM mhr_registrations r2
                       WHERE q.mhr_number = r2.mhr_number
                         AND r2.registration_ts BETWEEN :query_start AND :query_end)
"""
REG_FILTER_DOCUMENT_ID = " AND position('?' in q.document_id) > 0"
REG_FILTER_DOCUMENT_ID_COLLAPSE = """
 AND q.mhr_number IN (SELECT DISTINCT r2.mhr_number
                        FROM mhr_registrations r2, mhr_documents d2
                       WHERE q.mhr_number = r2.mhr_number
                         AND r2.id = d2.registration_id
                         AND position('?' in d2.document_id) > 0)
"""
REG_FILTER_MANUFACTURER_NAME = " AND position('?' in q.manufacturer_name) > 0"
REG_FILTER_MANUFACTURER_NAME_COLLAPSE = """
 AND q.mhr_number IN (SELECT DISTINCT arv2.mhr_number
                        FROM mhr_account_reg_vw arv2
                       WHERE q.mhr_number = arv2.mhr_number
                         AND position('?' in arv2.manufacturer_name) > 0)
"""
ACCOUNT_SORT_DESCENDING = " DESC"
ACCOUNT_SORT_ASCENDING = " ASC"
DEFAULT_SORT_ORDER = " ORDER BY q.registration_ts DESC"
