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
# pylint: disable=too-few-public-methods,too-many-lines

"""This module holds methods to support registration model updates - mostly account registration summary."""
from sqlalchemy.sql import text

from mhr_api.exceptions import DatabaseException
from mhr_api.models import utils as model_utils
from mhr_api.models.db import db
from mhr_api.models.queries import (
    ACCOUNT_SORT_ASCENDING,
    ACCOUNT_SORT_DESCENDING,
    CHANGE_QUERY_PKEYS,
    CHANGE_QUERY_PKEYS_NO_DRAFT,
    DEFAULT_SORT_ORDER,
    DOC_ID_COUNT_QUERY,
    MHR_CHECK_QUERY,
    QUERY_ACCOUNT_ADD_REG_DOC,
    QUERY_ACCOUNT_ADD_REG_MHR,
    QUERY_ACCOUNT_DEFAULT,
    QUERY_ACCOUNT_STAFF_NO_FILTER,
    QUERY_BATCH_MANUFACTURER_MHREG,
    QUERY_BATCH_MANUFACTURER_MHREG_DEFAULT,
    QUERY_PERMIT_COUNT,
    QUERY_PKEYS,
    QUERY_PKEYS_NO_DRAFT,
    QUERY_PPR_LIEN_COUNT,
    QUERY_PPR_REGISTRATION_TYPE,
    QUERY_REG_ID_PKEY,
    REG_FILTER_CLIENT_REF,
    REG_FILTER_CLIENT_REF_COLLAPSE,
    REG_FILTER_DATE,
    REG_FILTER_DATE_COLLAPSE,
    REG_FILTER_DOCUMENT_ID,
    REG_FILTER_DOCUMENT_ID_COLLAPSE,
    REG_FILTER_MANUFACTURER_NAME,
    REG_FILTER_MANUFACTURER_NAME_COLLAPSE,
    REG_FILTER_MHR,
    REG_FILTER_REG_TYPE,
    REG_FILTER_REG_TYPE_COLLAPSE,
    REG_FILTER_STATUS,
    REG_FILTER_STATUS_COLLAPSE,
    REG_FILTER_SUBMITTING_NAME,
    REG_FILTER_SUBMITTING_NAME_COLLAPSE,
    REG_FILTER_USERNAME,
    REG_FILTER_USERNAME_COLLAPSE,
    REG_ORDER_BY_CIVIC_ADDRESS,
    REG_ORDER_BY_CLIENT_REF,
    REG_ORDER_BY_DATE,
    REG_ORDER_BY_DOCUMENT_ID,
    REG_ORDER_BY_EXPIRY_DAYS,
    REG_ORDER_BY_MANUFACTURER_NAME,
    REG_ORDER_BY_MHR_NUMBER,
    REG_ORDER_BY_OWNER_NAME,
    REG_ORDER_BY_REG_TYPE,
    REG_ORDER_BY_STATUS,
    REG_ORDER_BY_SUBMITTING_NAME,
    REG_ORDER_BY_USERNAME,
    UPDATE_BATCH_REG_REPORT,
    UPDATE_QUERY_SUMMARY_SNAPSHOT_BY_MHR_NUMBER,
    UPDATE_QUERY_SUMMARY_SNAPSHOT_BY_REG_ID,
)
from mhr_api.models.type_tables import (
    MhrDocumentType,
    MhrDocumentTypes,
    MhrNoteStatusTypes,
    MhrRegistrationStatusTypes,
    MhrRegistrationType,
    MhrRegistrationTypes,
    MhrStatusTypes,
)
from mhr_api.services.authz import (
    DEALERSHIP_GROUP,
    GOV_ACCOUNT_ROLE,
    MANUFACTURER_GROUP,
    QUALIFIED_USER_GROUP,
    STAFF_ROLE,
    is_staff_account,
)
from mhr_api.utils.logging import logger

# Account registration request parameters to support sorting and filtering.
CLIENT_REF_PARAM = "clientReferenceId"
PAGE_NUM_PARAM = "pageNumber"
SORT_DIRECTION_PARAM = "sortDirection"
SORT_CRITERIA_PARAM = "sortCriteriaName"
MHR_NUMBER_PARAM = "mhrNumber"
DOC_REG_NUMBER_PARAM = "documentRegistrationNumber"
REG_TYPE_PARAM = "registrationType"
REG_TS_PARAM = "createDateTime"
START_TS_PARAM = "startDateTime"
END_TS_PARAM = "endDateTime"
STATUS_PARAM = "statusType"
SUBMITTING_NAME_PARAM = "submittingName"
OWNER_NAME_PARAM = "ownerName"
USER_NAME_PARAM = "username"
MANUFACTURER_NAME_PARAM = "manufacturerName"
CIVIC_ADDRESS_PARAM = "civicAddress"
EXPIRY_DAYS_PARAM = "expiryDays"
DOCUMENT_ID_PARAM = "documentId"
SORT_ASCENDING = "ascending"
SORT_DESCENDING = "descending"
DOC_ID_QUALIFIED_CLAUSE = ",  get_mhr_doc_qualified_id() AS doc_id"
DOC_ID_MANUFACTURER_CLAUSE = ",  get_mhr_doc_manufacturer_id() AS doc_id"
QUERY_NEXT_QUALIFIED_DOC_ID = "select get_mhr_doc_qualified_id()"
QUERY_NEXT_MANUFACTURER_DOC_ID = "select get_mhr_doc_manufacturer_id()"
DOC_ID_GOV_AGENT_CLAUSE = ",  get_mhr_doc_gov_agent_id() AS doc_id"
DOC_ID_STAFF_CLAUSE = ",  get_mhr_doc_staff_id() AS doc_id"
BATCH_DOC_NAME_MANUFACTURER_MHREG = "batch-manufacturer-mhreg-report-{time}.pdf"
REGISTRATION_PATH = "/mhr/api/v1/registrations/"
DOCUMENT_PATH = "/mhr/api/v1/documents/"
CAUTION_CANCELLED_DAYS: int = -9999
CAUTION_INDEFINITE_DAYS: int = 9999
DEFAULT_REG_TYPE_FILTER = "'MHREG'"
QUERY_ACCOUNT_FILTER_BY = {
    MHR_NUMBER_PARAM: REG_FILTER_MHR,
    STATUS_PARAM: REG_FILTER_STATUS,
    REG_TYPE_PARAM: REG_FILTER_REG_TYPE,
    SUBMITTING_NAME_PARAM: REG_FILTER_SUBMITTING_NAME,
    CLIENT_REF_PARAM: REG_FILTER_CLIENT_REF,
    USER_NAME_PARAM: REG_FILTER_USERNAME,
    START_TS_PARAM: REG_FILTER_DATE,
    DOCUMENT_ID_PARAM: REG_FILTER_DOCUMENT_ID,
    MANUFACTURER_NAME_PARAM: REG_FILTER_MANUFACTURER_NAME,
}
QUERY_ACCOUNT_FILTER_BY_COLLAPSE = {
    MHR_NUMBER_PARAM: REG_FILTER_MHR,
    STATUS_PARAM: REG_FILTER_STATUS_COLLAPSE,
    REG_TYPE_PARAM: REG_FILTER_REG_TYPE_COLLAPSE,
    SUBMITTING_NAME_PARAM: REG_FILTER_SUBMITTING_NAME_COLLAPSE,
    CLIENT_REF_PARAM: REG_FILTER_CLIENT_REF_COLLAPSE,
    USER_NAME_PARAM: REG_FILTER_USERNAME_COLLAPSE,
    START_TS_PARAM: REG_FILTER_DATE_COLLAPSE,
    DOCUMENT_ID_PARAM: REG_FILTER_DOCUMENT_ID_COLLAPSE,
    MANUFACTURER_NAME_PARAM: REG_FILTER_MANUFACTURER_NAME_COLLAPSE,
}
QUERY_ACCOUNT_ORDER_BY = {
    REG_TS_PARAM: REG_ORDER_BY_DATE,
    MHR_NUMBER_PARAM: REG_ORDER_BY_MHR_NUMBER,
    STATUS_PARAM: REG_ORDER_BY_STATUS,
    REG_TYPE_PARAM: REG_ORDER_BY_REG_TYPE,
    SUBMITTING_NAME_PARAM: REG_ORDER_BY_SUBMITTING_NAME,
    CLIENT_REF_PARAM: REG_ORDER_BY_CLIENT_REF,
    OWNER_NAME_PARAM: REG_ORDER_BY_OWNER_NAME,
    EXPIRY_DAYS_PARAM: REG_ORDER_BY_EXPIRY_DAYS,
    USER_NAME_PARAM: REG_ORDER_BY_USERNAME,
    DOCUMENT_ID_PARAM: REG_ORDER_BY_DOCUMENT_ID,
    MANUFACTURER_NAME_PARAM: REG_ORDER_BY_MANUFACTURER_NAME,
    CIVIC_ADDRESS_PARAM: REG_ORDER_BY_CIVIC_ADDRESS,
}


class AccountRegistrationParams:
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
    filter_document_id: str = None
    filter_manufacturer: str = None

    def __init__(self, account_id, collapse: bool = False, sbc_staff: bool = False):
        """Set common base initialization."""
        self.account_id = account_id
        self.collapse = collapse
        self.sbc_staff = sbc_staff

    def has_sort(self) -> bool:
        """Check if sort criteria provided."""
        if self.sort_criteria:
            if self.sort_criteria in (MHR_NUMBER_PARAM, REG_TYPE_PARAM, REG_TS_PARAM, CLIENT_REF_PARAM):
                return True
            if self.sort_criteria in (
                SUBMITTING_NAME_PARAM,
                OWNER_NAME_PARAM,
                USER_NAME_PARAM,
                STATUS_PARAM,
                EXPIRY_DAYS_PARAM,
                DOCUMENT_ID_PARAM,
                MANUFACTURER_NAME_PARAM,
                CIVIC_ADDRESS_PARAM,
            ):
                return True
        return False

    def has_filter(self) -> bool:
        """Check if filter criteria provided."""
        return (
            self.filter_client_reference_id
            or self.filter_mhr_number
            or self.filter_registration_type
            or self.filter_reg_start_date
            or self.filter_status_type
            or self.filter_submitting_name
            or self.filter_username
            or self.filter_document_id
            or self.filter_manufacturer
        )

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
        if self.filter_document_id:
            return DOCUMENT_ID_PARAM, self.filter_document_id
        if self.filter_manufacturer:
            return MANUFACTURER_NAME_PARAM, self.filter_manufacturer
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
        result = db.session.execute(query, {"query_value": mhr_number})
        row = result.first()
        lien_count = int(row[0])
        return lien_count
    except Exception as db_exception:  # noqa: B902; return nicer error
        logger.error("get_ppr_lien_count exception: " + str(db_exception))
        raise DatabaseException(db_exception) from db_exception


def get_ppr_registration_type(mhr_number: str) -> str:
    """Execute a query to get the existing PPR registration type on the MH (must not exist check)."""
    try:
        reg_type: str = None
        query = text(QUERY_PPR_REGISTRATION_TYPE)
        result = db.session.execute(query, {"query_value": mhr_number})
        if result:
            row = result.first()
            if row:
                reg_type = str(row[0]) if row[0] else None
        return reg_type
    except Exception as db_exception:  # noqa: B902; return nicer error
        logger.error("get_ppr_registration_type exception: " + str(db_exception))
        raise DatabaseException(db_exception) from db_exception


def get_owner_group_count(base_reg) -> int:
    """Derive the next owner group id from the number of existing groups."""
    count: int = len(base_reg.owner_groups)
    for reg in base_reg.change_registrations:
        if reg.owner_groups:
            count += len(reg.owner_groups)
    return count


def get_group_sequence_num(base_reg, add_count: int, group_id: int) -> int:
    """Derive the group sequence number from the group id of an added group with a default of 1."""
    sequence_num: int = add_count
    if not group_id:
        return sequence_num
    for group in base_reg.owner_groups:
        if group.group_id == group_id:
            return group.group_sequence_number
    for reg in base_reg.change_registrations:
        if reg.owner_groups:
            for group in reg.owner_groups:
                if group.group_id == group_id:
                    return group.group_sequence_number
    return sequence_num


def is_transfer_due_to_death(reg_type: str) -> bool:
    """Return if the registration type is a type of Transfer Due to Death."""
    return reg_type and reg_type in (
        MhrRegistrationTypes.TRANS_ADMIN,
        MhrRegistrationTypes.TRANS_AFFIDAVIT,
        MhrRegistrationTypes.TRANS_WILL,
        MhrRegistrationTypes.TRAND,
    )


def is_staff_review_registration(reg_doc_type: str, group: str) -> bool:
    """Return if the registration or document type is QS submitted and to be reviewed by staff."""
    if not group:
        return reg_doc_type and reg_doc_type in (
            MhrRegistrationTypes.TRANS_WILL,
            MhrDocumentTypes.WILL,
            MhrRegistrationTypes.TRANS_ADMIN,
            MhrRegistrationTypes.TRANS_AFFIDAVIT,
            MhrDocumentTypes.LETA,
            MhrDocumentTypes.AFFE,
        )
    return (
        group == QUALIFIED_USER_GROUP
        and reg_doc_type
        and reg_doc_type
        in (
            MhrRegistrationTypes.TRANS_WILL,
            MhrDocumentTypes.WILL,
            MhrRegistrationTypes.TRANS_ADMIN,
            MhrRegistrationTypes.TRANS_AFFIDAVIT,
            MhrDocumentTypes.LETA,
            MhrDocumentTypes.AFFE,
        )
    )


def is_transfer_due_to_death_staff(reg_type: str) -> bool:
    """Return if the registration type is a type of Transfer Due to Death."""
    return reg_type and reg_type in (
        MhrRegistrationTypes.TRANS_ADMIN,
        MhrRegistrationTypes.TRANS_AFFIDAVIT,
        MhrRegistrationTypes.TRANS_WILL,
    )


def get_generated_values(registration, draft, user_group: str = None, staff_doc_id: str = None):
    """Get db generated identifiers that are in more than one table.

    Get registration_id, mhr_number, and optionally draft_number.
    """
    # generate reg id, MHR number. If not existing draft also generate draft number
    query_text = QUERY_PKEYS
    gen_doc_id: bool = False
    if draft:
        query_text = QUERY_PKEYS_NO_DRAFT
    if user_group and user_group in (QUALIFIED_USER_GROUP, DEALERSHIP_GROUP):
        query_text += DOC_ID_QUALIFIED_CLAUSE
        gen_doc_id = True
        logger.info("Updating query to generate qualified user document id.")
    elif user_group and user_group == MANUFACTURER_GROUP:
        query_text += DOC_ID_MANUFACTURER_CLAUSE
        gen_doc_id = True
        logger.info("Updating query to generate manufacturer document id.")
    elif user_group and user_group == GOV_ACCOUNT_ROLE:
        query_text += DOC_ID_GOV_AGENT_CLAUSE
        gen_doc_id = True
        logger.info("Updating query to generate government agent document id.")
    elif user_group and user_group == STAFF_ROLE and not staff_doc_id:
        query_text += DOC_ID_STAFF_CLAUSE
        gen_doc_id = True
        logger.info("Updating query to generate staff document id.")
    query = text(query_text)
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
        registration.doc_id = str(row[6])
    elif gen_doc_id and draft:
        registration.doc_id = str(row[4])
    elif staff_doc_id:
        registration.doc_id = staff_doc_id
    return registration


def get_change_generated_values(registration, draft, user_group: str = None, staff_doc_id: str = None):
    """Get db generated identifiers that are in more than one table.

    Get registration_id, mhr_number, and optionally draft_number.
    """
    # generate reg id, MHR number. If not existing draft also generate draft number
    query_text = CHANGE_QUERY_PKEYS
    gen_doc_id: bool = False
    if draft:
        query_text = CHANGE_QUERY_PKEYS_NO_DRAFT
    if user_group and user_group in (QUALIFIED_USER_GROUP, DEALERSHIP_GROUP):
        query_text += DOC_ID_QUALIFIED_CLAUSE
        gen_doc_id = True
    elif user_group and user_group == MANUFACTURER_GROUP:
        query_text += DOC_ID_MANUFACTURER_CLAUSE
        gen_doc_id = True
    elif user_group and user_group == GOV_ACCOUNT_ROLE:
        query_text += DOC_ID_GOV_AGENT_CLAUSE
        gen_doc_id = True
        logger.info("Updating query to generate government agent document id.")
    elif user_group and user_group == STAFF_ROLE and not staff_doc_id:
        query_text += DOC_ID_STAFF_CLAUSE
        gen_doc_id = True
        logger.info("Updating query to generate staff document id.")
    query = text(query_text)
    result = db.session.execute(query)
    row = result.first()
    registration.id = int(row[0])
    registration.doc_pkey = int(row[1])
    registration.doc_reg_number = str(row[2])
    if not draft:
        registration.draft_number = str(row[3])
        registration.draft_id = int(row[4])
    if gen_doc_id and draft:
        registration.doc_id = str(row[3])
    elif gen_doc_id and not draft:
        registration.doc_id = str(row[5])
    elif staff_doc_id:
        registration.doc_id = staff_doc_id
    return registration


def get_qs_document_id(user_group: str) -> str:
    """Get db generated qualifed supplier document ID based on the user group. Only intended for DRS integration."""
    query: str = QUERY_NEXT_QUALIFIED_DOC_ID
    if user_group is not None and user_group == MANUFACTURER_GROUP:
        query = QUERY_NEXT_MANUFACTURER_DOC_ID
    result = db.session.execute(text(query))
    row = result.first()
    return str(row[0])


def get_registration_id() -> int:
    """Get db generated registration id, initially for creating a manufacturer."""
    result = db.session.execute(text(QUERY_REG_ID_PKEY))
    row = result.first()
    return int(row[0])


def update_deceased(owners_json, owner):
    """Set deceased information for transfer due to death registrations."""
    existing_json = owner.json
    match_json = None
    for owner_json in owners_json:
        if (
            owner_json.get("organizationName")
            and existing_json.get("organizationName")
            and owner_json.get("organizationName") == existing_json.get("organizationName")
        ):
            match_json = owner_json
            break
        if (
            owner_json.get("individualName")
            and existing_json.get("individualName")
            and owner_json.get("individualName") == existing_json.get("individualName")
        ):
            match_json = owner_json
            break
    if match_json:
        if match_json.get("deathCertificateNumber"):
            owner.death_cert_number = str(match_json.get("deathCertificateNumber")).strip()
        elif match_json.get("deathCorpNumber"):
            owner.death_corp_number = str(match_json.get("deathCorpNumber")).strip()
        if match_json.get("deathDateTime"):
            owner.death_ts = model_utils.ts_from_iso_format(match_json.get("deathDateTime"))


def include_caution_note(notes, document_id: str) -> bool:
    """Include expired caution note if subsequent continue or extend caution has not expired."""
    latest_caution = None
    for note in notes:
        if not latest_caution and note.get("documentType", "") in ("CAUC", "CAUE", "CAU "):
            latest_caution = note
        if note.get("documentId") == document_id:
            break
        if latest_caution and note.get("documentType", "") not in ("CAUC", "CAUE", "CAU "):
            return False
    return latest_caution and not model_utils.date_elapsed(latest_caution.get("expiryDate"))


def get_batch_manufacturer_reg_report_data(start_ts: str = None, end_ts: str = None) -> dict:
    """Get recent manufacturer MHREG registration report data for a batch report."""
    results_json = []
    query_s = QUERY_BATCH_MANUFACTURER_MHREG_DEFAULT
    if start_ts and end_ts:
        query_s = QUERY_BATCH_MANUFACTURER_MHREG
        logger.debug(f"Using timestamp range {start_ts} to {end_ts}.")
    else:
        logger.debug("Using a default timestamp range of within the previous day.")
    query = text(query_s)
    result = None
    if start_ts and end_ts:
        start: str = start_ts[:19].replace("T", " ")
        end: str = end_ts[:19].replace("T", " ")
        logger.debug(f"start={start} end={end}")
        result = db.session.execute(query, {"query_val1": start, "query_val2": end})
    else:
        result = db.session.execute(query)
    rows = result.fetchall()
    if rows is not None:
        for row in rows:
            batch_url = str(row[5]) if row[5] else ""
            result_json = {
                "registrationId": int(row[0]),
                "accountId": str(row[1]),
                "reportId": int(row[3]),
                "reportData": row[4],
                "batchStorageUrl": batch_url,
            }
            results_json.append(result_json)
    if results_json:
        logger.debug(f"Found {len(results_json)} manufacturer MHREG registrations.")
    else:
        logger.debug("No manufacturer MHREG registrations found within the timestamp range.")
    return results_json


def update_reg_report_batch_url(json_data: dict, batch_url: str) -> int:
    """Set the mhr registration reports batch storage url for the recent registrations in json_data."""
    update_count: int = 0
    if not json_data:
        return update_count
    query_s = UPDATE_BATCH_REG_REPORT
    report_ids: str = ""
    for report in json_data:
        update_count += 1
        if report_ids != "":
            report_ids += ","
        report_ids += str(report.get("reportId"))
    query_s = query_s.format(batch_url=batch_url, report_ids=report_ids)
    logger.debug(f"Executing update query {query_s}")
    query = text(query_s)
    result = db.session.execute(query)
    db.session.commit()
    if result:
        logger.debug(f"Updated {update_count} manufacturer report registrations batch url to {batch_url}.")
    return update_count


def get_batch_storage_name_manufacturer_mhreg():
    """Get a search document storage name in the format YYYY/MM/DD/batch-manufacturer-mhreg-report-time.pdf."""
    now_ts = model_utils.now_ts()
    name = now_ts.isoformat()[:10]
    time = str(now_ts.hour) + "_" + str(now_ts.minute)
    name = name.replace("-", "/") + "/" + BATCH_DOC_NAME_MANUFACTURER_MHREG.format(time=time)
    return name


def find_cancelled_note(registration, reg_id: int):
    """Try and find the cancelled note matching the cancel registration document id."""
    if not registration.change_registrations:
        return None
    logger.debug(f"find_cancelled_note id={reg_id}")
    for reg in registration.change_registrations:
        if reg.notes and reg.notes[0].change_registration_id == reg_id:
            return reg.notes[0]
    return None


def get_document_description(doc_type: str) -> str:
    """Try to find the document description by document type."""
    if doc_type:
        doc_type_info: MhrDocumentType = MhrDocumentType.find_by_doc_type(doc_type)
        if doc_type_info:
            return doc_type_info.document_type_desc
    return ""


def get_registration_description(reg_type: str) -> str:
    """Try to find the regisration description by registration type."""
    if reg_type:
        type_info = (
            db.session.query(MhrRegistrationType)
            .filter(MhrRegistrationType.registration_type == reg_type)
            .one_or_none()
        )
        if type_info:
            return type_info.registration_type_desc
    return ""


def save_cancel_note(registration, json_data, new_reg_id):  # pylint: disable=too-many-branches; only 1 more.
    """Update the original note status and change registration id."""
    cancel_doc_id: str = json_data.get("cancelDocumentId", "")
    if not cancel_doc_id:
        cancel_doc_id: str = json_data.get("updateDocumentId", "")
    cancel_note = get_cancel_note(registration, cancel_doc_id)
    if cancel_note:  # pylint: disable=too-many-nested-blocks; only 1 more.
        cancel_note.status_type = MhrNoteStatusTypes.CANCELLED
        cancel_note.change_registration_id = new_reg_id
        logger.debug(f"updating note status, change reg id for reg id {cancel_note.registration_id}")
        # Cancelling one active caution registration cancels all active caution registrations
        if cancel_note.document_type in (MhrDocumentTypes.CAU, MhrDocumentTypes.CAUC, MhrDocumentTypes.CAUE):
            for reg in registration.change_registrations:
                if reg.notes:
                    doc = reg.documents[0]
                    if doc.document_id != cancel_doc_id and doc.document_type in (
                        MhrDocumentTypes.CAU,
                        MhrDocumentTypes.CAUC,
                        MhrDocumentTypes.CAUE,
                    ):
                        note = reg.notes[0]
                        if note.status_type == MhrNoteStatusTypes.ACTIVE:
                            note.status_type = MhrNoteStatusTypes.CANCELLED
                            note.change_registration_id = new_reg_id
        elif cancel_note.document_type in (MhrDocumentTypes.EXNR, MhrDocumentTypes.EXRS, MhrDocumentTypes.EXMN):
            for reg in registration.change_registrations:
                if reg.notes:
                    doc = reg.documents[0]
                    if doc.document_id != cancel_doc_id and doc.document_type in (
                        MhrDocumentTypes.EXNR,
                        MhrDocumentTypes.EXRS,
                        MhrDocumentTypes.EXMN,
                    ):
                        note = reg.notes[0]
                        if note.status_type == MhrNoteStatusTypes.ACTIVE:
                            note.status_type = MhrNoteStatusTypes.CANCELLED
                            note.change_registration_id = new_reg_id
        db.session.commit()
    else:
        logger.debug(f"No modernized note found to cancel for reg id= {registration.id}")


def save_active(registration):
    """Set the state of the original MH registration to active."""
    if registration.status_type:
        logger.info(f"Setting MH state to ACTIVE for registration id={registration.id}")
        registration.status_type = MhrRegistrationStatusTypes.ACTIVE
        db.session.commit()
    else:
        logger.info("No modernized registration to set to active status.")


def cancel_note_exre(registration, new_reg_id):
    """EXRE cancel all active exemption notes."""
    for reg in registration.change_registrations:
        if reg.notes and reg.notes[0].document_type in (
            MhrDocumentTypes.EXNR,
            MhrDocumentTypes.EXRS,
            MhrDocumentTypes.EXMN,
        ):
            note = reg.notes[0]
            if note.status_type == MhrNoteStatusTypes.ACTIVE:
                note.status_type = MhrNoteStatusTypes.CANCELLED
                note.change_registration_id = new_reg_id


def save_admin(registration, json_data: dict, new_reg_id: int):
    """Admin registration updates to existing records."""
    doc_type: str = json_data.get("documentType", "")
    logger.debug(f"save_admin doc type={doc_type}")
    if doc_type not in (
        MhrDocumentTypes.EXRE,
        MhrDocumentTypes.STAT,
        MhrDocumentTypes.REGC_CLIENT,
        MhrDocumentTypes.REGC_STAFF,
        MhrDocumentTypes.PUBA,
    ):
        return
    if json_data.get("location"):
        if registration.locations and registration.locations[0].status_type == MhrStatusTypes.ACTIVE:
            registration.locations[0].status_type = MhrStatusTypes.HISTORICAL
            registration.locations[0].change_registration_id = new_reg_id
        elif registration.change_registrations:
            for reg in registration.change_registrations:  # Updating a change registration location.
                for existing in reg.locations:
                    if existing.status_type == MhrStatusTypes.ACTIVE and existing.registration_id != new_reg_id:
                        existing.status_type = MhrStatusTypes.HISTORICAL
                        existing.change_registration_id = new_reg_id
    save_description(registration, json_data, new_reg_id)
    save_admin_status(registration, json_data, new_reg_id, doc_type)
    if json_data.get("addOwnerGroups") and json_data.get("deleteOwnerGroups"):
        registration.remove_groups(json_data, new_reg_id)
    # EXRE cancel exemption notes as well.
    if doc_type == MhrDocumentTypes.EXRE:
        cancel_note_exre(registration, new_reg_id)
    db.session.commit()


def save_description(registration, json_data: dict, new_reg_id: int):
    """Conditonally update the status and change registration id of the previous description."""
    if not json_data.get("description"):
        return
    if registration.descriptions and registration.descriptions[0].status_type == MhrStatusTypes.ACTIVE:
        registration.descriptions[0].status_type = MhrStatusTypes.HISTORICAL
        registration.descriptions[0].change_registration_id = new_reg_id
        for section in registration.sections:
            if section.status_type == MhrStatusTypes.ACTIVE:
                section.status_type = MhrStatusTypes.HISTORICAL
                section.change_registration_id = new_reg_id
    elif registration.change_registrations:
        for reg in registration.change_registrations:
            if (
                reg.descriptions
                and reg.descriptions[0].status_type == MhrStatusTypes.ACTIVE
                and reg.descriptions[0].registration_id != new_reg_id
            ):
                reg.descriptions[0].status_type = MhrStatusTypes.HISTORICAL
                reg.descriptions[0].change_registration_id = new_reg_id
            if reg.sections:
                for section in reg.sections:
                    if section.status_type == MhrStatusTypes.ACTIVE:
                        section.status_type = MhrStatusTypes.HISTORICAL
                        section.change_registration_id = new_reg_id


def save_admin_status(registration, json_data: dict, new_reg_id: int, doc_type: str):
    """Admin registration updates to MH home status."""
    if (
        doc_type == MhrDocumentTypes.STAT
        and json_data.get("location")
        and json_data["location"]["address"].get("region", "BC") != model_utils.PROVINCE_BC
    ):
        registration.status_type = MhrRegistrationStatusTypes.EXEMPT
        logger.info("New location out of province, updating status to EXEMPT.")
    elif doc_type == MhrDocumentTypes.EXRE:
        registration.status_type = MhrRegistrationStatusTypes.ACTIVE
        logger.debug(f"Doc type {doc_type} updating MH status to ACTIVE.")
    elif json_data.get("status", "") and doc_type in (
        MhrDocumentTypes.REGC_CLIENT,
        MhrDocumentTypes.REGC_STAFF,
        MhrDocumentTypes.PUBA,
    ):
        status: str = json_data.get("status")
        if (
            registration.status_type == MhrRegistrationStatusTypes.ACTIVE
            and status != MhrRegistrationStatusTypes.ACTIVE
        ):
            registration.status_type = status
            logger.debug(f"Doc type {doc_type} updating ACTIVE status to {status}.")
        elif (
            registration.status_type != MhrRegistrationStatusTypes.ACTIVE
            and status == MhrRegistrationStatusTypes.ACTIVE
        ):
            registration.status_type = status
            logger.debug(f"Doc type {doc_type} updating status to {status}.")
            if registration.change_registrations:
                for reg in registration.change_registrations:  # Cancel existing exempttion note.
                    if (
                        reg.notes
                        and reg.notes[0]
                        and reg.notes[0].status_type == MhrNoteStatusTypes.ACTIVE
                        and reg.notes[0].document_type in (MhrDocumentTypes.EXRS, MhrDocumentTypes.EXNR)
                    ):
                        note = reg.notes[0]
                        note.status_type = MhrNoteStatusTypes.CANCELLED
                        note.change_registration_id = new_reg_id
                        logger.debug(f"Cancelling exemption note reg id={note.registration_id}.")


def get_cancel_note(registration, cancel_document_id: str):
    """Try and find the note matching the cancel document id."""
    cancel_note = None
    logger.info(f"Looking up note to cancel with doc id={cancel_document_id}")
    if not registration.change_registrations:
        logger.info("No change registrations so no notes to cancel.")
        return cancel_note
    for reg in registration.change_registrations:
        if reg.notes:
            doc = reg.documents[0]
            if doc.document_id == cancel_document_id:
                return reg.notes[0]
    return cancel_note


def set_declared_value_json(registration, json_data):
    """Set the most recent declared value and registration timestamp if they exist."""
    if not registration or not registration.change_registrations or not json_data:
        return json_data
    for reg in registration.change_registrations:
        if reg.documents and reg.documents[0].declared_value and reg.documents[0].declared_value > 0:
            json_data["declaredValue"] = reg.documents[0].declared_value
            json_data["declaredDateTime"] = model_utils.format_ts(reg.registration_ts)
    return json_data


def get_doc_id_count(doc_id: str) -> int:
    """Execute a query to count existing document id (must not exist check)."""
    try:
        query = text(DOC_ID_COUNT_QUERY)
        result = db.session.execute(query, {"query_value": doc_id})
        row = result.first()
        exist_count = int(row[0])
        logger.debug(f"Existing doc id count={exist_count}.")
        return exist_count
    except Exception as db_exception:  # noqa: B902; return nicer error
        logger.error("get_doc_id_count exception: " + str(db_exception))
        raise DatabaseException(db_exception) from db_exception


def validate_mhr_number(mhr_num: str) -> bool:
    """Execute a query to verify a MHR number does not exist and is less than the current max value."""
    try:
        query = text(MHR_CHECK_QUERY)
        result = db.session.execute(query, {"query_value": mhr_num})
        row = result.first()
        max_mhr: str = str(row[0])
        exist_count = int(row[1])
        logger.debug(f"MHR {mhr_num} max existing value {max_mhr} exist count={exist_count}.")
        if int(mhr_num) >= int(max_mhr):
            return False
        return exist_count == 0
    except Exception as db_exception:  # noqa: B902; return nicer error
        logger.error("get_doc_id_count exception: " + str(db_exception))
        raise DatabaseException(db_exception) from db_exception


def get_permit_count(mhr_number: str, name: str) -> int:
    """Execute a query to count existing transport permit registrations on a home."""
    try:
        query = text(QUERY_PERMIT_COUNT)
        query_name = name[0:40]
        result = db.session.execute(query, {"query_value1": mhr_number, "query_value2": query_name})
        row = result.first()
        exist_count = int(row[0])
        logger.debug(f"Existing transport permit count={exist_count}.")
        return exist_count
    except Exception as db_exception:  # noqa: B902; return nicer error
        logger.error("get_permit_count exception: " + str(db_exception))
        raise DatabaseException(db_exception) from db_exception


def find_summary_by_mhr_number(account_id: str, mhr_number: str, staff: bool):
    """Return the MHR registration summary parent-child information matching the registration number."""
    registrations = []
    try:
        query = text(QUERY_ACCOUNT_ADD_REG_MHR)
        result = db.session.execute(query, {"query_value1": account_id, "query_value2": mhr_number})
        rows = result.fetchall()
        if rows is not None:
            for row in rows:
                registrations.append(__build_summary(row, account_id, staff, True))
            registrations = __collapse_results(registrations)
        return registrations[0] if registrations else {}
    except Exception as db_exception:  # noqa: B902; return nicer error
        logger.error("find_summary_by_mhr_number exception: " + str(db_exception))
        raise DatabaseException(db_exception) from db_exception


def find_summary_by_doc_reg_number(account_id: str, doc_reg_number: str, staff: bool):
    """Return the MHR registration summary parent-child information matching the document registration number."""
    registrations = []
    try:
        query = text(QUERY_ACCOUNT_ADD_REG_DOC)
        result = db.session.execute(query, {"query_value1": account_id, "query_value2": doc_reg_number})
        rows = result.fetchall()
        if rows is not None:
            for row in rows:
                registrations.append(__build_summary(row, account_id, staff, True))
            registrations = __collapse_results(registrations)
        return registrations[0] if registrations else {}
    except Exception as db_exception:  # noqa: B902; return nicer error
        logger.error("find_summary_by_doc_reg_number exception: " + str(db_exception))
        raise DatabaseException(db_exception) from db_exception


def update_summary_snapshot_by_mhr_number(mhr_number: str):
    """Return the MHR registration summary snapshot matching the mhr number."""
    try:
        query = text(UPDATE_QUERY_SUMMARY_SNAPSHOT_BY_MHR_NUMBER)
        result = db.session.execute(query, {"query_value1": mhr_number})
        if result:
            logger.debug(f"Updated mhr registration summary snapshot for mhr_number {mhr_number}.")
        db.session.commit()
    except Exception as db_exception:  # noqa: B902; return nicer error
        logger.error("update_summary_snapshot_by_mhr_number exception: " + str(db_exception))
        raise DatabaseException(db_exception) from db_exception


def update_summary_snapshot_by_reg_id(registration_id: int):
    """Return the MHR registration summary snapshot matching the registration id."""
    try:
        query = text(UPDATE_QUERY_SUMMARY_SNAPSHOT_BY_REG_ID)
        result = db.session.execute(query, {"query_value1": registration_id})
        if result:
            logger.debug(f"Updated mhr registration summary snapshot for reg_id {registration_id}.")
        db.session.commit()
    except Exception as db_exception:  # noqa: B902; return nicer error
        logger.error("update_summary_snapshot_by_registration_id exception: " + str(db_exception))
        raise DatabaseException(db_exception) from db_exception


def find_all_by_account_id(params: AccountRegistrationParams):
    """Return a summary list of recent MHR registrations belonging to an account."""
    registrations = []
    try:
        query = text(build_account_query(params))
        # logger.info(query)
        if params.has_filter() and params.filter_reg_start_date and params.filter_reg_end_date:
            start_ts = model_utils.search_ts(params.filter_reg_start_date, True)
            end_ts = model_utils.search_ts(params.filter_reg_end_date, False)
            # logger.info(f'start_ts={start_ts} end_ts={end_ts}')
            result = db.session.execute(
                query, {"query_value1": params.account_id, "query_start": start_ts, "query_end": end_ts}
            )
        else:
            result = db.session.execute(query, {"query_value1": params.account_id})
        rows = result.fetchall()
        if rows is not None:
            for row in rows:
                registrations.append(__build_summary(row, params.account_id, params.sbc_staff, False))
            if params.collapse:
                registrations = __collapse_results(registrations)
        return registrations
    except Exception as db_exception:  # noqa: B902; return nicer error
        logger.error("find_all_by_account_id exception: " + str(db_exception))
        raise DatabaseException(db_exception) from db_exception


def __build_summary(row, account_id: str, staff: bool, add_in_user_list: bool = True):
    """Build registration summary from query result."""
    mhr_number = str(row[0])
    # logger.info(f'summary mhr#={mhr_number}')
    timestamp = row[2]
    owners = str(row[6]) if row[6] else ""
    owner_names = ""
    if owners:
        owner_names = owners.replace("\\n", ",\n")
        # remove comma if exists at end of str
        if owner_names[-3] == ",\n":
            owner_names = owner_names[:-3]
    reg_account_id: str = str(row[15])
    doc_type: str = str(row[18])
    username: str = str(row[7]) if row[7] else ""
    if not username and row[23]:
        username = str(row[23])
    summary = {
        "mhrNumber": mhr_number,
        "registrationDescription": str(row[16]),
        "username": username,
        "statusType": str(row[1]),
        "createDateTime": model_utils.format_ts(timestamp),
        "submittingParty": str(row[3]) if row[3] else "",
        "clientReferenceId": str(row[4]) if row[4] else "",
        "ownerNames": owner_names,
        "documentId": str(row[8]),
        "documentRegistrationNumber": str(row[9]),
        "registrationType": str(row[5]),
        "locationType": str(row[22]),
        "consumedDraftNumber": str(row[26]) if row[26] else "",
        "manufacturerName": str(row[27]) if row[27] else "",
        "civicAddress": str(row[28]) if row[28] else "",
    }
    summary = __get_report_path(account_id, staff, summary, row, timestamp)
    if add_in_user_list and summary["registrationType"] in (
        MhrRegistrationTypes.MHREG,
        MhrRegistrationTypes.MHREG_CONVERSION,
    ):
        remove_count: int = int(row[20])
        extra_count: int = int(row[21])
        summary["inUserList"] = bool((account_id == reg_account_id and remove_count == 0) or extra_count > 0)
    if summary["registrationType"] in (MhrRegistrationTypes.MHREG, MhrRegistrationTypes.MHREG_CONVERSION):
        summary["lienRegistrationType"] = str(row[17]) if row[17] else ""
    elif doc_type in (MhrDocumentTypes.NCAN, MhrDocumentTypes.NRED, MhrDocumentTypes.EXRE):
        summary = __get_cancel_info(summary, row)
    elif doc_type in (MhrDocumentTypes.CAU, MhrDocumentTypes.CAUC, MhrDocumentTypes.CAUE):
        summary = __get_caution_info(summary, row, doc_type)
    elif (
        doc_type in (MhrDocumentTypes.REG_103, MhrDocumentTypes.REG_103E, MhrDocumentTypes.AMEND_PERMIT)
        and row[12]
        and (not row[11] or row[11] not in (MhrNoteStatusTypes.CANCELLED, MhrNoteStatusTypes.COMPLETED))
    ):
        expiry = row[12]
        summary["expireDays"] = model_utils.expiry_ts_days(expiry)
    summary = __set_frozen_status(summary, row, staff)
    return summary


def __get_report_path(account_id: str, staff: bool, summary: dict, row, timestamp) -> dict:
    """Derive the report download path if applicable."""
    reg_account_id: str = str(row[15]) if row[15] else ""
    doc_storage_url: str = str(row[19]) if row[19] else ""
    rep_count: int = int(row[24])
    summary["legacy"] = rep_count <= 0
    if is_staff_account(account_id):
        if reg_account_id != "0":
            summary["accountId"] = str(row[25]) if row[25] else reg_account_id
        else:
            summary["accountId"] = "N/A"
    # To be consistent with PPR, allow registries staff to generate reports for legacy registrations
    # if rep_count > 0 and (staff or account_id == reg_account_id) and \
    if (staff or (rep_count > 0 and account_id == reg_account_id)) and (
        doc_storage_url or model_utils.report_retry_elapsed(timestamp)
    ):
        if summary["registrationType"] in (MhrRegistrationTypes.MHREG, MhrRegistrationTypes.MHREG_CONVERSION):
            summary["path"] = REGISTRATION_PATH + summary.get("mhrNumber")
        else:
            summary["path"] = DOCUMENT_PATH + summary.get("documentId")
    else:
        summary["path"] = ""
    return summary


def __get_caution_info(summary: dict, row, doc_type: str) -> dict:
    """Add expireDays to summary for CAU, CAUC, CAUE document types."""
    status: str = str(row[11]) if row[11] else None
    if status and status == MhrNoteStatusTypes.CANCELLED:
        summary["expireDays"] = CAUTION_CANCELLED_DAYS  # Cancelled.
    else:
        expiry = row[12] if row[12] else None
        if not expiry and doc_type == MhrDocumentTypes.CAUC:
            summary["expireDays"] = CAUTION_INDEFINITE_DAYS  # Indefinite expiry.
        elif expiry:
            summary["expireDays"] = model_utils.expiry_date_days(expiry.date())
    return summary


def __get_cancel_info(summary: dict, row) -> dict:
    """For registrations with the NCAN document type get the cancelled note type and description."""
    doc_type: str = str(row[13]) if row[13] else None
    if doc_type:
        summary["cancelledDocumentType"] = doc_type.strip()
        summary["cancelledDocumentDescription"] = get_document_description(doc_type)
    return summary


def __set_frozen_status(summary: dict, row, staff: bool) -> dict:
    """Conditionally set FROZEN status based on active note document types or last registration doc type."""
    if summary.get("statusType", "") != MhrRegistrationStatusTypes.ACTIVE:
        return summary
    last_doc_type: str = str(row[10])
    if last_doc_type == MhrDocumentTypes.AFFE:
        summary["statusType"] = model_utils.STATUS_FROZEN
        summary["frozenDocumentType"] = last_doc_type
    elif not staff:
        doc_type: str = str(row[14]) if row[14] else None
        if doc_type:
            summary["statusType"] = model_utils.STATUS_FROZEN
            summary["frozenDocumentType"] = doc_type
    return summary


def __get_previous_owner_names(changes: dict, default: str, doc_id: str) -> str:
    """Try and find owner names from a previous registration, using the default if none found."""
    found: bool = False
    names: str = None
    for change_reg in changes:
        if change_reg.get("documentId") == doc_id:
            found = True
        elif not names and found and change_reg.get("ownerNames"):
            names = change_reg.get("ownerNames")
            break
    if names:
        return names
    return default


def __collapse_results(results):
    """Organized reults as parent-children mh registration-change registrations."""
    registrations = []
    for result in results:
        if result["registrationType"] in (MhrRegistrationTypes.MHREG, MhrRegistrationTypes.MHREG_CONVERSION):
            registrations.append(result)
    for reg in registrations:
        has_caution: bool = False
        # owner_names = reg.get('ownerNames')
        changes = []
        for result in results:
            if result["mhrNumber"] == reg["mhrNumber"] and result["registrationType"] not in (
                MhrRegistrationTypes.MHREG,
                MhrRegistrationTypes.MHREG_CONVERSION,
            ):
                if (
                    result.get("expireDays")
                    and result.get("expireDays") >= 0
                    and str(result["registrationDescription"]).find("CAUTION") >= 0
                ):
                    has_caution = True
                changes.append(result)
        if changes:
            reg["changes"] = changes
        reg["hasCaution"] = has_caution
    return registrations


def build_account_query(params: AccountRegistrationParams) -> str:
    """Build the account registration summary query."""
    query_text: str = QUERY_ACCOUNT_DEFAULT
    if not params.has_filter() and params.account_id == STAFF_ROLE:
        query_text = QUERY_ACCOUNT_STAFF_NO_FILTER
    if not params.has_filter() and not params.has_sort():
        query_text += DEFAULT_SORT_ORDER
        return query_text
    order_clause: str = ""
    if params.has_filter():
        query_text = build_account_query_filter(query_text, params)
    if params.has_sort():
        order_clause = QUERY_ACCOUNT_ORDER_BY.get(params.sort_criteria)
        if params.sort_criteria == REG_TS_PARAM:
            if params.sort_direction and params.sort_direction == SORT_ASCENDING:
                order_clause = order_clause.replace(ACCOUNT_SORT_DESCENDING, ACCOUNT_SORT_ASCENDING)
        elif params.sort_direction and params.sort_direction == SORT_ASCENDING:
            order_clause += ACCOUNT_SORT_ASCENDING
        else:
            order_clause += ACCOUNT_SORT_DESCENDING
        query_text += order_clause
    else:  # Default sort order if filter but no sorting specified.
        query_text += DEFAULT_SORT_ORDER
    # logger.info(query_text)
    return query_text


def get_multiple_filters(params: AccountRegistrationParams) -> dict:
    """Build the list of all applied filters as a key/value dictionary."""
    filters = []
    if params.filter_mhr_number:
        filters.append(("mhrNumber", params.filter_mhr_number))
    if params.filter_registration_type:
        filters.append(("registrationType", params.filter_registration_type))
    if params.filter_reg_start_date:
        filters.append(("startDateTime", params.filter_reg_start_date))
    if params.filter_status_type:
        filters.append(("statusType", params.filter_status_type))
    if params.filter_client_reference_id:
        filters.append(("clientReferenceId", params.filter_client_reference_id))
    if params.filter_submitting_name:
        filters.append(("submittingName", params.filter_submitting_name))
    if params.filter_username:
        filters.append(("username", params.filter_username))
    if params.filter_document_id:
        filters.append(("documentId", params.filter_document_id))
    if params.filter_manufacturer:
        filters.append(("manufacturerName", params.filter_manufacturer))
    if filters:
        return filters
    return None


def build_account_query_filter(query_text: str, params: AccountRegistrationParams) -> str:
    """Build the account registration summary query filter clause."""
    filter_clause: str = ""
    # Get all selected filters and loop through, applying them
    filters = get_multiple_filters(params)
    for query_filter in filters:
        filter_type = query_filter[0]
        filter_value = query_filter[1]
        if filter_type and filter_value:
            # Filter may exclude parent MH registrations, so use a different query to include base registrations.
            filter_clause = QUERY_ACCOUNT_FILTER_BY_COLLAPSE.get(filter_type)
            if not params.collapse:
                filter_clause = QUERY_ACCOUNT_FILTER_BY.get(filter_type)
            if filter_clause:
                if filter_type == REG_TYPE_PARAM:
                    filter_clause = __get_reg_type_filter(filter_value, params.collapse)
                elif filter_type == STATUS_PARAM and filter_value == MhrRegistrationStatusTypes.DRAFT:
                    filter_clause = filter_clause.replace("?", MhrRegistrationStatusTypes.ACTIVE)
                elif filter_type != START_TS_PARAM:
                    filter_clause = filter_clause.replace("?", filter_value)
                query_text += filter_clause
    return query_text


def __get_reg_type_filter(filter_value: str, collapse: bool) -> dict:
    """Get the document type from the filter value."""
    doc_types = MhrDocumentType.find_all()
    doc_type: str = "missing"
    for doc_rec in doc_types:
        if filter_value in (doc_rec.document_type_desc, doc_rec.document_type):
            doc_type = doc_rec.document_type
            break
    if doc_type == "missing":
        return ""
    if collapse:
        return REG_FILTER_REG_TYPE_COLLAPSE.replace("?", doc_type)
    return REG_FILTER_REG_TYPE.replace("?", doc_type)
