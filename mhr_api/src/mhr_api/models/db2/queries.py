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
"""This module holds DB2 query strings."""


UPDATE_LTSA_PID = """
UPDATE location
   SET bcaajuri = :status_value
 WHERE pidnumb IN (?)
"""
QUERY_LTSA_PID = """
SELECT DISTINCT l.pidnumb
  FROM location l, manuhome m
 WHERE m.mhstatus in ('R', 'E')
   AND m.manhomid = l.manhomid
   AND l.status = 'A'
   AND TRIM(l.pidnumb) != ''
   AND LENGTH(TRIM(l.pidnumb)) = 9
   AND TRIM(bcaajuri) = ''
   AND mhregnum not like '150%'
FETCH FIRST 500 ROWS ONLY
"""
QUERY_ACCOUNT_MHR_LEGACY = """
SELECT DISTINCT mer.mhr_number, 'N' AS account_reg,
                (SELECT mlc.registration_type
                   FROM mhr_lien_check_vw mlc
                  WHERE mlc.mhr_number = mer.mhr_number) AS lien_registration_type
 FROM mhr_extra_registrations mer
WHERE account_id = :query_value
  AND (removed_ind IS NULL OR removed_ind != 'Y')
UNION (
SELECT DISTINCT mr.mhr_number, 'Y' AS account_reg,
                (SELECT mlc.registration_type
                   FROM mhr_lien_check_vw mlc
                  WHERE mlc.mhr_number = mr.mhr_number) AS lien_registration_type
  FROM mhr_registrations mr
WHERE account_id = :query_value
  AND mr.registration_type = 'MHREG'
  AND NOT EXISTS (SELECT mer.mhr_number
                    FROM mhr_extra_registrations mer
                   WHERE mer.account_id = mr.account_id
                     AND mer.mhr_number = mr.mhr_number
                     AND (mer.removed_ind IS NOT NULL AND mer.removed_ind = 'Y'))
)
"""
QUERY_ACCOUNT_REGISTRATIONS_SUMMARY = """
SELECT mr.id, mr.registration_ts, mr.account_id, mr.registration_type, mr.mhr_number,
       (SELECT d.document_id FROM mhr_documents d WHERE d.registration_id = mr.id FETCH FIRST 1 ROWS ONLY)
       AS document_id,
       mrr.create_ts as doc_ts, mrr.doc_storage_url, mrt.registration_type_desc,
       (SELECT CASE WHEN mr.user_id IS NULL THEN ''
          ELSE (SELECT u.firstname || ' ' || u.lastname FROM users u WHERE u.username = mr.user_id
                FETCH FIRST 1 ROWS ONLY)
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
            AND mr.registration_type IN ('MHREG')
            AND NOT EXISTS (SELECT mer.mhr_number
                              FROM mhr_extra_registrations mer
                             WHERE mer.mhr_number = mr.mhr_number
                               AND mer.account_id = mr.account_id
                               AND (mer.removed_ind IS NOT NULL AND mer.removed_ind = 'Y'))) AS reg_count,
       (SELECT COUNT(mer.id)
           FROM mhr_extra_registrations mer
          WHERE mer.account_id = :query_value
            AND mer.mhr_number = :query_value2
            AND (mer.removed_ind IS NULL OR mer.removed_ind != 'Y')) as extra_reg_count,
       (SELECT  mr.account_id
           FROM mhr_registrations mr
          WHERE mr.account_id = :query_value
            AND mr.mhr_number = :query_value2
            AND mr.registration_type IN ('MHREG')),
      (SELECT mlc.registration_type
         FROM mhr_lien_check_vw mlc
        WHERE mlc.mhr_number = :query_value2)
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
           AND og2.status IN ('3')) as owner_names,
       TRIM(d.affirmby),
       d.documtid as document_id,
       d.docuregi as doc_reg_number,
       (SELECT d2.docutype
          FROM document d2
         WHERE d2.mhregnum = d.mhregnum
           AND d2.regidate = (SELECT MAX(d3.regidate)
                                FROM document d3
                               WHERE d3.mhregnum = d.mhregnum)) AS last_doc_type,
       (SELECT n.status
          FROM mhomnote n
         WHERE mh.manhomid = n.manhomid AND n.regdocid = d.documtid) AS note_status,
       (SELECT n.expiryda
          FROM mhomnote n
         WHERE mh.manhomid = n.manhomid AND n.regdocid = d.documtid) AS note_expiry,
        CASE
        WHEN d.docutype = 'NCAN' THEN
          (SELECT n.docutype
             FROM mhomnote n
            WHERE n.manhomid = mh.manhomid AND n.candocid = d.documtid AND n.docutype NOT IN ('CAUC', 'CAUE')
          FETCH FIRST 1 ROWS ONLY)
        ELSE NULL
        END AS cancel_doc_type
  FROM manuhome mh, document d
 WHERE mh.mhregnum = :query_mhr_number
   AND mh.mhregnum = d.mhregnum
"""
QUERY_ACCOUNT_ADD_REGISTRATION_DOC = """
SELECT mh.mhregnum, mh.mhstatus, d.regidate, TRIM(d.name), TRIM(d.olbcfoli), TRIM(d.docutype),
       (SELECT XMLSERIALIZE(XMLAGG ( XMLELEMENT ( NAME "owner", o2.ownrtype || TRIM(o2.ownrname))) AS CLOB)
          FROM owner o2, owngroup og2
         WHERE o2.manhomid = mh.manhomid
           AND og2.manhomid = mh.manhomid
           AND og2.owngrpid = o2.owngrpid
           AND og2.status IN ('3')) as owner_names,
       TRIM(d.affirmby),
       d.documtid as document_id,
       d.docuregi as doc_reg_number,
       (SELECT d4.docutype
          FROM document d4
         WHERE d4.mhregnum = d.mhregnum
           AND d4.regidate = (SELECT MAX(d3.regidate)
                                FROM document d3
                               WHERE d3.mhregnum = d.mhregnum)) AS last_doc_type,
       (SELECT n.status
          FROM mhomnote n
         WHERE mh.manhomid = n.manhomid AND n.regdocid = d.documtid) AS note_status,
       (SELECT n.expiryda
          FROM mhomnote n
         WHERE mh.manhomid = n.manhomid AND n.regdocid = d.documtid) AS note_expiry,
        CASE
        WHEN d.docutype = 'NCAN' THEN
          (SELECT n.docutype
             FROM mhomnote n
            WHERE n.manhomid = mh.manhomid AND n.candocid = d.documtid AND n.docutype NOT IN ('CAUC', 'CAUE')
          FETCH FIRST 1 ROWS ONLY)
        ELSE NULL
        END AS cancel_doc_type
  FROM manuhome mh, document d, document d2
 WHERE d2.docuregi = :query_value
   AND d2.mhregnum = mh.mhregnum
   AND mh.mhregnum = d.mhregnum
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
       d.documtid as document_id,
       d.docuregi as doc_reg_number,
       (SELECT d2.docutype
          FROM document d2
         WHERE d2.mhregnum = d.mhregnum
           AND d2.regidate = (SELECT MAX(d3.regidate)
                                FROM document d3
                               WHERE d3.mhregnum = d.mhregnum)) AS last_doc_type,
       (SELECT n.status
          FROM mhomnote n
         WHERE mh.manhomid = n.manhomid AND n.regdocid = d.documtid) AS note_status,
       (SELECT n.expiryda
          FROM mhomnote n
         WHERE mh.manhomid = n.manhomid AND n.regdocid = d.documtid) AS note_expiry,
        CASE
        WHEN d.docutype = 'NCAN' THEN
          (SELECT n.docutype
             FROM mhomnote n
            WHERE n.manhomid = mh.manhomid AND n.candocid = d.documtid AND n.docutype NOT IN ('CAUC', 'CAUE')
          FETCH FIRST 1 ROWS ONLY)
        ELSE NULL
        END AS cancel_doc_type
  FROM manuhome mh, document d
 WHERE mh.mhregnum IN (?)
   AND mh.mhregnum = d.mhregnum
 ORDER BY d.regidate DESC
"""
QUERY_ACCOUNT_REGISTRATIONS_SORT = """
SELECT mh.mhregnum, mh.mhstatus, d.regidate, TRIM(d.name), TRIM(d.olbcfoli), TRIM(d.docutype),
       (SELECT XMLSERIALIZE(XMLAGG ( XMLELEMENT ( NAME "owner", o2.ownrtype || TRIM(o2.ownrname))) AS CLOB)
          FROM owner o2, owngroup og2
         WHERE o2.manhomid = mh.manhomid
           AND og2.manhomid = mh.manhomid
           AND og2.owngrpid = o2.owngrpid
           AND og2.regdocid = d.documtid) as owner_names,
       TRIM(d.affirmby),
       d.documtid as document_id,
       d.docuregi as doc_reg_number,
       (SELECT d2.docutype
          FROM document d2
         WHERE d2.mhregnum = d.mhregnum
           AND d2.regidate = (SELECT MAX(d3.regidate)
                                FROM document d3
                               WHERE d3.mhregnum = d.mhregnum)) AS last_doc_type,
       (SELECT n.status
          FROM mhomnote n
         WHERE mh.manhomid = n.manhomid AND n.regdocid = d.documtid) AS note_status,
       (SELECT n.expiryda
          FROM mhomnote n
         WHERE mh.manhomid = n.manhomid AND n.regdocid = d.documtid) AS note_expiry,
        CASE
        WHEN d.docutype = 'NCAN' THEN
          (SELECT n.docutype
             FROM mhomnote n
            WHERE n.manhomid = mh.manhomid AND n.candocid = d.documtid AND n.docutype NOT IN ('CAUC', 'CAUE')
          FETCH FIRST 1 ROWS ONLY)
        ELSE NULL
        END AS cancel_doc_type,
       (SELECT TRIM(o2.ownrname)
          FROM owner o2, owngroup og2
         WHERE o2.manhomid = mh.manhomid
           AND og2.manhomid = mh.manhomid
           AND og2.owngrpid = o2.owngrpid
           AND og2.regdocid = d.documtid
           FETCH FIRST 1 ROWS ONLY) as owner_name_sort
  FROM manuhome mh, document d
 WHERE mh.mhregnum IN (?)
   AND mh.mhregnum = d.mhregnum
"""
PERMIT_COUNT_QUERY = """
SELECT COUNT(documtid)
  FROM document
 WHERE mhregnum = :query_value1
   AND docutype = '103 '
   AND trim(name) = :query_value2
"""
REG_ORDER_BY_DATE = ' ORDER BY d.regidate DESC'
REG_ORDER_BY_MHR_NUMBER = ' ORDER BY mh.mhregnum'
REG_ORDER_BY_REG_TYPE = ' ORDER BY TRIM(d.docutype)'
REG_ORDER_BY_STATUS = ' ORDER BY mh.mhstatus'
REG_ORDER_BY_SUBMITTING_NAME = ' ORDER BY TRIM(d.name)'
REG_ORDER_BY_CLIENT_REF = ' ORDER BY TRIM(d.olbcfoli)'
REG_ORDER_BY_USERNAME = ' ORDER BY TRIM(d.affirmby)'
REG_ORDER_BY_OWNER_NAME = ' ORDER BY owner_name_sort'
REG_ORDER_BY_EXPIRY_DAYS = ' ORDER BY mh.mhregnum'
REG_FILTER_REG_TYPE = " AND d.docutype = '?'"
REG_FILTER_REG_TYPE_COLLAPSE = """
 AND (d.docutype = '?' OR (d.documtid = mh.regdocid AND EXISTS (SELECT d2.documtid
                                                                  FROM document d2
                                                                 WHERE d2.mhregnum = mh.mhregnum
                                                                   AND d2.docutype = '?')))
"""
REG_FILTER_STATUS = " AND mh.mhstatus = '?'"
REG_FILTER_SUBMITTING_NAME = " AND TRIM(d.name) LIKE '%?%'"
REG_FILTER_SUBMITTING_NAME_COLLAPSE = """
 AND (TRIM(d.name) LIKE '%?%' OR
      (d.documtid = mh.regdocid AND EXISTS (SELECT d2.documtid
                                              FROM document d2
                                             WHERE d2.mhregnum = mh.mhregnum
                                               AND TRIM(d2.name) LIKE '%?%')))
"""
REG_FILTER_CLIENT_REF = " AND UPPER(TRIM(d.olbcfoli)) LIKE '%?%'"
REG_FILTER_CLIENT_REF_COLLAPSE = """
 AND (UPPER(TRIM(d.olbcfoli)) LIKE '%?%' OR
      (d.documtid = mh.regdocid AND EXISTS (SELECT d2.documtid
                                              FROM document d2
                                             WHERE d2.mhregnum = mh.mhregnum
                                               AND TRIM(d2.olbcfoli) LIKE '%?%')))
"""
REG_FILTER_USERNAME = " AND TRIM(d.affirmby) LIKE '%?%'"
REG_FILTER_USERNAME_COLLAPSE = """
 AND (TRIM(d.affirmby) LIKE '%?%' OR
      (d.documtid = mh.regdocid AND EXISTS (SELECT d2.documtid
                                              FROM document d2
                                             WHERE d2.mhregnum = mh.mhregnum
                                               AND TRIM(d2.affirmby) LIKE '%?%')))
"""
REG_FILTER_DATE = ' AND d.regidate BETWEEN :query_start AND :query_end'
REG_FILTER_DATE_COLLAPSE = """
 AND (d.regidate BETWEEN :query_start AND :query_end OR
      (d.documtid = mh.regdocid AND EXISTS (SELECT d2.documtid
                                              FROM document d2
                                             WHERE d2.mhregnum = mh.mhregnum
                                               AND d2.regidate BETWEEN :query_start AND :query_end)))
"""
SORT_DESCENDING = ' DESC'
SORT_ASCENDING = ' ASC'
DEFAULT_SORT_ORDER = ' ORDER BY d.regidate DESC'

NEXT_MHR_NUM_SELECT_FOR_UPDATE = """
SELECT contnum
  FROM contnumb
 WHERE contkey = 'SERMREG'
 FOR UPDATE
"""
NEXT_MHR_NUM_UPDATE = """
UPDATE contnumb
   SET contnum = :query_val
 WHERE contkey = 'SERMREG'
"""
