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
"""This module holds model data and database operations for financing statements."""
# flake8: noqa E127
# pylint: disable=too-many-statements, too-many-branches, too-many-nested-blocks; not working at method scope

from __future__ import annotations

from http import HTTPStatus

from flask import current_app
from sqlalchemy.sql import text

from ppr_api.exceptions import BusinessException, DatabaseException, ResourceErrorCodes
from ppr_api.models import utils as model_utils
from ppr_api.models.type_tables import RegistrationType, RegistrationTypes
from ppr_api.utils.base import BaseEnum
from ppr_api.utils.logging import logger

from .db import db
from .general_collateral import (  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
    GeneralCollateral,
)
from .general_collateral_legacy import GeneralCollateralLegacy  # noqa: F401 pylint: disable=unused-import; see above
from .party import Party  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
from .registration import (  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
    Registration,
)
from .securities_act_notice import (  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
    SecuritiesActNotice,
)
from .trust_indenture import (  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
    TrustIndenture,
)
from .user_extra_registration import (  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
    UserExtraRegistration,
)
from .vehicle_collateral import (  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
    VehicleCollateral,
)


class FinancingStatement(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class maintains financing statement information."""

    class FinancingTypes(BaseEnum):
        """Render an Enum of the financing statement types."""

        SECURITY_AGREEMENT = "SA"
        SALE_OF_GOODS = "SG"
        REPAIRERS_LIEN = "RL"
        MARRIAGE_MH = "FR"
        LAND_TAX_LIEN = "LT"
        MANUFACTURED_HOME_LIEN = "MH"
        FORESTRY_CONTRACTOR_LIEN = "FL"
        FORESTRY_CONTRACTOR_CHARGE = "FA"
        FORESTRY_SUBCONTRACTOR_LIEN = "FS"
        MISCELLANEOUS = "MR"

    __tablename__ = "financing_statements"
    __allow_unmapped__ = True

    id = db.mapped_column("id", db.Integer, db.Sequence("financing_id_seq"), primary_key=True)
    state_type = db.mapped_column("state_type", db.String(3), db.ForeignKey("state_types.state_type"), nullable=False)
    life = db.mapped_column("life", db.Integer, nullable=True)
    expire_date = db.mapped_column("expire_date", db.DateTime, nullable=True)
    discharged = db.mapped_column("discharged", db.String(1), nullable=True)
    renewed = db.mapped_column("renewed", db.String(1), nullable=True)

    type_claim = db.mapped_column("type_claim", db.String(2), nullable=True)
    crown_charge_type = db.mapped_column("crown_charge_type", db.String(2), nullable=True)
    crown_charge_other = db.mapped_column("crown_charge_other", db.String(70), nullable=True)

    # Parent keys

    # Relationships
    registration = db.relationship(
        "Registration", order_by="asc(Registration.registration_ts)", back_populates="financing_statement"
    )
    parties = db.relationship("Party", order_by="asc(Party.id)", back_populates="financing_statement")
    vehicle_collateral = db.relationship(
        "VehicleCollateral", order_by="asc(VehicleCollateral.id)", back_populates="financing_statement"
    )
    general_collateral = db.relationship(
        "GeneralCollateral", order_by="asc(GeneralCollateral.id)", back_populates="financing_statement"
    )
    general_collateral_legacy = db.relationship(
        "GeneralCollateralLegacy",
        order_by="asc(GeneralCollateralLegacy.registration_id)",
        back_populates="financing_statement",
    )
    trust_indenture = db.relationship("TrustIndenture", back_populates="financing_statement")
    previous_statement = db.relationship("PreviousFinancingStatement", back_populates="financing_statement")
    # Relationships - StateType
    fin_state_type = db.relationship(
        "StateType",
        foreign_keys=[state_type],
        back_populates="financing_statement",
        cascade="all, delete",
        uselist=False,
    )

    # Use to indicate if a party or collateral is not in the original financing statement.
    mark_update_json = False
    # Use to specify if generated json content is current state or original financing statement.
    current_view_json = True
    # Use to include/exclude all change statement data in the financing statement json for search results.
    include_changes_json = False
    # Use to include/exclude registration history at the time of the registration for verfication statements.
    verification_reg_id = 0

    @property
    def json(self) -> dict:
        """Return the financing statement as a json object."""
        statement = {"statusType": self.state_type}
        if self.state_type == model_utils.STATE_DISCHARGED:
            index = len(self.registration) - 1
            statement["dischargedDateTime"] = model_utils.format_ts(self.registration[index].registration_ts)
        if not self.current_view_json and self.state_type != model_utils.STATE_ACTIVE:
            statement["statusType"] = model_utils.STATE_ACTIVE
        elif (
            self.current_view_json
            and self.state_type == model_utils.STATE_ACTIVE
            and self.expire_date
            and self.expire_date.timestamp() < model_utils.now_ts().timestamp()
        ):
            statement["statusType"] = model_utils.STATE_EXPIRED

        if self.registration and self.registration[0]:
            reg = self.registration[0]
            registration_id = reg.id
            statement["type"] = reg.registration_type
            statement["baseRegistrationNumber"] = reg.registration_num
            if reg.registration_type:
                statement["registrationDescription"] = reg.reg_type.registration_desc
                statement["registrationAct"] = reg.reg_type.registration_act
                if reg.registration_type == model_utils.REG_TYPE_OTHER and self.crown_charge_other:
                    statement["otherTypeDescription"] = self.crown_charge_other
                    statement["registrationDescription"] = (
                        f"CROWN CHARGE - OTHER - FILED PURSUANT TO {self.crown_charge_other.upper()}"
                    )

            statement["createDateTime"] = model_utils.format_ts(reg.registration_ts)
            if reg.client_reference_id:
                statement["clientReferenceId"] = reg.client_reference_id
            statement["registeringParty"] = self.party_json(Party.PartyTypes.REGISTERING_PARTY.value, registration_id)
            statement["securedParties"] = self.party_json(Party.PartyTypes.SECURED_PARTY.value, registration_id)
            statement["debtors"] = self.party_json(Party.PartyTypes.DEBTOR_COMPANY.value, registration_id)

            general_collateral = self.general_collateral_json(registration_id)
            if general_collateral:
                statement["generalCollateral"] = general_collateral

            vehicle_collateral = self.vehicle_collateral_json(registration_id)
            if vehicle_collateral:
                statement["vehicleCollateral"] = vehicle_collateral

            if reg.registration_type in (RegistrationTypes.RL.value, RegistrationTypes.CL.value):
                if reg.lien_value:
                    statement["lienAmount"] = reg.lien_value
                if reg.surrender_date:
                    statement["surrenderDate"] = model_utils.format_ts(reg.surrender_date)
            if reg.registration_type == RegistrationTypes.SE.value:
                statement["securitiesActNotices"] = self.securities_act_notices_json(registration_id)
            elif reg.registration_type == RegistrationTypes.CL.value:
                statement["transitioned"] = FinancingStatement.is_rl_transition(reg)

        if self.trust_indenture:
            for trust in self.trust_indenture:
                if not trust.registration_id_end:
                    if trust.trust_indenture == "Y":
                        statement["trustIndenture"] = True
                    else:
                        statement["trustIndenture"] = False
        else:
            statement["trustIndenture"] = False

        if self.current_view_json:
            if self.life and self.life == model_utils.LIFE_INFINITE:
                statement["lifeInfinite"] = True
            elif self.life:
                statement["lifeYears"] = self.life

            if self.expire_date:
                statement["expiryDate"] = model_utils.format_ts(self.expire_date)
        else:
            # Set the original life years and expiry date: not current view is the verification statement
            registration = self.registration[0]
            if registration.life == model_utils.LIFE_INFINITE:
                statement["lifeInfinite"] = True
            elif registration.life:
                statement["lifeYears"] = registration.life
                expiry = model_utils.expiry_dt_from_registration(registration.registration_ts, registration.life)
                statement["expiryDate"] = model_utils.format_ts(expiry)
            elif model_utils.REG_TYPE_REPAIRER_LIEN == registration.registration_type:
                statement["lifeYears"] = 0
                expiry = model_utils.expiry_dt_repairer_lien(registration.registration_ts)
                statement["expiryDate"] = model_utils.format_ts(expiry)
        self.set_court_order_json(statement)
        self.set_payment_json(statement)
        self.set_transition_json(statement)
        return self.set_changes_json(statement)

    def set_court_order_json(self, statement):
        """Add court order info to the statement json if generating the current view and court order info exists."""
        if self.current_view_json:
            for registration in self.registration:
                if registration.court_order:
                    statement["courtOrderInformation"] = registration.court_order.json

    def set_changes_json(self, statement):
        """Add history of changes in reverse chronological order to financing statement json."""
        if self.include_changes_json and self.registration and len(self.registration) > 1:
            changes = []
            cl_timestamp = None
            if statement.get("transitioned"):
                cl_timestamp = model_utils.get_cl_transition_ts()
            for reg in reversed(self.registration):
                if reg.registration_type_cl not in ("PPSALIEN", "MISCLIEN", "CROWNLIEN") and (
                    self.verification_reg_id < 1 or reg.id <= self.verification_reg_id
                ):
                    statement_json = reg.json
                    if cl_timestamp and reg.registration_ts > cl_timestamp:
                        statement_json["transitioned"] = True
                    statement_json["statementType"] = model_utils.REG_CLASS_TO_STATEMENT_TYPE[reg.registration_type_cl]
                    changes.append(statement_json)
            statement["changes"] = changes
        return statement

    def set_payment_json(self, statement):
        """Add financing statement payment info json if payment exists."""
        if self.registration and self.registration[0].pay_invoice_id:
            payment = {"invoiceId": str(self.registration[0].pay_invoice_id), "receipt": self.registration[0].pay_path}
            statement["payment"] = payment
        return statement

    def set_transition_json(self, statement):
        """Add financing statement transition json if a previous financing statement exists."""
        if self.previous_statement and self.previous_statement[0].registration_type:
            previous_json = self.previous_statement[0].json
            statement["transitionDescription"] = previous_json.get("transitionDescription")
            if previous_json.get("transitionDate"):
                statement["transitionDate"] = previous_json.get("transitionDate")
            if previous_json.get("transitionNumber"):
                statement["transitionNumber"] = previous_json.get("transitionNumber")
        return statement

    def party_json(self, party_type, registration_id):
        """Build party JSON: current_view_json determines if current or original data is included."""
        if party_type == Party.PartyTypes.REGISTERING_PARTY.value:
            for party in self.parties:
                if party.party_type == party_type and registration_id == party.registration_id:
                    return party.json
            # No registering party record: legacy data.
            return {}

        parties = []
        for party in self.parties:
            party_json = None
            if party.party_type == party_type or (
                party_type == Party.PartyTypes.DEBTOR_COMPANY.value
                and party.party_type == Party.PartyTypes.DEBTOR_INDIVIDUAL.value
            ):
                # If not current view only display financing statement registration parties.
                # If current view and verification registration ID exists, include all active parties at the
                # time of the registration.
                # If current view include all active parties.
                if party.registration_id == registration_id and (
                    not party.registration_id_end or not self.current_view_json
                ):
                    party_json = party.json
                elif (
                    self.current_view_json
                    and party.registration_id_end
                    and self.verification_reg_id > 0
                    and self.verification_reg_id >= party.registration_id
                    and self.verification_reg_id < party.registration_id_end
                ):
                    party_json = party.json
                    if self.mark_update_json and party.registration_id != registration_id:
                        party_json["added"] = True
                elif (
                    self.current_view_json
                    and not party.registration_id_end
                    and (self.verification_reg_id < 1 or self.verification_reg_id >= party.registration_id)
                ):
                    party_json = party.json
                    if self.mark_update_json and party.registration_id != registration_id:
                        party_json["added"] = True

            if party_json:
                parties.append(party_json)

        return parties

    def general_collateral_json(self, registration_id):
        """Build general collateral JSON: current_view_json determines if current or original data is included."""
        if not self.general_collateral and not self.general_collateral_legacy:
            return None
        collateral_json = []
        collateral_json = self.__build_general_collateral_json(registration_id, collateral_json, False)
        collateral_json = self.__build_general_collateral_json(registration_id, collateral_json, True)
        return collateral_json

    def __build_general_collateral_json(
        self, registration_id, collateral_json, legacy: bool
    ):  # pylint: disable=too-many-nested-blocks
        """Build general collateral JSON for a financing statement from either the API or legacy table."""
        collateral_list = None
        if (not legacy and not self.general_collateral) or (legacy and not self.general_collateral_legacy):
            return collateral_json
        if not legacy:
            collateral_list = reversed(self.general_collateral)
        else:
            collateral_list = reversed(self.general_collateral_legacy)

        for collateral in collateral_list:
            if collateral.registration_id == registration_id or not collateral.status:
                gc_json = collateral.json
                collateral_json.append(gc_json)
            # Add only solution for legacy records: current view shows all records including deleted.
            elif self.current_view_json and (
                self.verification_reg_id < 1 or self.verification_reg_id >= collateral.registration_id
            ):
                gc_json = collateral.current_json
                exists = False
                # If amendment/change registration is 1 add, 1 remove then combine them.
                if self.__is_edit_general_collateral(collateral.registration_id, legacy):
                    for exists_collateral in collateral_json:
                        if exists_collateral["addedDateTime"] == gc_json["addedDateTime"]:
                            if (
                                "descriptionAdd" in exists_collateral
                                and "descriptionDelete" not in exists_collateral
                                and "descriptionDelete" in gc_json
                            ):
                                exists = True
                                exists_collateral["descriptionDelete"] = gc_json["descriptionDelete"]
                            elif (
                                "descriptionDelete" in exists_collateral
                                and "descriptionAdd" not in exists_collateral
                                and "descriptionAdd" in gc_json
                            ):
                                exists = True
                                exists_collateral["descriptionAdd"] = gc_json["descriptionAdd"]
                if not exists:
                    collateral_json.append(gc_json)
        return collateral_json

    def __is_edit_general_collateral(self, registration_id, legacy: bool):
        """True if an amendment adds 1 gc and removes 1 gc."""
        add_count = 0
        delete_count = 0
        collateral_list = self.general_collateral if not legacy else self.general_collateral_legacy
        for collateral in collateral_list:
            if collateral.registration_id == registration_id and collateral.status:
                if collateral.status == GeneralCollateralLegacy.StatusTypes.ADDED:
                    add_count += 1
                elif collateral.status == GeneralCollateralLegacy.StatusTypes.DELETED:
                    delete_count += 1
        return add_count == 1 and delete_count == 1

    def vehicle_collateral_json(self, registration_id):
        """Build vehicle collateral JSON: current_view_json determines if current or original data is included."""
        if not self.vehicle_collateral:
            return None

        collateral_list = []
        for collateral in self.vehicle_collateral:
            collateral_json = None
            if collateral.registration_id == registration_id and (
                not collateral.registration_id_end or not self.current_view_json
            ):
                collateral_json = collateral.json
            elif (
                self.current_view_json
                and collateral.registration_id_end
                and self.verification_reg_id > 0
                and self.verification_reg_id >= collateral.registration_id
                and self.verification_reg_id < collateral.registration_id_end
            ):
                collateral_json = collateral.json
                if self.mark_update_json and collateral.registration_id != registration_id:
                    collateral_json["added"] = True
            elif (
                self.current_view_json
                and not collateral.registration_id_end
                and (self.verification_reg_id < 1 or self.verification_reg_id >= collateral.registration_id)
            ):
                collateral_json = collateral.json
                if self.mark_update_json and collateral.registration_id != registration_id:
                    collateral_json["added"] = True

            if collateral_json:
                collateral_list.append(collateral_json)

        return collateral_list

    def securities_act_notices_json(self, registration_id):
        """Build securities act notices JSON: current_view_json determines if current or original data is included."""
        notices_list = []
        if not self.registration:
            return notices_list
        for reg in self.registration:
            if not self.current_view_json and reg.id == registration_id and reg.securities_act_notices:
                for notice in reg.securities_act_notices:
                    notices_list.append(notice.json)
                return notices_list
            if self.current_view_json and reg.securities_act_notices:
                for notice in reg.securities_act_notices:
                    notice_json = None
                    if not notice.registration_id_end and (
                        self.verification_reg_id < 1 or self.verification_reg_id >= notice.registration_id
                    ):
                        notice_json = notice.json
                        if self.mark_update_json and notice.registration_id != registration_id:
                            notice_json["added"] = True
                    elif (
                        notice.registration_id_end
                        and self.verification_reg_id > 0
                        and self.verification_reg_id >= notice.registration_id
                        and self.verification_reg_id < notice.registration_id_end
                    ):
                        notice_json = notice.json
                        if self.mark_update_json and notice.registration_id != registration_id:
                            notice_json["added"] = True
                    if notice_json:
                        notices_list.append(notice.json)
        if notices_list and self.current_view_json:  # Current view remove existing amendment notice/order links.
            for notice in notices_list:
                if "amendNoticeId" in notice:
                    del notice["amendNoticeId"]
                if notice.get("securitiesActOrders"):
                    for order in notice.get("securitiesActOrders"):
                        if "amendOrderId" in order:
                            del order["amendOrderId"]
        return notices_list

    def validate_debtor_name(self, debtor_name_json, staff: bool = False):
        """Verify supplied debtor name when registering non-financing statements. Bypass the check for staff.
        Debtor name match rules:
        The debtor name may be for any debtor in the financing statement and may be historical/removed.
        Match on first five characters, or all if less than 5, on the business name or the individual last name.
        """
        if staff:
            return True

        if not debtor_name_json:
            return False

        check_name = None
        if "businessName" in debtor_name_json:
            check_name = debtor_name_json["businessName"].upper()[:5]
        elif "personName" in debtor_name_json and "last" in debtor_name_json["personName"]:
            check_name = debtor_name_json["personName"]["last"].upper()[:5]
        else:
            return False

        if self.parties:
            for party in self.parties:
                if party.party_type == model_utils.PARTY_DEBTOR_BUS and check_name == party.business_name.upper()[:5]:
                    return True
                if party.party_type == model_utils.PARTY_DEBTOR_IND and check_name == party.last_name.upper()[:5]:
                    return True
        return False

    def save(self):
        """Save the object to the database immediately."""
        db.session.add(self)
        db.session.commit()

        # Now save draft
        draft = self.registration[0].draft
        db.session.add(draft)
        db.session.commit()

    @classmethod
    def find_all_by_account_id(cls, account_id):
        """Return a summary list of recent financing statements belonging to an account."""
        results_json = []
        if not account_id:
            return results_json

        max_results_size = int(current_app.config.get("ACCOUNT_REGISTRATIONS_MAX_RESULTS"))
        results = db.session.execute(
            text(model_utils.QUERY_ACCOUNT_FINANCING_STATEMENTS),
            {"query_account": account_id, "max_results_size": max_results_size},
        )
        rows = results.fetchall()
        if rows is not None:
            for row in rows:
                result = {
                    "registrationNumber": str(row[1]),
                    "baseRegistrationNumber": str(row[1]),
                    "createDateTime": model_utils.format_ts(row[2]),
                    "registrationType": str(row[3]),
                    "registrationClass": str(row[4]),
                    "registrationDescription": str(row[5]),
                    "statusType": str(row[7]),
                    "expireDays": int(row[8]),
                    "lastUpdateDateTime": model_utils.format_ts(row[9]),
                    "registeringParty": str(row[10]),
                    "securedParties": str(row[11]),
                    "clientReferenceId": str(row[12]),
                    "path": "/ppr/api/v1/financing-statements/" + str(row[1]),
                }
                results_json.append(result)
        return results_json

    @classmethod
    def find_by_id(cls, financing_id: int = None):
        """Return a financing statement object by financing ID."""
        statement = None
        if financing_id:
            statement = db.session.query(FinancingStatement).filter(FinancingStatement.id == financing_id).one_or_none()

        return statement

    @classmethod
    def find_by_registration_number(
        cls, registration_num: str, account_id: str, staff: bool = False, create: bool = False
    ):
        """Return a financing statement by registration number."""
        statement = None
        if registration_num:
            try:
                statement = (
                    db.session.query(FinancingStatement)
                    .filter(
                        FinancingStatement.id == Registration.financing_id,
                        Registration.registration_num == registration_num,
                        Registration.registration_type_cl.in_(["PPSALIEN", "MISCLIEN", "CROWNLIEN"]),
                    )
                    .one_or_none()
                )
            except Exception as db_exception:  # noqa: B902; return nicer error
                logger.error("DB find_by_registration_number exception: " + repr(db_exception))
                raise DatabaseException(db_exception) from db_exception

        if not statement:
            raise BusinessException(
                error=model_utils.ERR_FINANCING_NOT_FOUND.format(
                    code=ResourceErrorCodes.NOT_FOUND_ERR.value, registration_num=registration_num
                ),
                status_code=HTTPStatus.NOT_FOUND,
            )

        if not staff and account_id and statement.registration[0].account_id != account_id:
            # Check extra registrations
            extra_reg = UserExtraRegistration.find_by_registration_number(
                statement.registration[0].registration_num, account_id
            )
            if not extra_reg:
                raise BusinessException(
                    error=model_utils.ERR_REGISTRATION_ACCOUNT.format(
                        code=ResourceErrorCodes.UNAUTHORIZED_ERR.value,
                        account_id=account_id,
                        registration_num=registration_num,
                    ),
                    status_code=HTTPStatus.UNAUTHORIZED,
                )
        # Skip historical check if staff and not creating
        if staff and not create:
            return statement
        if model_utils.is_historical(statement, create):  # and (not staff or create):
            raise BusinessException(
                error=model_utils.ERR_FINANCING_HISTORICAL.format(
                    code=ResourceErrorCodes.HISTORICAL_ERR.value, registration_num=registration_num
                ),
                status_code=HTTPStatus.BAD_REQUEST,
            )
        return statement

    @classmethod
    def find_by_financing_id(cls, financing_id: int = None):
        """Return a financing statement by financing statement ID."""
        statement = None
        if financing_id:
            statement = (
                db.session.query(FinancingStatement)
                .filter(FinancingStatement.id == Registration.financing_id, FinancingStatement.id == financing_id)
                .one_or_none()
            )

        return statement

    @classmethod
    def find_debtor_names_by_registration_number(cls, registration_num: str = None):
        """Return a list of all debtor names fora base registration number."""
        names_json = []
        if not registration_num:
            return names_json
        statement = None
        try:
            statement = (
                db.session.query(FinancingStatement)
                .filter(
                    FinancingStatement.id == Registration.financing_id,
                    Registration.registration_num == registration_num,
                    Registration.registration_type_cl.in_(["PPSALIEN", "MISCLIEN", "CROWNLIEN"]),
                )
                .one_or_none()
            )
        except Exception as db_exception:  # noqa: B902; return nicer error
            logger.error("DB find_debtor_names_by_registration_number exception: " + repr(db_exception))
            raise DatabaseException(db_exception) from db_exception

        if statement and statement.parties:
            for party in statement.parties:
                if party.party_type == model_utils.PARTY_DEBTOR_BUS:
                    name = {"businessName": party.business_name}
                    names_json.append(name)
                elif party.party_type == model_utils.PARTY_DEBTOR_IND:
                    person_name = {"first": party.first_name, "last": party.last_name}
                    if party.middle_initial and party.middle_initial != "" and party.middle_initial.upper() != "NONE":
                        person_name["middle"] = party.middle_initial
                    name = {"personName": person_name}
                    names_json.append(name)
        return names_json

    @classmethod
    def is_rl_transition(cls, reg: Registration) -> bool:
        """Check if an CL registration type transitioned from RL: commercial lien act timestamp must exist."""
        reg_type: RegistrationType = RegistrationType.find_by_registration_type(RegistrationTypes.CL.value)
        if reg_type and reg_type.act_ts:
            return reg.registration_ts.timestamp() < reg_type.act_ts.timestamp()
        return False

    @staticmethod
    def create_from_json(json_data, account_id: str, user_id: str = None):
        """Create a financing statement object from a json Financing Statement schema object: map json to db."""
        statement = FinancingStatement()
        statement.state_type = model_utils.STATE_ACTIVE

        # Do this early as it also checks the party codes and may throw an exception
        statement.parties = Party.create_from_financing_json(json_data, None)

        reg_type = json_data["type"]
        statement.registration = [Registration.create_financing_from_json(json_data, account_id, user_id)]
        statement.life = statement.registration[0].life
        if reg_type == model_utils.REG_TYPE_REPAIRER_LIEN:
            statement.expire_date = model_utils.expiry_dt_repairer_lien()
        elif statement.life and statement.life != model_utils.LIFE_INFINITE:
            statement.expire_date = model_utils.expiry_dt_from_years(statement.life)

        if reg_type == model_utils.REG_TYPE_OTHER and "otherTypeDescription" in json_data:
            statement.crown_charge_other = json_data["otherTypeDescription"]

        registration_id = statement.registration[0].id
        statement.trust_indenture = TrustIndenture.create_from_json(json_data, registration_id)
        if "vehicleCollateral" in json_data:
            statement.vehicle_collateral = VehicleCollateral.create_from_financing_json(json_data, registration_id)
        if "generalCollateral" in json_data:
            statement.general_collateral = GeneralCollateral.create_from_financing_json(json_data, registration_id)

        for party in statement.parties:
            party.registration_id = registration_id

        return statement
