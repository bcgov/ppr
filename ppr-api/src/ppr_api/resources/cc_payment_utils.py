# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Helper methods for saving draft and registration info when payment is by credit card."""
from http import HTTPStatus

from sqlalchemy.sql import text

from ppr_api.models import (
    CourtOrder,
    Draft,
    EventTracking,
    FinancingStatement,
    GeneralCollateral,
    Party,
    Registration,
    SecuritiesActNotice,
    TrustIndenture,
    VehicleCollateral,
    db,
    registration_utils,
)
from ppr_api.models import utils as model_utils
from ppr_api.models.draft import DRAFT_PAY_PENDING_PREFIX
from ppr_api.models.registration import ACCOUNT_DRAFT_USED_SUFFIX, MiscellaneousTypes
from ppr_api.resources.financing_utils import save_rl_transition
from ppr_api.services.authz import STAFF_ROLE
from ppr_api.utils.logging import logger

DRAFT_QUERY_PKEYS = """
select get_draft_document_number() AS doc_num,
       nextval('draft_id_seq') AS draft_id
"""
REG_STATUS_LOCKED = "L"
REG_STATUS_UNLOCKED = "Y"
# 07 used by payment tracking job
TRACKING_MESSAGES = {
    "00": "00: default credit card payment update error for invoice id={invoice_id}.",
    "01": "01: credit card payment set up complete for invoice id={invoice_id}.",
    "01S": "01S: staff credit card payment set up complete for invoice id={invoice_id}.",
    "02": "02: credit card payment update set up error for invoice id={invoice_id}.",
    "03": "03: credit card payment update error no draft found for invoice id={invoice_id}.",
    "04": "04: credit card payment update error no registration for invoice id={invoice_id}.",
    "05": "05: credit card payment update pay status CANCELLED for invoice id={invoice_id}.",
    "06": "06: credit card payment update draft pending status CANCELLED for invoice id={invoice_id}.",
    "09": "09: credit card payment completed successfully for invoice id={invoice_id}.",
    "10": "10: create registration successful for cc payment invoice id={invoice_id}.",
    "11": "11: search credit card payment set up complete for invoice id={invoice_id}.",
    "11S": "11S: staff search credit card payment set up complete for invoice id={invoice_id}.",
    "13": "13: credit card payment update error no search found for invoice id={invoice_id}.",
    "14": "14: credit card payment update error search no pending payment for invoice id={invoice_id}.",
}


def track_event(code: str, invoice_id: str, status_code: int, message: str = None):
    """Capture a cc payment event in the event tracking table."""
    msg: str = TRACKING_MESSAGES[code].format(invoice_id=invoice_id)
    if message:
        msg += " " + message
    if status_code not in (HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.ACCEPTED):
        logger.error(msg)
    else:
        logger.info(msg)
    EventTracking.create(int(invoice_id), EventTracking.EventTrackingTypes.PPR_PAYMENT, status_code, msg)
    return msg


def create_new_draft(json_data: dict, registration_class: str, base_reg_num: str = None) -> Draft:
    """Get db generated identifiers for a new MHR draft record.

    Get draft_number and draft ID.
    """
    draft: Draft = Draft()
    draft.draft = json_data
    draft.account_id = json_data.get("accountId")
    draft.create_ts = model_utils.now_ts()
    draft.registration_type_cl = registration_class
    if draft.registration_type_cl in (model_utils.REG_CLASS_AMEND, model_utils.REG_CLASS_AMEND_COURT):
        json_data = model_utils.cleanup_amendment(json_data)
        draft.registration_type = model_utils.amendment_change_type(json_data)
        if draft.registration_type == model_utils.REG_TYPE_AMEND_COURT:
            draft.registration_type_cl = model_utils.REG_CLASS_AMEND_COURT
    elif draft.registration_type_cl == model_utils.REG_CLASS_RENEWAL:
        draft.registration_type = model_utils.REG_TYPE_RENEWAL
    elif draft.registration_type_cl == model_utils.REG_CLASS_DISCHARGE:
        draft.registration_type = model_utils.REG_TYPE_DISCHARGE
    if base_reg_num:
        draft.registration_number = base_reg_num
    query = text(DRAFT_QUERY_PKEYS)
    result = db.session.execute(query)
    row = result.first()
    draft.document_number = DRAFT_PAY_PENDING_PREFIX + str(row[0])
    draft.id = int(row[1])
    logger.info(f"New draft created id={draft.id} doc number={draft.document_number}")
    return draft


def track_search_payment(json_data: dict, account_id: str, search_id: str):
    """
    Create an event tracking record for search cc payment request.

    Args:
        json_data (dict): Search results response with payment informatiob.
        account_id (str): Account ID that submitted the search request.
        search_id (str): Search ID of the search request.
    """
    try:
        invoice_id: int = int(json_data["payment"].get("invoiceId"))
        if account_id != STAFF_ROLE:
            track_event("11", invoice_id, HTTPStatus.OK, f"Search id=*{search_id}*.")
        else:
            pay_account_id: str = json_data["payment"].get("accountId", "")
            track_event("11S", invoice_id, HTTPStatus.OK, f"Account {pay_account_id} search id=*{search_id}*.")
    except Exception as err:  # noqa: B902; return nicer default error
        logger.info(f"track_search_payment failed for search id {search_id}: {err}")


def save_change_cc_draft(base_reg: Registration, json_data: dict, new_reg: Registration) -> Registration:
    """
    Change registration with credit card payment create/update draft. Returns an unsaved registration
    with response JSON.

    Args:
        base_reg (Registration): current registration being updated.
        json_data (dict): Request payload updated with some extra registration information (payment).
        registration (Registration): Minimal registration with registration type and class.
    """
    # Create or update draft.
    draft: Draft = None
    if json_data.get("documentId"):
        draft = Draft.find_by_document_number(json_data["documentId"].strip(), False)
    json_data["paymentPending"] = True
    json_data["baseRegistrationNumber"] = base_reg.registration_num
    json_data["registrationType"] = new_reg.registration_type
    if draft:
        draft.draft = json_data
        draft.document_number = DRAFT_PAY_PENDING_PREFIX + draft.document_number
    else:
        draft = create_new_draft(json_data, new_reg.registration_type_cl, base_reg.registration_num)
    draft.update_ts = model_utils.now_ts()
    draft.user_id = json_data["payment"].get("invoiceId")
    draft.registration_number = base_reg.registration_num
    draft.save()
    new_reg.draft = draft
    new_reg.reg_json = json_data
    # Lock the base registration here:
    base_reg.ver_bypassed = REG_STATUS_LOCKED
    logger.info(f"Locking base reg# {base_reg.registration_num}.")
    base_reg.save()
    track_event("01", int(json_data["payment"].get("invoiceId")), HTTPStatus.OK, "Change registration draft saved.")
    return new_reg


def save_new_cc_draft(json_data: dict, new_reg: Registration) -> Registration:
    """
    New registration with credit card payment create/update draft. Returns an unsaved registration
    with response JSON.

    Args:
        json_data (dict): Request payload updated with some extra registration information (payment).
        registration (Registration): Minimal registration with registration type and class.
    """
    # Create or update draft.
    draft: Draft = None
    if json_data.get("documentId"):
        draft = Draft.find_by_document_number(json_data["documentId"].strip(), False)
    json_data["paymentPending"] = True
    if draft:
        draft.draft = json_data
        draft.document_number = DRAFT_PAY_PENDING_PREFIX + draft.document_number
    else:
        json_data["registrationType"] = new_reg.registration_type
        draft = create_new_draft(json_data, new_reg.registration_type_cl, None)
    draft.registration_type = new_reg.registration_type
    draft.update_ts = model_utils.now_ts()
    draft.user_id = json_data["payment"].get("invoiceId")
    draft.save()
    new_reg.draft = draft
    new_reg.reg_json = json_data
    statement: FinancingStatement = FinancingStatement()
    statement.registration = [new_reg]
    track_event("01", int(json_data["payment"].get("invoiceId")), HTTPStatus.OK, "New registration draft saved.")
    return statement


def create_new_statement(draft: Draft) -> FinancingStatement:
    """Create new financing statement base registration from the draft."""
    json_data: dict = draft.draft
    statement: FinancingStatement = FinancingStatement(state_type=model_utils.STATE_ACTIVE)
    statement.parties = Party.create_from_financing_json(json_data, None)
    new_reg: Registration = create_financing_registration(draft)
    statement.registration = [new_reg]
    statement.life = statement.registration[0].life
    if new_reg.registration_type == model_utils.REG_TYPE_REPAIRER_LIEN:
        statement.expire_date = model_utils.expiry_dt_repairer_lien()
    elif statement.life and statement.life != model_utils.LIFE_INFINITE:
        statement.expire_date = model_utils.expiry_dt_from_years(statement.life)

    if new_reg.registration_type == model_utils.REG_TYPE_OTHER and "otherTypeDescription" in json_data:
        statement.crown_charge_other = json_data["otherTypeDescription"]

    statement.trust_indenture = TrustIndenture.create_from_json(json_data, new_reg.id)
    if "vehicleCollateral" in json_data:
        statement.vehicle_collateral = VehicleCollateral.create_from_financing_json(json_data, new_reg.id)
    if "generalCollateral" in json_data:
        statement.general_collateral = GeneralCollateral.create_from_financing_json(json_data, new_reg.id)

    for party in statement.parties:
        party.registration_id = new_reg.id
    statement.save()
    logger.info(f"New fs reg id={new_reg.id} {new_reg.registration_type} #={new_reg.registration_num}")
    return statement


def create_change_registration(draft: Draft, statement: FinancingStatement) -> Registration:
    """Create new change registration from the draft."""
    registration: Registration = create_basic_registration(draft, statement)
    json_data: dict = draft.draft
    registration_id = registration.id
    financing_reg_type = statement.registration[0].registration_type
    if registration.registration_type_cl == model_utils.REG_CLASS_RENEWAL:
        registration_utils.set_renewal_life(registration, json_data, financing_reg_type)
    # Repairer's lien renewal or amendment can have court order information.
    if (
        registration.registration_type in (model_utils.REG_TYPE_AMEND_COURT, model_utils.REG_TYPE_RENEWAL)
        and "courtOrderInformation" in json_data
    ):
        registration.court_order = CourtOrder.create_from_json(json_data["courtOrderInformation"], registration_id)
    if registration.registration_type_cl in (
        model_utils.REG_CLASS_AMEND,
        model_utils.REG_CLASS_AMEND_COURT,
        model_utils.REG_CLASS_CHANGE,
    ):
        # Possibly add vehicle collateral
        registration.vehicle_collateral = VehicleCollateral.create_from_statement_json(
            json_data, registration_id, registration.financing_id
        )
        # Possibly add general collateral
        registration.general_collateral = GeneralCollateral.create_from_statement_json(
            json_data, registration_id, registration.financing_id
        )
        # Possibly add/remove a trust indenture
        if ("addTrustIndenture" in json_data and json_data["addTrustIndenture"]) or (
            "removeTrustIndenture" in json_data and json_data["removeTrustIndenture"]
        ):
            registration.trust_indenture = TrustIndenture.create_from_amendment_json(
                registration.financing_id, registration.id
            )
            if "removeTrustIndenture" in json_data and json_data["removeTrustIndenture"]:
                registration.trust_indenture.trust_indenture = TrustIndenture.TRUST_INDENTURE_NO
        if json_data.get("addSecuritiesActNotices") and financing_reg_type == MiscellaneousTypes.SECURITIES_NOTICE:
            registration.securities_act_notices = SecuritiesActNotice.create_from_statement_json(
                json_data, registration_id
            )
        # Close out deleted parties and collateral, trust indenture, and securities act notices.
        Registration.delete_from_json(json_data, registration, statement)
    registration.save()
    save_rl_transition(registration.registration_type_cl, statement, registration.id)
    logger.info(f"New reg id={registration.id} {registration.registration_type} #={registration.registration_num}")
    return registration


def create_basic_registration(draft: Draft, statement: FinancingStatement) -> Registration:
    """Create new registration from the draft with common properties."""
    json_data = draft.draft
    registration: Registration = Registration.get_generated_values(draft)
    registration.financing_id = statement.id
    registration.financing_statement = statement
    registration.account_id = draft.account_id
    registration.user_id = json_data.get("username")
    registration.registration_ts = model_utils.now_ts()
    registration.pay_invoice_id = int(json_data["payment"].get("invoiceId"))
    registration.pay_path = json_data["payment"].get("receipt")
    registration.registration_type = draft.registration_type
    registration.registration_type_cl = draft.registration_type_cl
    registration.base_registration_num = draft.registration_number
    registration_utils.set_registration_basic_info(registration, json_data, draft.registration_type_cl)
    draft.draft = json_data
    draft.account_id = draft.account_id + ACCOUNT_DRAFT_USED_SUFFIX
    registration.draft = draft
    # All registrations have at least one party (registering).
    registration.parties = Party.create_from_statement_json(
        json_data, registration.registration_type_cl, registration.financing_id
    )
    return registration


def create_financing_registration(draft: Draft) -> Registration:
    """Create new base registration from the draft with common properties."""
    json_data = draft.draft
    registration: Registration = Registration.get_generated_values(draft)
    registration.account_id = draft.account_id
    registration.user_id = json_data.get("username")
    registration.registration_ts = model_utils.now_ts()
    registration.pay_invoice_id = int(json_data["payment"].get("invoiceId"))
    registration.pay_path = json_data["payment"].get("receipt")
    registration.registration_type = draft.registration_type
    registration.registration_type_cl = draft.registration_type_cl
    registration.ver_bypassed = "Y"
    if registration.registration_type == model_utils.REG_TYPE_REPAIRER_LIEN:
        if "lienAmount" in json_data:
            registration.lien_value = json_data["lienAmount"].strip()
        if "surrenderDate" in json_data:
            registration.surrender_date = model_utils.ts_from_date_iso_format(json_data["surrenderDate"])
        registration.life = model_utils.REPAIRER_LIEN_YEARS
    elif "lifeInfinite" in json_data and json_data["lifeInfinite"]:
        registration.life = model_utils.LIFE_INFINITE
    elif registration.registration_type_cl in (model_utils.REG_CLASS_CROWN, model_utils.REG_CLASS_MISC):
        registration.life = model_utils.LIFE_INFINITE
    elif registration.registration_type in (
        model_utils.REG_TYPE_MARRIAGE_SEPARATION,
        model_utils.REG_TYPE_TAX_MH,
        model_utils.REG_TYPE_LAND_TAX_MH,
    ):
        registration.life = model_utils.LIFE_INFINITE
    elif "lifeYears" in json_data:
        registration.life = json_data["lifeYears"]
    if "clientReferenceId" in json_data:
        registration.client_reference_id = json_data["clientReferenceId"]
    draft.account_id = draft.account_id + ACCOUNT_DRAFT_USED_SUFFIX
    registration.draft = draft
    if draft.registration_type == MiscellaneousTypes.SECURITIES_NOTICE and json_data.get("securitiesActNotices"):
        registration = registration_utils.create_securities_act_notices(registration, json_data)
    return registration
