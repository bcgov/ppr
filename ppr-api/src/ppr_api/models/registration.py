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

from enum import Enum
from http import HTTPStatus
import json

from flask import current_app

from ppr_api.exceptions import BusinessException, DatabaseException, ResourceErrorCodes
from ppr_api.models import utils as model_utils
from ppr_api.services.authz import is_all_staff_account

from .db import db
from .draft import Draft
from .party import Party
from .court_order import CourtOrder
from .general_collateral import GeneralCollateral
from .general_collateral_legacy import GeneralCollateralLegacy
from .type_tables import RegistrationType
from .trust_indenture import TrustIndenture
from .user_extra_registration import UserExtraRegistration
from .vehicle_collateral import VehicleCollateral
# noqa: I003


FINANCING_PATH = '/ppr/api/v1/financing-statements/'


class CrownChargeTypes(str, Enum):
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


class MiscellaneousTypes(str, Enum):
    """Render an Enum of the financing statement miscellaneous registration type class."""

    HC_NOTICE = 'HN'
    MAINTENANCE = 'ML'
    MH_NOTICE = 'MN'
    POC_NOTICE = 'PN'
    WAGES_UNPAID = 'WL'


class PPSATypes(str, Enum):
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


class Registration(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all statement registration information."""

    class RegistrationTypes(str, Enum):
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
    draft_id = db.Column('draft_id', db.Integer, db.ForeignKey('drafts.id'), nullable=False, index=True)
    registration_type = db.Column('registration_type', db.String(2),
                                  db.ForeignKey('registration_types.registration_type'), nullable=False)
    registration_type_cl = db.Column('registration_type_cl', db.String(10),
                                     db.ForeignKey('registration_type_classes.registration_type_cl'), nullable=False)

    # relationships
    financing_statement = db.relationship('FinancingStatement', foreign_keys=[financing_id],
                                          back_populates='registration', cascade='all, delete', uselist=False)
    reg_type = db.relationship('RegistrationType', foreign_keys=[registration_type],
                               back_populates='registration', cascade='all, delete', uselist=False)
    parties = db.relationship('Party', back_populates='registration')
    general_collateral = db.relationship('GeneralCollateral', back_populates='registration')
    general_collateral_legacy = db.relationship('GeneralCollateralLegacy', back_populates='registration')
    vehicle_collateral = db.relationship('VehicleCollateral', back_populates='registration')
    draft = db.relationship('Draft', foreign_keys=[draft_id], uselist=False)
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
        if self.general_collateral_legacy:
            for gen_c in self.general_collateral_legacy:
                if gen_c.registration_id == registration_id and \
                   gen_c.status == GeneralCollateralLegacy.StatusTypes.ADDED:
                    collateral.append(gen_c.json)
        if self.general_collateral:
            for gen_c in self.general_collateral:
                if gen_c.registration_id == registration_id and \
                   gen_c.status == GeneralCollateralLegacy.StatusTypes.ADDED:
                    # collateral_json = gen_c.json
                    # collateral_json['reg_id'] = registration_id  # Need this for report edit badge
                    collateral.append(gen_c.json)
        if collateral:
            json_data['addGeneralCollateral'] = collateral

    def __delete_general_collateral_json(self, json_data, registration_id):
        """Build general collateral deleted as part of the registration."""
        collateral = []
        if self.financing_statement.general_collateral_legacy:
            for gen_c in self.financing_statement.general_collateral_legacy:
                if registration_id == gen_c.registration_id_end or \
                        (registration_id == gen_c.registration_id and
                         gen_c.status == GeneralCollateralLegacy.StatusTypes.DELETED):
                    collateral.append(gen_c.json)
        if self.financing_statement.general_collateral:
            for gen_c in self.financing_statement.general_collateral:
                if registration_id == gen_c.registration_id_end or \
                        (registration_id == gen_c.registration_id and
                         gen_c.status == GeneralCollateralLegacy.StatusTypes.DELETED):
                    # collateral_json = gen_c.json
                    # collateral_json['reg_id'] = registration_id  # Need this for report edit badge
                    collateral.append(gen_c.json)
        if collateral:
            json_data['deleteGeneralCollateral'] = collateral

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
    def find_by_registration_number(cls, registration_num: str,
                                    account_id: str,
                                    staff: bool = False,
                                    base_reg_num: str = None):
        """Return the registration matching the registration number."""
        registration = None
        if registration_num:
            try:
                registration = cls.query.filter(Registration.registration_num == registration_num).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB find_by_registration_number exception: ' + repr(db_exception))
                raise DatabaseException(db_exception)

        if not registration:
            raise BusinessException(
                error=model_utils.ERR_REGISTRATION_NOT_FOUND.format(code=ResourceErrorCodes.NOT_FOUND_ERR,
                                                                    registration_num=registration_num),
                status_code=HTTPStatus.NOT_FOUND
            )

        if not staff and account_id and registration.account_id != account_id:
            # Check extra registrations
            extra_reg = UserExtraRegistration.find_by_registration_number(base_reg_num, account_id)
            if not extra_reg:
                raise BusinessException(
                    error=model_utils.ERR_REGISTRATION_ACCOUNT.format(code=ResourceErrorCodes.UNAUTHORIZED_ERR,
                                                                      account_id=account_id,
                                                                      registration_num=registration_num),
                    status_code=HTTPStatus.UNAUTHORIZED
                )

        if not staff and model_utils.is_historical(registration.financing_statement, False):
            raise BusinessException(
                error=model_utils.ERR_FINANCING_HISTORICAL.format(code=ResourceErrorCodes.HISTORICAL_ERR,
                                                                  registration_num=registration_num),
                status_code=HTTPStatus.BAD_REQUEST
            )

        if not staff and base_reg_num and base_reg_num != registration.base_registration_num:
            raise BusinessException(
                error=model_utils.ERR_REGISTRATION_MISMATCH.format(code=ResourceErrorCodes.DATA_MISMATCH_ERR,
                                                                   registration_num=registration_num,
                                                                   base_reg_num=base_reg_num),
                status_code=HTTPStatus.BAD_REQUEST
            )

        return registration

    @classmethod
    def find_all_by_account_id(  # pylint: disable=too-many-locals
            cls, account_id: str, collapse: bool = False, account_name: str = None):
        """Return a summary list of recent registrations belonging to an account.

        To access a verification statement report, one of the followng conditions must be true:
        1. The request account ID matches the registration account ID.
        2. The request account name matches the registration registering party name.
        3. The request account name matches one of the base registration secured party names.
        """
        results_json = []
        if account_id is None:
            return results_json

        registrations_json = []
        try:
            results = db.session.execute(model_utils.QUERY_ACCOUNT_REGISTRATIONS,
                                         {'query_account': account_id,
                                          'max_results_size': model_utils.get_max_registrations_size()})
            rows = results.fetchall()
            if rows is not None:
                for row in rows:
                    mapping = row._mapping  # pylint: disable=protected-access; follows documentation
                    removed_count = int(mapping['removed_count'])
                    if removed_count < 1:
                        reg_num = str(mapping['registration_number'])
                        base_reg_num = str(mapping['base_reg_number'])
                        registering_name = str(mapping['registering_name'])
                        if not registering_name:
                            registering_name = ''
                        result = {
                            'accountId': str(mapping['account_id']),
                            'registrationNumber': reg_num,
                            'baseRegistrationNumber': base_reg_num,
                            'createDateTime': model_utils.format_ts(mapping['registration_ts']),
                            'registrationType': str(mapping['registration_type']),
                            'registrationDescription': str(mapping['registration_desc']),
                            'registrationClass': str(mapping['registration_type_cl']),
                            'statusType': str(mapping['state']),
                            'expireDays': int(mapping['expire_days']),
                            'lastUpdateDateTime': model_utils.format_ts(mapping['last_update_ts']),
                            'registeringParty': str(mapping['registering_party']),
                            'securedParties': str(mapping['secured_party']),
                            'clientReferenceId': str(mapping['client_reference_id']),
                            'registeringName': registering_name
                        }
                        reg_class = result['registrationClass']
                        if model_utils.is_financing(reg_class):
                            result['baseRegistrationNumber'] = reg_num
                            result['path'] = FINANCING_PATH + reg_num
                        elif reg_class == model_utils.REG_CLASS_DISCHARGE:
                            result['path'] = FINANCING_PATH + base_reg_num + '/discharges/' + reg_num
                        elif reg_class == model_utils.REG_CLASS_RENEWAL:
                            result['path'] = FINANCING_PATH + base_reg_num + '/renewals/' + reg_num
                        elif reg_class == model_utils.REG_CLASS_CHANGE:
                            result['path'] = FINANCING_PATH + base_reg_num + '/changes/' + reg_num
                        elif reg_class in (model_utils.REG_CLASS_AMEND, model_utils.REG_CLASS_AMEND_COURT):
                            result['path'] = FINANCING_PATH + base_reg_num + '/amendments/' + reg_num

                        result = Registration.__update_summary_optional(result, account_id)
                        # Set if user can access verification statement.
                        if not Registration.can_access_report(account_id, account_name, result):
                            result['path'] = ''
                        
                        if 'accountId' in result:
                            del result['accountId']  # Only use this for report access checking.

                        if collapse and not model_utils.is_financing(reg_class):
                            registrations_json.append(result)
                        else:
                            results_json.append(result)
                if collapse:
                    return Registration.__build_account_collapsed_json(results_json, registrations_json)
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB find_all_by_account_id exception: ' + repr(db_exception))
            raise DatabaseException(db_exception)

        return results_json

    @classmethod
    def find_summary_by_reg_num(cls, account_id: str, registration_num: str, account_name: str = None):
        """Return a single registration summary by registration_number."""
        result = {}
        changes = []
        if account_id is None or registration_num is None:
            return result
        try:
            results = db.session.execute(model_utils.QUERY_ACCOUNT_ADD_REGISTRATION,
                                         {'query_account': account_id, 'query_reg_num': registration_num})
            rows = results.fetchall()
            if rows is not None:
                for row in rows:
                    mapping = row._mapping  # pylint: disable=protected-access; follows documentation
                    reg_num = str(mapping['registration_number'])
                    base_reg_num = str(mapping['base_reg_number'])
                    reg_class = str(mapping['registration_type_cl'])
                    result = {
                        'registrationNumber': reg_num,
                        'baseRegistrationNumber': base_reg_num,
                        'createDateTime': model_utils.format_ts(mapping['registration_ts']),
                        'registrationType': str(mapping['registration_type']),
                        'registrationDescription': str(mapping['registration_desc']),
                        'registrationClass': reg_class,
                        'registeringParty': str(mapping['registering_party']),
                        'securedParties': str(mapping['secured_party']),
                        'clientReferenceId': str(mapping['client_reference_id']),
                        'registeringName': str(mapping['registering_name']),
                        'accountId': str(mapping['account_id'])
                    }
                    if model_utils.is_financing(reg_class):
                        result['baseRegistrationNumber'] = reg_num
                        result['path'] = FINANCING_PATH + reg_num
                        result['statusType'] = str(mapping['state'])
                        result['expireDays'] = int(mapping['expire_days'])
                        result['lastUpdateDateTime'] = model_utils.format_ts(mapping['last_update_ts'])
                        result['existsCount'] = int(mapping['exists_count'])
                        # Another account already added.
                        if result['existsCount'] > 0 and result['accountId'] != account_id:
                            result['inUserList'] = True
                        # User account previously removed (can be added back).
                        elif result['existsCount'] > 0 and result['accountId'] == account_id:
                            result['inUserList'] = False
                        # User account added by default.
                        elif result['accountId'] == account_id:
                            result['inUserList'] = True
                        # Another account excluded by default.
                        else:
                            result['inUserList'] = False
                    elif reg_class == model_utils.REG_CLASS_DISCHARGE:
                        result['path'] = FINANCING_PATH + base_reg_num + '/discharges/' + reg_num
                    elif reg_class == model_utils.REG_CLASS_RENEWAL:
                        result['path'] = FINANCING_PATH + base_reg_num + '/renewals/' + reg_num
                    elif reg_class == model_utils.REG_CLASS_CHANGE:
                        result['path'] = FINANCING_PATH + base_reg_num + '/changes/' + reg_num
                    elif reg_class in (model_utils.REG_CLASS_AMEND, model_utils.REG_CLASS_AMEND_COURT):
                        result['path'] = FINANCING_PATH + base_reg_num + '/amendments/' + reg_num
                    # Set if user can access verification statement.\
                    if not Registration.can_access_report(account_id, account_name, result):
                        result['path'] = ''
                    result = Registration.__update_summary_optional(result, account_id)
                    if not model_utils.is_financing(reg_class):
                        changes.append(result)
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB find_summary_by_reg_num exception: ' + repr(db_exception))
            raise DatabaseException(db_exception)

        if not result:
            return None
        if result and changes:
            result['changes'] = changes
        return result

    @staticmethod
    def can_access_report(account_id: str, account_name: str, reg_json) -> bool:
        """Determine if request account can view the registration verification statement."""
        # All staff roles can see any verification statement.
        reg_account_id = reg_json['accountId']
        if is_all_staff_account(account_id):
            return True
        if account_id == reg_account_id:
            return True
        if account_name:
            if reg_json['registeringParty'] == account_name:
                return True
            sp_names = reg_json['securedParties']
            if sp_names and account_name in sp_names:
                return True
        return False

    @staticmethod
    def __update_summary_optional(reg_json, account_id: str):
        """Single summary result replace optional property 'None' with ''."""
        if not reg_json['registeringName'] or reg_json['registeringName'].lower() == 'none':
            reg_json['registeringName'] = ''
        # Only staff role or matching account includes registeringName
        elif not is_all_staff_account(account_id) and 'accountId' in reg_json and account_id != reg_json['accountId']:
            reg_json['registeringName'] = ''

        if not reg_json['clientReferenceId'] or reg_json['clientReferenceId'].lower() == 'none':
            reg_json['clientReferenceId'] = ''
        return reg_json

    @staticmethod
    def __build_account_collapsed_json(financing_json, registrations_json):
        """Organize account registrations as parent/child financing statement/change registrations."""
        for statement in financing_json:
            changes = []
            for registration in registrations_json:
                if statement['registrationNumber'] == registration['baseRegistrationNumber']:
                    changes.append(registration)
            if changes:
                statement['changes'] = changes
        return financing_json

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
    def create_from_json(json_data,
                         registration_type_cl: str,
                         financing_statement,
                         base_registration_num: str,
                         account_id: str = None):
        """Create a registration object for an existing financing statement from dict/json."""
        # Create or update draft.
        draft = Registration.find_draft(json_data, None, None)
        reg_vals = Registration.get_generated_values(draft)
        registration = Registration()
        registration.id = reg_vals.id  # pylint: disable=invalid-name; allow name of id.
        registration.registration_num = reg_vals.registration_num
        registration.registration_ts = model_utils.now_ts()
        registration.financing_id = financing_statement.id
        registration.financing_statement = financing_statement
        registration.account_id = account_id
        if not draft:
            registration.document_number = reg_vals.document_number
            draft = Draft.create_from_registration(registration, json_data)
        registration.draft = draft
        registration.registration_type_cl = registration_type_cl
        if registration_type_cl in (model_utils.REG_CLASS_AMEND,
                                    model_utils.REG_CLASS_AMEND_COURT):
            json_data = model_utils.cleanup_amendment(json_data)
            registration.registration_type = model_utils.amendment_change_type(json_data)
            if registration.registration_type == model_utils.REG_TYPE_AMEND_COURT:
                registration.registration_type_cl = model_utils.REG_CLASS_AMEND_COURT
            if 'description' in json_data:
                registration.detail_description = json_data['description']
        elif registration_type_cl == model_utils.REG_CLASS_CHANGE:
            registration.registration_type = json_data['changeType']
        elif registration_type_cl == model_utils.REG_CLASS_RENEWAL:
            registration.registration_type = model_utils.REG_TYPE_RENEWAL
        elif registration_type_cl == model_utils.REG_CLASS_DISCHARGE:
            registration.registration_type = model_utils.REG_TYPE_DISCHARGE

        registration.base_registration_num = base_registration_num
        registration.ver_bypassed = 'Y'
        registration.draft.registration_type = registration.registration_type
        registration.draft.registration_type_cl = registration.registration_type_cl

        if 'clientReferenceId' in json_data:
            registration.client_reference_id = json_data['clientReferenceId']

        # All registrations have at least one party (registering).
        registration.parties = Party.create_from_statement_json(json_data,
                                                                registration_type_cl,
                                                                registration.financing_id)

        # If get to here all data should be valid: get reg id to close out updated entities.
        registration_id = registration.id
        financing_reg_type = registration.financing_statement.registration[0].registration_type
        if registration_type_cl == model_utils.REG_CLASS_DISCHARGE:
            registration.financing_statement.state_type = model_utils.STATE_DISCHARGED
            registration.financing_statement.discharged = 'Y'
        elif registration_type_cl == model_utils.REG_CLASS_RENEWAL:
            if financing_reg_type == model_utils.REG_TYPE_REPAIRER_LIEN:
                registration.life = model_utils.REPAIRER_LIEN_YEARS
                # Adding 180 days to existing expiry.
                registration.financing_statement.expire_date = \
                    model_utils.expiry_dt_repairer_lien(registration.financing_statement.expire_date)
            else:
                if 'lifeInfinite' in json_data and json_data['lifeInfinite']:
                    registration.life = model_utils.LIFE_INFINITE
                    registration.financing_statement.expire_date = None
                if 'lifeYears' in json_data:
                    registration.life = json_data['lifeYears']
                    # registration.financing_statement.expire_date = model_utils.expiry_dt_from_years(registration.life)
                    # Replace above line with below: adding years to the existing expiry
                    registration.financing_statement.expire_date = \
                        model_utils.expiry_dt_add_years(registration.financing_statement.expire_date, registration.life)
                elif 'expiryDate' in json_data:
                    new_expiry_date = model_utils.expiry_ts_from_iso_format(json_data['expiryDate'])
                    registration.life = new_expiry_date.year - registration.financing_statement.expire_date.year
                    registration.financing_statement.expire_date = new_expiry_date

                # Verify this is updated.
                if 'lifeInfinite' in json_data and json_data['lifeInfinite']:
                    registration.financing_statement.life = registration.life
                else:
                    registration.financing_statement.life += registration.life

        # Repairer's lien renewal or amendment can have court order information.
        if (registration.registration_type == model_utils.REG_TYPE_AMEND_COURT or
                registration.registration_type == model_utils.REG_TYPE_RENEWAL) and \
                'courtOrderInformation' in json_data:
            registration.court_order = CourtOrder.create_from_json(json_data['courtOrderInformation'],
                                                                   registration_id)

        if registration_type_cl in (model_utils.REG_CLASS_AMEND,
                                    model_utils.REG_CLASS_AMEND_COURT,
                                    model_utils.REG_CLASS_CHANGE):
            # Possibly add vehicle collateral
            registration.vehicle_collateral = VehicleCollateral.create_from_statement_json(json_data,
                                                                                           registration_id,
                                                                                           registration.financing_id)
            # Possibly add general collateral
            registration.general_collateral = GeneralCollateral.create_from_statement_json(json_data,
                                                                                           registration_id,
                                                                                           registration.financing_id)
            # Possibly add/remove a trust indenture
            if ('addTrustIndenture' in json_data and json_data['addTrustIndenture']) or \
                    ('removeTrustIndenture' in json_data and json_data['removeTrustIndenture']):
                registration.trust_indenture = TrustIndenture.create_from_amendment_json(registration.financing_id,
                                                                                         registration.id)
                if 'removeTrustIndenture' in json_data and json_data['removeTrustIndenture']:
                    registration.trust_indenture.trust_indenture = TrustIndenture.TRUST_INDENTURE_NO
            # Close out deleted parties and collateral, and trust indenture.
            Registration.delete_from_json(json_data, registration, financing_statement)

        return registration

    @staticmethod
    def create_financing_from_json(json_data, account_id: str = None, user_id: str = None):
        """Create a registraion object from dict/json."""
        registration = Registration()
        registration.account_id = account_id
        registration.user_id = user_id
        registration.registration_ts = model_utils.now_ts()
        reg_type = json_data['type']
        registration.registration_type_cl = model_utils.REG_TYPE_TO_REG_CLASS[reg_type]
        registration.registration_type = reg_type
        registration.ver_bypassed = 'Y'

        if reg_type == model_utils.REG_TYPE_REPAIRER_LIEN:
            if 'lienAmount' in json_data:
                registration.lien_value = json_data['lienAmount'].strip()
            if 'surrenderDate' in json_data:
                registration.surrender_date = model_utils.ts_from_date_iso_format(json_data['surrenderDate'])
            registration.life = model_utils.REPAIRER_LIEN_YEARS
        elif 'lifeInfinite' in json_data and json_data['lifeInfinite']:
            registration.life = model_utils.LIFE_INFINITE
        elif registration.registration_type_cl in (model_utils.REG_CLASS_CROWN, model_utils.REG_CLASS_MISC):
            registration.life = model_utils.LIFE_INFINITE
        elif reg_type in (model_utils.REG_TYPE_MARRIAGE_SEPARATION,
                          model_utils.REG_TYPE_TAX_MH,
                          model_utils.REG_TYPE_LAND_TAX_MH):
            registration.life = model_utils.LIFE_INFINITE
        elif 'lifeYears' in json_data:
            registration.life = json_data['lifeYears']

        if 'clientReferenceId' in json_data:
            registration.client_reference_id = json_data['clientReferenceId']

        # Create or update draft.
        draft = Registration.find_draft(json_data, registration.registration_type_cl, reg_type)
        reg_vals = Registration.get_generated_values(draft)
        registration.id = reg_vals.id
        registration.registration_num = reg_vals.registration_num
        if not draft:
            registration.document_number = reg_vals.document_number
            draft = Draft.create_from_registration(registration, json_data, user_id)
        registration.draft = draft

        return registration

    @staticmethod
    def delete_from_json(json_data, registration, financing_statement):
        """For deleted parties and collateral in registrations set registration_id_end from dict/json."""
        if 'deleteDebtors' in json_data and json_data['deleteDebtors']:
            for party in json_data['deleteDebtors']:
                existing = Registration.find_party_by_id(party['partyId'],
                                                         model_utils.PARTY_DEBTOR_BUS,
                                                         financing_statement.parties)
                if existing:
                    existing.registration_id_end = registration.id

        if 'deleteSecuredParties' in json_data and json_data['deleteSecuredParties']:
            for party in json_data['deleteSecuredParties']:
                existing = Registration.find_party_by_id(party['partyId'],
                                                         model_utils.PARTY_SECURED,
                                                         financing_statement.parties)
                if existing:
                    existing.registration_id_end = registration.id

        # In "add only" general collateral solution gc records are never logically deleted.
        # if 'deleteGeneralCollateral' in json_data and json_data['deleteGeneralCollateral']:
        #    for gen_c in json_data['deleteGeneralCollateral']:
        #        collateral = Registration.find_general_collateral_by_id(gen_c['collateralId'],
        #                                                                financing_statement.general_collateral)
        #        if collateral:
        #            collateral.registration_id_end = registration.id

        if 'deleteVehicleCollateral' in json_data and json_data['deleteVehicleCollateral']:
            for vehicle_c in json_data['deleteVehicleCollateral']:
                collateral = Registration.find_vehicle_collateral_by_id(vehicle_c['vehicleId'],
                                                                        financing_statement.vehicle_collateral)
                if collateral:
                    collateral.registration_id_end = registration.id

        if 'removeTrustIndenture' in json_data and json_data['removeTrustIndenture'] and \
                financing_statement.trust_indenture:
            for trust_indenture in financing_statement.trust_indenture:
                if trust_indenture.registration_id != registration.id and not trust_indenture.registration_id_end:
                    trust_indenture.registration_id_end = registration.id
        # Could be transitioning with removed with a record to added: close out removed record.
        elif 'addTrustIndenture' in json_data and json_data['addTrustIndenture'] and \
                financing_statement.trust_indenture:
            for trust_indenture in financing_statement.trust_indenture:
                if trust_indenture.registration_id != registration.id and not trust_indenture.registration_id_end:
                    trust_indenture.registration_id_end = registration.id

    @staticmethod
    def find_draft(json_data, registration_class: str, registration_type: str):
        """Try to find an existing draft if a documentId is in json_data.).

        Return None if not found or no documentId.
        """
        draft = None

        if 'documentId' in json_data:
            try:
                doc_id = json_data['documentId'].strip()
                if doc_id != '':
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

        result = db.session.execute(query)
        row = result.first()
        registration.id = int(row._mapping['reg_id'])  # pylint: disable=protected-access; follows documentation
        registration.registration_num = str(row._mapping['reg_num'])  # pylint: disable=protected-access
        if not draft:
            registration.document_number = str(row._mapping['doc_num'])  # pylint: disable=protected-access

        return registration

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
        """Search parties for a party former name."""
        former_name = ''
        for party in self.financing_statement.parties:
            if new_party.party_type == party.party_type and new_party.registration_id == party.registration_id_end:
                if party.client_code and party.client_code.name:
                    former_name = party.client_code.name
                elif party.business_name:
                    former_name = party.business_name
                else:
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
                expiry_ts = model_utils.expiry_dt_repairer_lien(registration.registration_ts)

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
