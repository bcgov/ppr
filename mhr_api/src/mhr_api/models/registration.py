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

from http import HTTPStatus

from flask import current_app

from mhr_api.exceptions import BusinessException, DatabaseException, ResourceErrorCodes
from mhr_api.models import utils as model_utils
from mhr_api.utils.base import BaseEnum

from .db import db
# from .court_order import CourtOrder
from .general_collateral import GeneralCollateral
from .party import Party
from .type_tables import RegistrationType


class CrownChargeTypes(BaseEnum):
    """Render an Enum of the financing statement crown charge registration type class."""

    CORP_TAX = 'CC'
    CARBON_TAX = 'CT'
    CONSUMPTION_TAX = 'DP'
    EXCISE_TAX = 'ET'
    FOREST_TAX = 'FO'
    MOTOR_FUEL_TAX = 'FT'
    HOTEL_TAX = 'HR'
    INSURANCE_TAX = 'IP'
    INCOME_TAX = 'IT'
    LOGGING_TAX = 'LO'
    MINERAL_LAND_TAX = 'MD'
    MINING_TAX = 'MI'
    MINERAL_TAX = 'MR'
    OTHER = 'OT'
    PETROLEUM_TAX = 'PG'
    PROV_SALES_TAX = 'PS'
    PROPERTY_TRANSFER_TAX = 'PT'
    RURAL_TAX = 'RA'
    SCHOOL_ACT = 'SC'
    SOCIAL_TAX = 'SS'
    TAX_LIEN = 'TL'


class MiscellaneousTypes(BaseEnum):
    """Render an Enum of the financing statement miscellaneous registration type class."""

    HC_NOTICE = 'HN'
    MAINTENANCE = 'ML'
    MH_NOTICE = 'MN'
    POC_NOTICE = 'PN'
    WAGES_UNPAID = 'WL'


class PPSATypes(BaseEnum):
    """Render an Enum of the financing statement PPSA lien registration type class."""

    FORESTRY_CHARGE = 'FA'
    FORESTRY_LIEN = 'FL'
    MARRIAGE_SEPARATION = 'FR'
    FORESTRY_SUB_CHARGE = 'FS'
    LAND_TAX = 'LT'
    MH_LIEN = 'MH'
    REPAIRER_LIEN = 'RL'
    SECURITY_AGREEMENT = 'SA'
    SALE_GOODS = 'SG'


class Registration(db.Model):  # pylint: disable=too-many-instance-attributes, too-many-public-methods
    """This class manages all statement registration information."""

    class RegistrationTypes(BaseEnum):
        """Render an Enum of the registration types."""

        REG_CLASS_AMEND = 'AMENDMENT'
        REG_CLASS_AMEND_COURT = 'COURTORDER'
        REG_CLASS_CHANGE = 'CHANGE'
        REG_CLASS_FINANCING = 'PPSALIEN'
        REG_CLASS_DISCHARGE = 'DISCHARGE'
        REG_CLASS_RENEWAL = 'RENEWAL'

    __tablename__ = 'registrations'

    # Always use get_generated_values() to generate PK.
    id = db.Column('id', db.Integer, primary_key=True)
    registration_ts = db.Column('registration_ts', db.DateTime, nullable=False, index=True)
    registration_num = db.Column('registration_number', db.String(10), nullable=False, index=True,
                                 default=db.func.get_registration_num())
    base_registration_num = db.Column('base_reg_number', db.String(10), nullable=True, index=True)
    account_id = db.Column('account_id', db.String(20), nullable=True, index=True)
    client_reference_id = db.Column('client_reference_id', db.String(50), nullable=True)
    life = db.Column('life', db.Integer, nullable=True)
    lien_value = db.Column('lien_value', db.String(15), nullable=True)
    surrender_date = db.Column('surrender_date', db.DateTime, nullable=True)
    ver_bypassed = db.Column('ver_bypassed', db.String(1), nullable=True)
    pay_invoice_id = db.Column('pay_invoice_id', db.Integer, nullable=True)
    pay_path = db.Column('pay_path', db.String(256), nullable=True)

    user_id = db.Column('user_id', db.String(1000), nullable=True)
    detail_description = db.Column('detail_description', db.String(4000), nullable=True)

    # parent keys
    financing_id = db.Column('financing_id', db.Integer,
                             db.ForeignKey('financing_statements.id'), nullable=False, index=True)
    registration_type = db.Column('registration_type', db.String(2),
                                  db.ForeignKey('registration_types.registration_type'), nullable=False)
    registration_type_cl = db.Column('registration_type_cl', db.String(10),
                                     db.ForeignKey('registration_type_classes.registration_type_cl'), nullable=False)

    # relationships
    financing_statement = db.relationship('FinancingStatement', foreign_keys=[financing_id],
                                          back_populates='registration', cascade='all, delete', uselist=False)
    reg_type = db.relationship('RegistrationType', foreign_keys=[registration_type],
                               back_populates='registration', cascade='all, delete', uselist=False)
    parties = db.relationship('Party', order_by='asc(Party.id)', back_populates='registration')
    general_collateral = db.relationship('GeneralCollateral', back_populates='registration')
    vehicle_collateral = db.relationship('VehicleCollateral', back_populates='registration')
    trust_indenture = db.relationship('TrustIndenture', back_populates='registration', uselist=False)
    court_order = db.relationship('CourtOrder', back_populates='registration', uselist=False)

    document_number: str = None

    @property
    def json(self) -> dict:
        """Return the registration as a json object."""
        registration = {
            'baseRegistrationNumber': self.base_registration_num,
            'createDateTime': model_utils.format_ts(self.registration_ts)
        }
        if self.registration_type == model_utils.REG_TYPE_DISCHARGE:
            registration['dischargeRegistrationNumber'] = self.registration_num
        elif self.registration_type == model_utils.REG_TYPE_RENEWAL:
            registration['renewalRegistrationNumber'] = self.registration_num
        elif self.registration_type_cl in (model_utils.REG_CLASS_AMEND, model_utils.REG_CLASS_AMEND_COURT):
            registration['amendmentRegistrationNumber'] = self.registration_num
            if self.detail_description:
                registration['description'] = self.detail_description
            if self.financing_statement.trust_indenture:
                for trust_indenture in self.financing_statement.trust_indenture:
                    if self.id == trust_indenture.registration_id:
                        registration['addTrustIndenture'] = True
                    elif self.id == trust_indenture.registration_id_end:
                        registration['removeTrustIndenture'] = True
        else:
            registration['changeRegistrationNumber'] = self.registration_num

#        if self.draft and self.registration_type != model_utils.REG_TYPE_DISCHARGE and \
#               self.registration_type != model_utils.REG_TYPE_RENEWAL:
#            registration['documentId'] = self.draft.document_number

        if self.is_change():
            registration['changeType'] = self.registration_type

        if self.client_reference_id:
            registration['clientReferenceId'] = self.client_reference_id

        registration_id = self.id
        if self.parties:
            for party in self.parties:
                if party.party_type == model_utils.PARTY_REGISTERING and \
                        party.registration_id == registration_id:
                    registration['registeringParty'] = party.json

        if self.registration_type == model_utils.REG_TYPE_RENEWAL and self.life is not None:
            if self.life != model_utils.LIFE_INFINITE:
                registration['lifeYears'] = self.life
            if self.life == model_utils.REPAIRER_LIEN_YEARS or \
               self.financing_statement.registration[0].registration_type == model_utils.REG_TYPE_REPAIRER_LIEN:
                # Computed expiry date is cumulatative: original 180 days + sum of renewals up to this one.
                registration['expiryDate'] = self.__get_renewal_rl_expiry()
            else:
                registration['expiryDate'] = self.__get_renewal_expiry()

        if self.court_order:
            registration['courtOrderInformation'] = self.court_order.json

        # add debtors, secured parties
        if self.parties and self.is_change():
            secured = []
            debtors = []
            for party in self.parties:
                if party.party_type in (model_utils.PARTY_DEBTOR_BUS, model_utils.PARTY_DEBTOR_IND) and \
                        party.registration_id == registration_id:
                    party_json = party.json
                    party_json['reg_id'] = party.registration_id
                    party_json['former_name'] = self.get_former_party_name(party)
                    debtors.append(party_json)
                elif party.party_type == model_utils.PARTY_SECURED and party.registration_id == registration_id:
                    party_json = party.json
                    party_json['reg_id'] = party.registration_id
                    party_json['former_name'] = self.get_former_party_name(party)
                    secured.append(party_json)

            if debtors:
                registration['addDebtors'] = debtors
            if secured:
                registration['addSecuredParties'] = secured

        # delete debtors, secured parties
        if self.financing_statement.parties and self.is_change():
            secured = []
            debtors = []
            for party in self.financing_statement.parties:
                if party.party_type in (model_utils.PARTY_DEBTOR_BUS, model_utils.PARTY_DEBTOR_IND) and \
                        party.registration_id_end == registration_id:
                    party_json = party.json
                    party_json['reg_id'] = party.registration_id_end
                    debtors.append(party_json)
                elif party.party_type == model_utils.PARTY_SECURED and party.registration_id_end == registration_id:
                    party_json = party.json
                    party_json['reg_id'] = party.registration_id_end
                    secured.append(party_json)

            if debtors:
                registration['deleteDebtors'] = debtors
            if secured:
                registration['deleteSecuredParties'] = secured

        # general collateral including legacy
        if self.is_change():
            self.__add_general_collateral_json(registration, registration_id)
            self.__delete_general_collateral_json(registration, registration_id)

        # add vehicle collateral
        if self.vehicle_collateral and self.is_change():
            collateral = []
            for vehicle_c in self.vehicle_collateral:
                if vehicle_c.registration_id == registration_id:
                    collateral_json = vehicle_c.json
                    collateral_json['reg_id'] = registration_id
                    collateral.append(collateral_json)
            if collateral:
                registration['addVehicleCollateral'] = collateral

        # delete vehicle collateral
        if self.financing_statement.vehicle_collateral and self.is_change():
            collateral = []
            for vehicle_c in self.financing_statement.vehicle_collateral:
                if vehicle_c.registration_id_end == registration_id:
                    collateral_json = vehicle_c.json
                    collateral_json['reg_id'] = registration_id
                    collateral.append(collateral_json)
            if collateral:
                registration['deleteVehicleCollateral'] = collateral

        return self.__set_payment_json(registration)

    def __set_payment_json(self, registration):
        """Add registration payment info json if payment exists."""
        if self.pay_invoice_id and self.pay_path:
            payment = {
                'invoiceId': str(self.pay_invoice_id),
                'receipt': self.pay_path
            }
            registration['payment'] = payment
        return registration

    def __add_general_collateral_json(self, json_data, registration_id):
        """Build general collateral added as part of the registration."""
        collateral = []
        if self.general_collateral:
            for gen_c in self.general_collateral:
                if gen_c.registration_id == registration_id and \
                   gen_c.status == GeneralCollateral.StatusTypes.ADDED:
                    # collateral_json = gen_c.json
                    # collateral_json['reg_id'] = registration_id  # Need this for report edit badge
                    collateral.append(gen_c.json)
        if collateral:
            json_data['addGeneralCollateral'] = collateral

    def __delete_general_collateral_json(self, json_data, registration_id):
        """Build general collateral deleted as part of the registration."""
        collateral = []
        if self.financing_statement.general_collateral:
            for gen_c in self.financing_statement.general_collateral:
                if registration_id == gen_c.registration_id_end or \
                        (registration_id == gen_c.registration_id and
                         gen_c.status == GeneralCollateral.StatusTypes.DELETED):
                    # collateral_json = gen_c.json
                    # collateral_json['reg_id'] = registration_id  # Need this for report edit badge
                    collateral.append(gen_c.json)
        if collateral:
            json_data['deleteGeneralCollateral'] = collateral

    def get_registration_type(self):
        """Lookup registration type record if it has not already been fetched."""
        if self.reg_type is None and self.registration_type:
            self.reg_type = db.session.query(RegistrationType).\
                            filter(RegistrationType.registration_type == self.registration_type).\
                            one_or_none()

    def is_financing(self):
        """Check if the registration is a financing registration for some conditions."""
        return self.registration_type_cl and \
            self.registration_type_cl in (model_utils.REG_CLASS_CROWN,
                                          model_utils.REG_CLASS_MISC,
                                          model_utils.REG_CLASS_PPSA)

    def is_change(self):
        """Check if the registration is a change or amendment for some conditions."""
        return self.registration_type_cl and \
            self.registration_type_cl in (model_utils.REG_CLASS_AMEND,
                                          model_utils.REG_CLASS_AMEND_COURT,
                                          model_utils.REG_CLASS_CHANGE)

    @classmethod
    def find_by_id(cls, registration_id: int):
        """Return the registration matching the id."""
        registration = None
        if registration_id:
            registration = cls.query.get(registration_id)
        return registration

    @classmethod
    def find_by_registration_number(cls, registration_num: str, account_id: str):
        """Return the registration matching the registration number."""
        current_app.logger.debug(f'Account={account_id}, reg_num={registration_num}')
        registration = None
        if registration_num:
            try:
                registration = cls.query.filter(Registration.registration_num == registration_num).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB find_by_registration_number exception: ' + str(db_exception))
                raise DatabaseException(db_exception)

        if not registration:
            raise BusinessException(
                error=model_utils.ERR_REGISTRATION_NOT_FOUND.format(code=ResourceErrorCodes.NOT_FOUND_ERR,
                                                                    registration_num=registration_num),
                status_code=HTTPStatus.NOT_FOUND
            )

        return registration

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
    def find_party_by_id(party_id: int, party_type: str, parties):
        """Search existing list of party objects for a matching party id and type."""
        party = None

        if party_id and party_type and parties:
            for eval_party in parties:
                if eval_party.id == party_id and party_type == eval_party.party_type and \
                        not eval_party.registration_id_end:
                    party = eval_party
                elif eval_party.id == party_id and party_type == model_utils.PARTY_DEBTOR_BUS and \
                        eval_party.party_type == model_utils.PARTY_DEBTOR_IND and \
                        not eval_party.registration_id_end:
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
        former_name = ''
        for party in self.financing_statement.parties:
            if new_party.party_type == party.party_type and new_party.registration_id == party.registration_id_end:
                address1 = party.address
                address2 = new_party.address
                if address1 is None and party.client_code:
                    address1 = party.client_code.address
                if address2 is None and new_party.client_code:
                    address2 = new_party.client_code.address
                if address1 and address2 and address1.json == address2.json:
                    if party.client_code and party.client_code.name:
                        former_name = party.client_code.name
                    elif party.business_name:
                        former_name = party.business_name
                    else:
                        # match if only 1 name is different in addition to same address.
                        former_name = Registration.__get_matching_party_name(new_party, party)
                    if former_name:
                        return former_name
        return former_name

    @staticmethod
    def __get_matching_party_name(new_party: Party, party: Party):
        """Match name only if one name part has changed (addresses already match."""
        former_name: str = ''
        found: bool = False
        if new_party.last_name == party.last_name and new_party.first_name != party.first_name:
            found = True
        elif new_party.last_name != party.last_name and new_party.first_name == party.first_name:
            found = True
        elif new_party.last_name == party.last_name and new_party.first_name == party.first_name:
            if (new_party.middle_initial is None and party.middle_initial is not None) or \
                    (new_party.middle_initial is not None and party.middle_initial is None) or \
                    (new_party.middle_initial != party.middle_initial):
                found = True
        if found:
            former_name = party.last_name + ', ' + party.first_name
            if party.middle_initial:
                former_name += ' ' + party.middle_initial
        return former_name

    def __get_renewal_rl_expiry(self):
        """Build a repairer's lien expiry date as the sum of previous registrations."""
        expiry_ts = None
        for registration in self.financing_statement.registration:
            if registration.registration_type_cl in (model_utils.REG_CLASS_CROWN, model_utils.REG_CLASS_MISC,
                                                     model_utils.REG_CLASS_PPSA):
                expiry_ts = model_utils.expiry_dt_from_registration(registration.registration_ts, None)

        for registration in self.financing_statement.registration:
            if registration.registration_type == model_utils.REG_TYPE_RENEWAL and registration.id <= self.id:
                expiry_ts = model_utils.expiry_dt_repairer_lien(expiry_ts)
        return model_utils.format_ts(expiry_ts)

    def __get_renewal_expiry(self):
        """Build a non-repairer's lien expiry date as the sum of previous registrations."""
        if self.life == model_utils.LIFE_INFINITE:
            return 'Never'

        expiry_ts = None
        for registration in self.financing_statement.registration:
            if registration.registration_type_cl in (model_utils.REG_CLASS_CROWN, model_utils.REG_CLASS_MISC,
                                                     model_utils.REG_CLASS_PPSA):
                expiry_ts = model_utils.expiry_dt_from_registration(registration.registration_ts,
                                                                    registration.life)
        for registration in self.financing_statement.registration:
            if registration.registration_type == model_utils.REG_TYPE_RENEWAL and registration.id <= self.id:
                expiry_ts = model_utils.expiry_dt_add_years(expiry_ts, registration.life)
        return model_utils.format_ts(expiry_ts)
