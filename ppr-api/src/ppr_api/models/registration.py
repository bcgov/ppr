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
# pylint: disable=too-many-statements, too-many-branches

import json
from http import HTTPStatus

from sqlalchemy.sql import text

from ppr_api.exceptions import BusinessException, DatabaseException, ResourceErrorCodes
from ppr_api.models import registration_utils
from ppr_api.models import utils as model_utils
from ppr_api.models.registration_utils import AccountRegistrationParams
from ppr_api.models.type_tables import RegistrationTypes
from ppr_api.services.authz import is_staff_account
from ppr_api.utils.base import BaseEnum
from ppr_api.utils.logging import logger

from .court_order import CourtOrder
from .db import db
from .draft import Draft
from .general_collateral import GeneralCollateral
from .party import Party
from .securities_act_notice import SecuritiesActNotice
from .trust_indenture import TrustIndenture
from .type_tables import RegistrationType
from .user_extra_registration import UserExtraRegistration
from .vehicle_collateral import VehicleCollateral

# noqa: I003


FINANCING_PATH = "/ppr/api/v1/financing-statements/"
ACCOUNT_DRAFT_USED_SUFFIX = "_USED"


class CrownChargeTypes(BaseEnum):
    """Render an Enum of the financing statement crown charge registration type class."""

    CORP_TAX = RegistrationTypes.CC.value
    CARBON_TAX = RegistrationTypes.CT.value
    CONSUMPTION_TAX = RegistrationTypes.DP.value
    EXCISE_TAX = RegistrationTypes.ET.value
    FOREST_TAX = RegistrationTypes.FO.value
    MOTOR_FUEL_TAX = RegistrationTypes.FT.value
    HOTEL_TAX = RegistrationTypes.HR.value
    INSURANCE_TAX = RegistrationTypes.IP.value
    INCOME_TAX = RegistrationTypes.IT.value
    LOGGING_TAX = RegistrationTypes.LO.value
    MINERAL_LAND_TAX = RegistrationTypes.MD.value
    MINING_TAX = RegistrationTypes.MI.value
    MINERAL_TAX = RegistrationTypes.MR.value
    OTHER = RegistrationTypes.OT.value
    PETROLEUM_TAX = RegistrationTypes.PG.value
    PROV_SALES_TAX = RegistrationTypes.PS.value
    PROPERTY_TRANSFER_TAX = RegistrationTypes.PT.value
    RURAL_TAX = RegistrationTypes.RA.value
    SCHOOL_ACT = RegistrationTypes.SC.value
    SOCIAL_TAX = RegistrationTypes.SS.value
    TAX_LIEN = RegistrationTypes.TL.value
    TOBACCO_TAX = RegistrationTypes.TO.value
    SPECULATION_TAX = RegistrationTypes.SV.value


class MiscellaneousTypes(BaseEnum):
    """Render an Enum of the financing statement miscellaneous registration type class."""

    HC_NOTICE = RegistrationTypes.HN.value
    MAINTENANCE = RegistrationTypes.ML.value
    MH_NOTICE = RegistrationTypes.MN.value
    POC_NOTICE = RegistrationTypes.PN.value
    WAGES_UNPAID = RegistrationTypes.WL.value
    SECURITIES_NOTICE = RegistrationTypes.SE.value


class PPSATypes(BaseEnum):
    """Render an Enum of the financing statement PPSA lien registration type class."""

    COMMERCIAL_LIEN = RegistrationTypes.CL.value
    FORESTRY_CHARGE = RegistrationTypes.FA.value
    FORESTRY_LIEN = RegistrationTypes.FL.value
    MARRIAGE_SEPARATION = RegistrationTypes.FR.value
    FORESTRY_SUB_CHARGE = RegistrationTypes.FS.value
    LAND_TAX = RegistrationTypes.LT.value
    MH_LIEN = RegistrationTypes.MH.value
    REPAIRER_LIEN = RegistrationTypes.RL.value
    SECURITY_AGREEMENT = RegistrationTypes.SA.value
    SALE_GOODS = RegistrationTypes.SG.value


class Registration(db.Model):  # pylint: disable=too-many-instance-attributes, too-many-public-methods
    """This class manages all statement registration information."""

    class RegistrationTypes(BaseEnum):
        """Render an Enum of the registration types."""

        REG_CLASS_AMEND = "AMENDMENT"
        REG_CLASS_AMEND_COURT = "COURTORDER"
        REG_CLASS_CHANGE = "CHANGE"
        REG_CLASS_FINANCING = "PPSALIEN"
        REG_CLASS_DISCHARGE = "DISCHARGE"
        REG_CLASS_RENEWAL = "RENEWAL"

    __tablename__ = "registrations"
    __allow_unmapped__ = True

    # Always use get_generated_values() to generate PK.
    id = db.mapped_column("id", db.Integer, primary_key=True)
    registration_ts = db.mapped_column("registration_ts", db.DateTime, nullable=False, index=True)
    registration_num = db.mapped_column(
        "registration_number", db.String(10), nullable=False, index=True, default=db.func.get_registration_num()
    )
    base_registration_num = db.mapped_column("base_reg_number", db.String(10), nullable=True, index=True)
    account_id = db.mapped_column("account_id", db.String(20), nullable=True, index=True)
    client_reference_id = db.mapped_column("client_reference_id", db.String(50), nullable=True)
    life = db.mapped_column("life", db.Integer, nullable=True)
    lien_value = db.mapped_column("lien_value", db.String(15), nullable=True)
    surrender_date = db.mapped_column("surrender_date", db.DateTime, nullable=True)
    ver_bypassed = db.mapped_column("ver_bypassed", db.String(1), nullable=True)
    pay_invoice_id = db.mapped_column("pay_invoice_id", db.Integer, nullable=True)
    pay_path = db.mapped_column("pay_path", db.String(256), nullable=True)

    user_id = db.mapped_column("user_id", db.String(1000), nullable=True)
    detail_description = db.mapped_column("detail_description", db.String(4000), nullable=True)

    # parent keys
    financing_id = db.mapped_column(
        "financing_id", db.Integer, db.ForeignKey("financing_statements.id"), nullable=False, index=True
    )
    draft_id = db.mapped_column("draft_id", db.Integer, db.ForeignKey("drafts.id"), nullable=False, index=True)
    registration_type = db.mapped_column(
        "registration_type", db.String(2), db.ForeignKey("registration_types.registration_type"), nullable=False
    )
    registration_type_cl = db.mapped_column(
        "registration_type_cl",
        db.String(10),
        db.ForeignKey("registration_type_classes.registration_type_cl"),
        nullable=False,
    )

    # relationships
    financing_statement = db.relationship(
        "FinancingStatement",
        foreign_keys=[financing_id],
        back_populates="registration",
        cascade="all, delete",
        uselist=False,
    )
    reg_type = db.relationship(
        "RegistrationType",
        foreign_keys=[registration_type],
        back_populates="registration",
        cascade="all, delete",
        uselist=False,
    )
    parties = db.relationship("Party", order_by="asc(Party.id)", back_populates="registration")
    general_collateral = db.relationship("GeneralCollateral", back_populates="registration")
    general_collateral_legacy = db.relationship("GeneralCollateralLegacy", back_populates="registration")
    vehicle_collateral = db.relationship("VehicleCollateral", back_populates="registration")
    draft = db.relationship("Draft", foreign_keys=[draft_id], uselist=False)
    trust_indenture = db.relationship("TrustIndenture", back_populates="registration", uselist=False)
    court_order = db.relationship("CourtOrder", back_populates="registration", uselist=False)
    verification_report = db.relationship("VerificationReport", back_populates="registration", uselist=False)
    securities_act_notices = db.relationship(
        "SecuritiesActNotice", order_by="asc(SecuritiesActNotice.id)", back_populates="registration"
    )

    document_number: str = None
    # Use for pending payments
    reg_json = None

    @property
    def json(self) -> dict:
        """Return the registration as a json object."""
        registration = {
            "baseRegistrationNumber": self.base_registration_num,
            "createDateTime": model_utils.format_ts(self.registration_ts),
        }
        if self.registration_type == model_utils.REG_TYPE_DISCHARGE:
            registration["dischargeRegistrationNumber"] = self.registration_num
        elif self.registration_type == model_utils.REG_TYPE_RENEWAL:
            registration["renewalRegistrationNumber"] = self.registration_num
        elif self.registration_type_cl in (model_utils.REG_CLASS_AMEND, model_utils.REG_CLASS_AMEND_COURT):
            registration["amendmentRegistrationNumber"] = self.registration_num
            if self.detail_description:
                registration["description"] = self.detail_description
            if self.financing_statement.trust_indenture:
                for trust_indenture in self.financing_statement.trust_indenture:
                    if self.id == trust_indenture.registration_id:
                        registration["addTrustIndenture"] = True
                    elif self.id == trust_indenture.registration_id_end:
                        registration["removeTrustIndenture"] = True
            if (
                "addTrustIndenture" not in registration
                and self.trust_indenture
                and self.trust_indenture.trust_indenture == TrustIndenture.TRUST_INDENTURE_YES
            ):
                registration["addTrustIndenture"] = True
        else:
            registration["changeRegistrationNumber"] = self.registration_num

        if self.is_change():
            registration["changeType"] = self.registration_type

        if self.client_reference_id:
            registration["clientReferenceId"] = self.client_reference_id

        registration_id = self.id
        if self.parties:
            for party in self.parties:
                if party.party_type == model_utils.PARTY_REGISTERING and party.registration_id == registration_id:
                    registration["registeringParty"] = party.json

        if self.registration_type == model_utils.REG_TYPE_RENEWAL and self.life is not None:
            if self.life != model_utils.LIFE_INFINITE:
                registration["lifeYears"] = self.life
            if (
                self.life == model_utils.REPAIRER_LIEN_YEARS
                or self.financing_statement.registration[0].registration_type == model_utils.REG_TYPE_REPAIRER_LIEN
            ):
                # Computed expiry date is cumulatative: original 180 days + sum of renewals up to this one.
                registration["expiryDate"] = self.__get_renewal_rl_expiry()
            else:
                registration["expiryDate"] = self.__get_renewal_expiry()

        if self.court_order:
            registration["courtOrderInformation"] = self.court_order.json

        # add debtors, secured parties
        if self.parties and self.is_change():
            secured = []
            debtors = []
            for party in self.parties:
                if (
                    party.party_type in (model_utils.PARTY_DEBTOR_BUS, model_utils.PARTY_DEBTOR_IND)
                    and party.registration_id == registration_id
                ):
                    party_json = party.json
                    party_json["reg_id"] = party.registration_id
                    if "amendPartyId" not in party_json or party_json.get("amendPartyId", 0) > 0:
                        party_json["former_name"] = self.get_former_party_name(party)
                    debtors.append(party_json)
                elif party.party_type == model_utils.PARTY_SECURED and party.registration_id == registration_id:
                    party_json = party.json
                    party_json["reg_id"] = party.registration_id
                    if "amendPartyId" not in party_json or party_json.get("amendPartyId", 0) > 0:
                        party_json["former_name"] = self.get_former_party_name(party)
                    secured.append(party_json)
            if debtors:
                registration["addDebtors"] = debtors
            if secured:
                registration["addSecuredParties"] = secured

        # delete debtors, secured parties
        if self.financing_statement.parties and self.is_change():
            secured = []
            debtors = []
            for party in self.financing_statement.parties:
                if (
                    party.party_type in (model_utils.PARTY_DEBTOR_BUS, model_utils.PARTY_DEBTOR_IND)
                    and party.registration_id_end == registration_id
                ):
                    party_json = party.json
                    party_json["reg_id"] = party.registration_id_end
                    debtors.append(party_json)
                elif party.party_type == model_utils.PARTY_SECURED and party.registration_id_end == registration_id:
                    party_json = party.json
                    party_json["reg_id"] = party.registration_id_end
                    secured.append(party_json)

            if debtors:
                registration["deleteDebtors"] = debtors
            if secured:
                registration["deleteSecuredParties"] = secured

        if self.is_change():
            # general collateral changes including legacy
            registration_utils.set_add_general_collateral_json(self, registration, registration_id)
            registration_utils.set_delete_general_collateral_json(self, registration, registration_id)
            # vehicle collateral changes
            registration_utils.set_vehicle_collateral_json(self, registration, registration_id)
            registration_utils.set_securities_notices_json(self, registration, registration_id)

        return self.__set_payment_json(registration)

    def __set_payment_json(self, registration):
        """Add registration payment info json if payment exists."""
        if self.pay_invoice_id and self.pay_path:
            payment = {"invoiceId": str(self.pay_invoice_id), "receipt": self.pay_path}
            registration["payment"] = payment
        return registration

    def save(self):
        """Render a registration to the local cache."""
        db.session.add(self)
        db.session.commit()

        # Now save draft
        draft = self.draft
        db.session.add(draft)
        db.session.commit()

    def get_registration_type(self):
        """Lookup registration type record if it has not already been fetched."""
        if self.reg_type is None and self.registration_type:
            self.reg_type = (
                db.session.query(RegistrationType)
                .filter(RegistrationType.registration_type == self.registration_type)
                .one_or_none()
            )

    def is_financing(self):
        """Check if the registration is a financing registration for some conditions."""
        return self.registration_type_cl and self.registration_type_cl in (
            model_utils.REG_CLASS_CROWN,
            model_utils.REG_CLASS_MISC,
            model_utils.REG_CLASS_PPSA,
        )

    def is_change(self):
        """Check if the registration is a change or amendment for some conditions."""
        return self.registration_type_cl and self.registration_type_cl in (
            model_utils.REG_CLASS_AMEND,
            model_utils.REG_CLASS_AMEND_COURT,
            model_utils.REG_CLASS_CHANGE,
        )

    @classmethod
    def find_by_id(cls, registration_id: int):
        """Return the registration matching the id."""
        registration = None
        if registration_id:
            registration = db.session.query(Registration).filter(Registration.id == registration_id).one_or_none()
        return registration

    @classmethod
    def find_by_registration_number(
        cls, registration_num: str, account_id: str, staff: bool = False, base_reg_num: str = None
    ):
        """Return the registration matching the registration number."""
        registration = None
        if registration_num:
            try:
                registration = (
                    db.session.query(Registration)
                    .filter(Registration.registration_num == registration_num)
                    .one_or_none()
                )
            except Exception as db_exception:  # noqa: B902; return nicer error
                logger.error("DB find_by_registration_number exception: " + str(db_exception))
                raise DatabaseException(db_exception) from db_exception

        if not registration:
            raise BusinessException(
                error=model_utils.ERR_REGISTRATION_NOT_FOUND.format(
                    code=ResourceErrorCodes.NOT_FOUND_ERR, registration_num=registration_num
                ),
                status_code=HTTPStatus.NOT_FOUND,
            )
        # logger.info(f"staff={staff} account_id={account_id} reg account={registration.account_id}")
        if not staff and account_id and registration.account_id != account_id:
            # Check extra registrations
            extra_reg = UserExtraRegistration.find_by_registration_number(base_reg_num, account_id)
            if not extra_reg:
                raise BusinessException(
                    error=model_utils.ERR_REGISTRATION_ACCOUNT.format(
                        code=ResourceErrorCodes.UNAUTHORIZED_ERR,
                        account_id=account_id,
                        registration_num=registration_num,
                    ),
                    status_code=HTTPStatus.UNAUTHORIZED,
                )
        if not staff and model_utils.is_historical(registration.financing_statement, False):
            raise BusinessException(
                error=model_utils.ERR_FINANCING_HISTORICAL.format(
                    code=ResourceErrorCodes.HISTORICAL_ERR, registration_num=registration_num
                ),
                status_code=HTTPStatus.BAD_REQUEST,
            )
        if not staff and base_reg_num and base_reg_num != registration.base_registration_num:
            raise BusinessException(
                error=model_utils.ERR_REGISTRATION_MISMATCH.format(
                    code=ResourceErrorCodes.DATA_MISMATCH_ERR,
                    registration_num=registration_num,
                    base_reg_num=base_reg_num,
                ),
                status_code=HTTPStatus.BAD_REQUEST,
            )
        return registration

    @classmethod
    def get_account_reg_count(cls, account_id: str) -> int:
        """Get the total number of eligible financing statements for an account."""
        count: int = 0
        result = db.session.execute(text(model_utils.QUERY_ACCOUNT_REG_TOTAL), {"query_account": account_id})
        row = result.first()
        count = int(row[0])
        return count

    @classmethod
    def find_all_by_account_id(cls, params: AccountRegistrationParams, new_feature_enabled: bool):
        # pylint: disable=too-many-locals
        """Return a summary list of recent registrations belonging to an account.

        To access a verification statement report, one of the followng conditions must be true:
        1. The request account ID matches the registration account ID.
        2. The request account name matches the registration registering party name.
        3. The request account name matches one of the base registration secured party names.
        """
        results_json = []
        if params is None or params.account_id is None:
            return results_json

        registrations_json = []
        try:
            if params.from_ui:
                return Registration.find_all_by_account_id_filter(params, new_feature_enabled)
            if registration_utils.api_account_reg_filter(params):
                return Registration.find_all_by_account_id_api_filter(params, new_feature_enabled)

            results = db.session.execute(
                text(registration_utils.QUERY_ACCOUNT_REGISTRATIONS),
                {"query_account": params.account_id, "max_results_size": model_utils.MAX_ACCOUNT_REGISTRATIONS_DEFAULT},
            )
            rows = results.fetchall()
            if rows is not None:
                for row in rows:
                    removed_count = int(row[14])
                    if removed_count < 1:
                        reg_num = str(row[0])
                        base_reg_num = str(row[6])
                        registering_name = str(row[13]) if row[13] else ""
                        result = {
                            "accountId": str(row[4]),
                            "registrationNumber": reg_num,
                            "baseRegistrationNumber": base_reg_num,
                            "createDateTime": model_utils.format_ts(row[1]),
                            "registrationType": str(row[2]),
                            "registrationDescription": str(row[5]),
                            "registrationClass": str(row[3]),
                            "statusType": str(row[7]),
                            "expireDays": int(row[8]),
                            "lastUpdateDateTime": model_utils.format_ts(row[9]),
                            "registeringParty": str(row[10]),
                            "securedParties": str(row[11]),
                            "clientReferenceId": str(row[12]),
                            "registeringName": registering_name,
                        }
                        result["legacy"] = result.get("accountId") == "0"
                        result = registration_utils.set_path(params, result, reg_num, base_reg_num)

                        if (
                            result["statusType"] == model_utils.STATE_ACTIVE
                            and result["expireDays"] < 0
                            and result["expireDays"] != -99
                        ):
                            result["statusType"] = model_utils.STATE_EXPIRED

                        result = registration_utils.update_summary_optional(result, params.account_id, params.sbc_staff)
                        if "accountId" in result:
                            del result["accountId"]  # Only use this for report access checking.

                        if params.collapse and not model_utils.is_financing(result["registrationClass"]):
                            registrations_json.append(result)
                        else:
                            results_json.append(result)
                if params.collapse:
                    return registration_utils.build_account_collapsed_json(results_json, registrations_json)
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error("DB find_all_by_account_id exception: " + str(db_exception))
            raise DatabaseException(db_exception) from db_exception
        return results_json

    @classmethod
    def find_all_by_account_id_filter(cls, params: AccountRegistrationParams, new_feature_enabled: bool):
        # pylint: disable=too-many-locals
        """Return a summary list of registrations belonging to an account applying filters."""
        results_json = []
        count = Registration.get_account_reg_count(params.account_id)
        query = registration_utils.build_account_reg_query(params, new_feature_enabled)
        query_params = registration_utils.build_account_query_params(params)
        results = db.session.execute(text(query), query_params)
        rows = results.fetchall()
        results_json = registration_utils.build_account_base_reg_results(params, rows)
        if results_json:
            results_json[0]["totalRegistrationCount"] = count
            # Get change registrations.
            query = registration_utils.build_account_change_query(params, results_json)
            results = db.session.execute(text(query), query_params)
            rows = results.fetchall()
            results_json = registration_utils.update_account_reg_results(params, rows, results_json)
        return results_json

    @classmethod
    def find_all_by_account_id_api_filter(cls, params: AccountRegistrationParams, new_feature_enabled: bool):
        """Return a summary list of registrations belonging to an api account applying filters."""
        results_json = []
        # Restrict filter to client ref id, reg number, or timestamp range.
        params.page_number = 1
        params.sort_direction = "desc"
        params.sort_criteria = None
        params.registration_type = None
        params.status_type = None
        params.registering_name = None
        query = registration_utils.build_account_reg_query(params, new_feature_enabled)
        query_params = registration_utils.build_account_query_params(params, True)
        results = db.session.execute(text(query), query_params)
        rows = results.fetchall()
        results_json = registration_utils.build_account_base_reg_results(params, rows, True)
        if results_json:
            # Get change registrations.
            query = registration_utils.build_account_change_query(params, results_json)
            results = db.session.execute(text(query), query_params)
            rows = results.fetchall()
            results_json = registration_utils.update_account_reg_results(params, rows, results_json, True)
        return results_json

    @classmethod
    def find_summary_by_reg_num(
        cls, account_id: str, registration_num: str, account_name: str = None, sbc_staff: bool = False
    ):
        """Return a single registration summary by registration_number."""
        result = {}
        changes = []
        if account_id is None or registration_num is None:
            return result
        try:
            results = db.session.execute(
                text(registration_utils.QUERY_ACCOUNT_ADD_REGISTRATION),
                {"query_account": account_id, "query_reg_num": registration_num},
            )
            rows = results.fetchall()
            if rows is not None:
                for row in rows:
                    reg_num = str(row[0])
                    base_reg_num = str(row[5])
                    reg_class = str(row[3])
                    result = registration_utils.build_add_reg_result(row, reg_class, base_reg_num, reg_num)
                    if model_utils.is_financing(reg_class):
                        # Another account already added.
                        if result["existsCount"] > 0 and result["accountId"] not in (account_id, account_id + "_R"):
                            result["inUserList"] = True
                        # User account previously removed (can be added back).
                        elif result["existsCount"] > 0 and result["accountId"] in (account_id, account_id + "_R"):
                            result["inUserList"] = False
                        # User account added by default.
                        elif result["accountId"] == account_id:
                            result["inUserList"] = True
                        # Another account excluded by default.
                        else:
                            result["inUserList"] = False
                    # Set if user can access verification statement.
                    if not registration_utils.can_access_report(account_id, account_name, result, sbc_staff):
                        result["path"] = ""
                    if is_staff_account(account_id):
                        if result.get("accountId", "0") == "0":
                            result["accountId"] = "N/A"
                        elif row[18]:
                            result["accountId"] = str(row[18])
                    result = registration_utils.update_summary_optional(result, account_id, sbc_staff)
                    if not model_utils.is_financing(reg_class):
                        changes.append(result)
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error("DB find_summary_by_reg_num exception: " + str(db_exception))
            raise DatabaseException(db_exception) from db_exception
        if not result:
            return None
        if result and changes:
            result["changes"] = changes
        return result

    def verification_json(self, reg_num_name: str):
        """Generate verification statement json for API response and verification reports."""
        self.financing_statement.current_view_json = True  # Changed to include the consolidated/current view.
        self.financing_statement.mark_update_json = True
        self.financing_statement.include_changes_json = True
        self.financing_statement.verification_reg_id = self.id
        verification_json = self.financing_statement.json
        verification_json[reg_num_name] = self.registration_num
        return verification_json

    @staticmethod
    def create_from_json(
        json_data, registration_type_cl: str, financing_statement, base_registration_num: str, account_id: str = None
    ):
        """Create a registration object for an existing financing statement from dict/json."""
        # Create or update draft.
        draft = Registration.find_draft(json_data, None, None)
        reg_vals = Registration.get_generated_values(draft)
        registration = Registration()
        registration.id = reg_vals.id  # pylint: disable=invalid-name; allow name of id.
        registration.registration_num = reg_vals.registration_num
        registration.financing_id = financing_statement.id
        registration.financing_statement = financing_statement
        registration.account_id = account_id
        registration.base_registration_num = base_registration_num
        registration_utils.set_registration_basic_info(registration, json_data, registration_type_cl)
        if not draft:
            registration.document_number = reg_vals.document_number
            draft = Draft.create_from_registration(registration, json_data)
        else:
            draft.draft = json_data
        draft.account_id = draft.account_id + ACCOUNT_DRAFT_USED_SUFFIX
        registration.draft = draft
        registration.draft.registration_type = registration.registration_type
        registration.draft.registration_type_cl = registration.registration_type_cl
        # All registrations have at least one party (registering).
        registration.parties = Party.create_from_statement_json(
            json_data, registration_type_cl, registration.financing_id
        )
        # If get to here all data should be valid: get reg id to close out updated entities.
        registration_id = registration.id
        financing_reg_type = registration.financing_statement.registration[0].registration_type
        if registration_type_cl == model_utils.REG_CLASS_DISCHARGE:
            registration.financing_statement.state_type = model_utils.STATE_DISCHARGED
            registration.financing_statement.discharged = "Y"
        elif registration_type_cl == model_utils.REG_CLASS_RENEWAL:
            registration_utils.set_renewal_life(registration, json_data, financing_reg_type)
        # Repairer's lien renewal or amendment can have court order information.
        if (
            registration.registration_type in (model_utils.REG_TYPE_AMEND_COURT, model_utils.REG_TYPE_RENEWAL)
            and "courtOrderInformation" in json_data
        ):
            registration.court_order = CourtOrder.create_from_json(json_data["courtOrderInformation"], registration_id)

        if registration_type_cl in (
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
            Registration.delete_from_json(json_data, registration, financing_statement)

        return registration

    @staticmethod
    def create_financing_from_json(json_data, account_id: str = None, user_id: str = None):
        """Create a registraion object from dict/json."""
        registration = Registration()
        registration.account_id = account_id
        registration.user_id = user_id
        registration.registration_ts = model_utils.now_ts()
        reg_type = json_data["type"]
        registration.registration_type_cl = model_utils.REG_TYPE_TO_REG_CLASS[reg_type]
        registration.registration_type = reg_type
        registration.ver_bypassed = "Y"

        if reg_type == model_utils.REG_TYPE_REPAIRER_LIEN:
            if "lienAmount" in json_data:
                registration.lien_value = json_data["lienAmount"].strip()
            if "surrenderDate" in json_data:
                registration.surrender_date = model_utils.ts_from_date_iso_format(json_data["surrenderDate"])
            registration.life = model_utils.REPAIRER_LIEN_YEARS
        elif "lifeInfinite" in json_data and json_data["lifeInfinite"]:
            registration.life = model_utils.LIFE_INFINITE
        elif registration.registration_type_cl in (model_utils.REG_CLASS_CROWN, model_utils.REG_CLASS_MISC):
            registration.life = model_utils.LIFE_INFINITE
        elif reg_type in (
            model_utils.REG_TYPE_MARRIAGE_SEPARATION,
            model_utils.REG_TYPE_TAX_MH,
            model_utils.REG_TYPE_LAND_TAX_MH,
        ):
            registration.life = model_utils.LIFE_INFINITE
        elif "lifeYears" in json_data:
            registration.life = json_data["lifeYears"]

        if "clientReferenceId" in json_data:
            registration.client_reference_id = json_data["clientReferenceId"]
        # Create or update draft.
        draft = Registration.find_draft(json_data, registration.registration_type_cl, reg_type)
        reg_vals = Registration.get_generated_values(draft)
        registration.id = reg_vals.id
        registration.registration_num = reg_vals.registration_num
        if not draft:
            registration.document_number = reg_vals.document_number
            draft = Draft.create_from_registration(registration, json_data, user_id)
        else:
            draft.draft = json_data
        draft.account_id = draft.account_id + ACCOUNT_DRAFT_USED_SUFFIX
        registration.draft = draft
        if reg_type == MiscellaneousTypes.SECURITIES_NOTICE and json_data.get("securitiesActNotices"):
            registration = registration_utils.create_securities_act_notices(registration, json_data)
        return registration

    @staticmethod
    def delete_from_json(json_data, registration, financing_statement):
        """For deleted parties, collateral, trust, notices in registrations set registration_id_end from dict/json."""
        if "deleteDebtors" in json_data and json_data["deleteDebtors"]:
            for party in json_data["deleteDebtors"]:
                existing = Registration.find_party_by_id(
                    party["partyId"], model_utils.PARTY_DEBTOR_BUS, financing_statement.parties
                )
                if existing:
                    existing.registration_id_end = registration.id
        if "deleteSecuredParties" in json_data and json_data["deleteSecuredParties"]:
            for party in json_data["deleteSecuredParties"]:
                existing = Registration.find_party_by_id(
                    party["partyId"], model_utils.PARTY_SECURED, financing_statement.parties
                )
                if existing:
                    existing.registration_id_end = registration.id
        if "deleteVehicleCollateral" in json_data and json_data["deleteVehicleCollateral"]:
            for vehicle_c in json_data["deleteVehicleCollateral"]:
                collateral = Registration.find_vehicle_collateral_by_id(
                    vehicle_c["vehicleId"], financing_statement.vehicle_collateral
                )
                if collateral:
                    collateral.registration_id_end = registration.id
        if (
            "removeTrustIndenture" in json_data
            and json_data["removeTrustIndenture"]
            and financing_statement.trust_indenture
        ):
            for trust_indenture in financing_statement.trust_indenture:
                if trust_indenture.registration_id != registration.id and not trust_indenture.registration_id_end:
                    trust_indenture.registration_id_end = registration.id
        # Could be transitioning with removed with a record to added: close out removed record.
        elif (
            "addTrustIndenture" in json_data and json_data["addTrustIndenture"] and financing_statement.trust_indenture
        ):
            for trust_indenture in financing_statement.trust_indenture:
                if trust_indenture.registration_id != registration.id and not trust_indenture.registration_id_end:
                    trust_indenture.registration_id_end = registration.id
        if (
            json_data.get("deleteSecuritiesActNotices")
            and financing_statement.registration[0].registration_type == MiscellaneousTypes.SECURITIES_NOTICE
        ):
            for del_json in json_data.get("deleteSecuritiesActNotices"):
                notice = registration_utils.find_securities_notice_by_id(del_json.get("noticeId"), financing_statement)
                if notice:
                    notice.registration_id_end = registration.id

    @staticmethod
    def find_draft(json_data, registration_class: str, registration_type: str):
        """Try to find an existing draft if a documentId is in json_data.).

        Return None if not found or no documentId.
        """
        draft = None
        if "documentId" in json_data:
            try:
                doc_id = json_data["documentId"].strip()
                if doc_id != "":
                    draft = Draft.find_by_document_number(doc_id, False)
                    if draft:
                        draft.document_number = doc_id
                        draft.draft = json.dumps(json_data)
                        if registration_class and registration_type:
                            draft.registration_type_cl = registration_class
                            draft.registration_type = registration_type
            except BusinessException:
                draft = None
        return draft

    @staticmethod
    def get_generated_values(draft):
        """Get db generated identifiers that are in more than one table.

        Get registration_id, registration_number, and optionally document_number.
        """
        registration = Registration()
        # generate reg id, reg number. If not existing draft also generate doc number
        query = """
        select nextval('registration_id_seq') AS reg_id,
               get_registration_num() AS reg_num,
               get_draft_document_number() AS doc_num
        """
        if draft:
            query = "select nextval('registration_id_seq') AS reg_id, get_registration_num() AS reg_num"
        result = db.session.execute(text(query))
        row = result.first()
        registration.id = int(row[0])
        registration.registration_num = str(row[1])
        if not draft:
            registration.document_number = str(row[2])
        return registration

    @staticmethod
    def find_party_by_id(party_id: int, party_type: str, parties):
        """Search existing list of party objects for a matching party id and type."""
        party = None
        if party_id and party_type and parties:
            for eval_party in parties:
                if (
                    eval_party.id == party_id
                    and party_type == eval_party.party_type
                    and not eval_party.registration_id_end
                ):
                    party = eval_party
                elif (
                    eval_party.id == party_id
                    and party_type == model_utils.PARTY_DEBTOR_BUS
                    and eval_party.party_type == model_utils.PARTY_DEBTOR_IND
                    and not eval_party.registration_id_end
                ):
                    party = eval_party
        return party

    @staticmethod
    def find_vehicle_collateral_by_id(vehicle_id: int, vehicle_collateral):
        """Search existing list of vehicle_collateral objects for a matching vehicle id."""
        collateral = None
        if vehicle_id and vehicle_collateral:
            for v_collateral in vehicle_collateral:
                if v_collateral.id == vehicle_id and not v_collateral.registration_id_end:
                    collateral = v_collateral
        return collateral

    @staticmethod
    def find_general_collateral_by_id(collateral_id: int, general_collateral):
        """Search existing list of general_collateral objects for a matching collateral id."""
        collateral = None
        if collateral_id and general_collateral:
            for g_collateral in general_collateral:
                if g_collateral.id == collateral_id and not g_collateral.registration_id_end:
                    collateral = g_collateral
        return collateral

    def get_former_party_name(self, new_party: Party):
        """Search parties for a party former name: add and remove in the same registration and addresses match."""
        former_name = ""
        for party in self.financing_statement.parties:
            if new_party.party_type == party.party_type and new_party.registration_id == party.registration_id_end:
                # If address change do not return a former name.
                address1 = party.address
                address2 = new_party.address
                if address1 is None and party.client_code:
                    address1 = party.client_code.address
                if address2 is None and new_party.client_code:
                    address2 = new_party.client_code.address
                if (  # pylint: disable=too-many-boolean-expressions
                    address1
                    and address2
                    and address1.json != address2.json
                    and (
                        not new_party.previous_party_id
                        or (new_party.previous_party_id and new_party.previous_party_id == party.id)
                    )
                ):
                    return former_name
                # Could only be changing a birthdate (names are identical).
                if new_party.previous_party_id and new_party.previous_party_id == party.id:
                    if (
                        party.client_code
                        and party.client_code.name
                        and new_party.business_name
                        and new_party.business_name != party.client_code.name
                    ):
                        former_name = party.client_code.name
                    elif (
                        party.business_name
                        and new_party.business_name
                        and new_party.business_name != party.business_name
                    ):
                        former_name = party.business_name
                    else:
                        former_name = self.__get_matching_party_name(new_party, party)
                    return former_name
                if address1 and address2 and address1.json == address2.json:
                    if (
                        party.client_code
                        and party.client_code.name
                        and new_party.business_name
                        and new_party.business_name != party.client_code.name
                    ):
                        former_name = party.client_code.name
                    elif (
                        party.business_name
                        and new_party.business_name
                        and new_party.business_name != party.business_name
                    ):
                        former_name = party.business_name
                    else:
                        # match if only 1 name is different in addition to same address.
                        former_name = Registration.__get_matching_party_name(new_party, party)
        return former_name

    @staticmethod
    def __get_matching_party_name(new_party: Party, party: Party):
        """Match name only if one name part has changed (addresses already match."""
        former_name: str = ""
        found: bool = False
        if new_party.last_name == party.last_name and new_party.first_name != party.first_name:
            found = True
        elif new_party.last_name != party.last_name and new_party.first_name == party.first_name:
            found = True
        elif new_party.last_name == party.last_name and new_party.first_name == party.first_name:
            if (
                (new_party.middle_initial is None and party.middle_initial is not None)
                or (new_party.middle_initial is not None and party.middle_initial is None)
                or (new_party.middle_initial != party.middle_initial)
            ):
                found = True
        if found:
            former_name = party.last_name + ", " + party.first_name
            if party.middle_initial:
                former_name += " " + party.middle_initial
        return former_name

    def __get_renewal_rl_expiry(self):
        """Build a repairer's lien expiry date as the sum of previous registrations."""
        expiry_ts = None
        for registration in self.financing_statement.registration:
            if registration.registration_type_cl in (
                model_utils.REG_CLASS_CROWN,
                model_utils.REG_CLASS_MISC,
                model_utils.REG_CLASS_PPSA,
            ):
                expiry_ts = model_utils.expiry_dt_from_registration(registration.registration_ts, None)
        for registration in self.financing_statement.registration:
            if registration.registration_type == model_utils.REG_TYPE_RENEWAL and registration.id <= self.id:
                expiry_ts = model_utils.expiry_dt_repairer_lien(expiry_ts)
        return model_utils.format_ts(expiry_ts)

    def __get_renewal_expiry(self):
        """Build a non-repairer's lien expiry date as the sum of previous registrations."""
        if self.life == model_utils.LIFE_INFINITE:
            return "Never"
        expiry_ts = None
        for registration in self.financing_statement.registration:
            if registration.registration_type_cl in (
                model_utils.REG_CLASS_CROWN,
                model_utils.REG_CLASS_MISC,
                model_utils.REG_CLASS_PPSA,
            ):
                expiry_ts = model_utils.expiry_dt_from_registration(registration.registration_ts, registration.life)
        for registration in self.financing_statement.registration:
            if registration.registration_type == model_utils.REG_TYPE_RENEWAL and registration.id <= self.id:
                expiry_ts = model_utils.expiry_dt_add_years(expiry_ts, registration.life)
        return model_utils.format_ts(expiry_ts)
