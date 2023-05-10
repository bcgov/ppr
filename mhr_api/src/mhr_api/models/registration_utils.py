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
import json

from flask import current_app
from sqlalchemy.sql import text

from mhr_api.exceptions import BusinessException, DatabaseException
from mhr_api.models import utils as model_utils, MhrDraft
from mhr_api.models.db import db
from mhr_api.models.type_tables import MhrRegistrationTypes
from mhr_api.services.authz import MANUFACTURER_GROUP, QUALIFIED_USER_GROUP, GENERAL_USER_GROUP, BCOL_HELP


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


def get_generated_values(registration, draft):
    """Get db generated identifiers that are in more than one table.

    Get registration_id, mhr_number, and optionally draft_number.
    """
    # generate reg id, MHR number. If not existing draft also generate draft number
    query = QUERY_PKEYS
    if draft:
        query = QUERY_PKEYS_NO_DRAFT
    result = db.session.execute(query)
    row = result.first()
    registration.id = int(row[0])
    registration.doc_pkey = int(row[1])
    registration.mhr_number = str(row[2])
    registration.doc_reg_number = str(row[3])
    if not draft:
        registration.draft_number = str(row[4])
        registration.draft_id = int(row[5])
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


def find_draft(json_data, registration_type: str = None):
    """Try to find an existing draft if a draftNumber is in json_data.).

    Return None if not found or no documentId.
    """
    draft = None
    if json_data.get('draftNumber'):
        try:
            draft_number = json_data['draftNumber'].strip()
            if draft_number != '':
                draft: MhrDraft = MhrDraft.find_by_draft_number(draft_number, False)
                if draft:
                    draft.draft = json.dumps(json_data)
                    if registration_type:
                        draft.registration_type = registration_type
        except BusinessException:
            draft = None
    return draft


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
