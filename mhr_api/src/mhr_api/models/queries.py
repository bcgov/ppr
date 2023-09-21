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
SELECT mhr_number, status_type, registration_ts, submitting_name, client_reference_id, registration_type, owner_names,
       registering_name, document_id, document_registration_number, last_doc_type, note_status, note_expiry,
       cancel_doc_type, frozen_doc_type, account_id, document_type_desc, ppr_lien_type, document_type, doc_storage_url,
       (SELECT COUNT(mer.id)
          FROM mhr_extra_registrations mer
         WHERE mer.mhr_number = arv.mhr_number
           AND mer.account_id = arv.account_id
           AND (mer.removed_ind IS NULL OR mer.removed_ind != 'Y')) AS reg_count,
       (SELECT COUNT(mer.id)
          FROM mhr_extra_registrations mer
         WHERE mer.mhr_number = arv.mhr_number
           AND mer.account_id = :query_value1
           AND mer.account_id != arv.account_id
           AND (mer.removed_ind IS NULL OR mer.removed_ind != 'Y')) AS extra_reg_count
  FROM mhr_account_reg_vw arv
"""
QUERY_ACCOUNT_ADD_REG_MHR = QUERY_ACCOUNT_REG_BASE + """
 WHERE mhr_number = :query_value2
ORDER BY registration_ts
"""
QUERY_ACCOUNT_ADD_REG_DOC = QUERY_ACCOUNT_REG_BASE + """
 WHERE mhr_number = (SELECT r.mhr_number
                       FROM mhr_registrations r, mhr_documents d
                      WHERE r.id = d.registration_id
                        AND d.document_registration_number = :query_value2)
ORDER BY registration_ts
"""
QUERY_ACCOUNT_DEFAULT = QUERY_ACCOUNT_REG_BASE + """
 WHERE mhr_number IN (SELECT DISTINCT mer.mhr_number
                           FROM mhr_extra_registrations mer
                          WHERE account_id = :query_value1
                            AND (removed_ind IS NULL OR removed_ind != 'Y')
                          UNION (
                         SELECT DISTINCT mr.mhr_number
                           FROM mhr_registrations mr
                          WHERE account_id = :query_value1
                            AND mr.registration_type = 'MHREG'))
"""

REG_ORDER_BY_DATE = ' ORDER BY registration_ts DESC'
REG_ORDER_BY_MHR_NUMBER = ' ORDER BY mhr_number'
REG_ORDER_BY_REG_TYPE = ' ORDER BY document_type'
REG_ORDER_BY_STATUS = ' ORDER BY status_type'
REG_ORDER_BY_SUBMITTING_NAME = ' ORDER BY submitting_name'
REG_ORDER_BY_CLIENT_REF = ' ORDER BY client_reference_id'
REG_ORDER_BY_USERNAME = ' ORDER BY registering_name'
REG_ORDER_BY_OWNER_NAME = ' ORDER BY owner_names'
REG_ORDER_BY_EXPIRY_DAYS = ' ORDER BY mhr_number'
REG_FILTER_REG_TYPE = " AND document_type = '?'"
REG_FILTER_REG_TYPE_COLLAPSE = """
 AND mhr_number IN (SELECT DISTINCT r2.mhr_number
                      FROM mhr_registrations r2, mhr_documents d2
                     WHERE r2.id = d2.registration_id
                       AND d2.document_type = '?')
"""
REG_FILTER_STATUS = " AND status_type = '?'"
REG_FILTER_SUBMITTING_NAME = " AND submitting_name LIKE '%?%'"
REG_FILTER_SUBMITTING_NAME_COLLAPSE = """
 AND mhr_number IN (SELECT DISTINCT arv2.mhr_number
                      FROM mhr_account_reg_vw arv2
                     WHERE arv2.submitting_name LIKE '%?%')
"""
REG_FILTER_CLIENT_REF = " AND UPPER(client_reference_id) LIKE '%?%'"
REG_FILTER_CLIENT_REF_COLLAPSE = """
 AND mhr_number IN (SELECT DISTINCT r2.mhr_number
                      FROM mhr_registrations r2
                     WHERE arv.registration_id = r2.id
                       AND UPPER(r2.client_reference_id) LIKE '%?%')
"""
REG_FILTER_USERNAME = " AND registering_name LIKE '%?%'"
REG_FILTER_USERNAME_COLLAPSE = """
 AND mhr_number IN (SELECT DISTINCT arv2.mhr_number
                      FROM mhr_account_reg_vw arv2
                     WHERE arv2.registering_name LIKE '%?%')
"""
REG_FILTER_DATE = ' AND registration_ts BETWEEN :query_start AND :query_end'
REG_FILTER_DATE_COLLAPSE = """
 AND mhr_number IN (SELECT DISTINCT r2.mhr_number
                      FROM mhr_registrations r2
                     WHERE arv.registration_id = r2.id
                       AND r2.registration_ts BETWEEN :query_start AND :query_end)
"""
ACCOUNT_SORT_DESCENDING = ' DESC'
ACCOUNT_SORT_ASCENDING = ' ASC'
DEFAULT_SORT_ORDER = ' ORDER BY registration_ts DESC'
