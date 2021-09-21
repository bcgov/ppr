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
# pylint: disable=too-many-statements, too-many-branches

from __future__ import annotations

from enum import Enum
from http import HTTPStatus

from flask import current_app

from ppr_api.exceptions import BusinessException
from ppr_api.models import utils as model_utils

from .db import db
from .registration import Registration  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
from .trust_indenture import TrustIndenture  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
from .party import Party  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
from .general_collateral import GeneralCollateral  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
from .general_collateral_legacy import GeneralCollateralLegacy  # noqa: F401 pylint: disable=unused-import; see above
from .vehicle_collateral import VehicleCollateral  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship


class FinancingStatement(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class maintains financing statement information."""

    class FinancingTypes(Enum):
        """Render an Enum of the financing statement types."""

        SECURITY_AGREEMENT = 'SA'
        SALE_OF_GOODS = 'SG'
        REPAIRERS_LIEN = 'RL'
        MARRIAGE_MH = 'FR'
        LAND_TAX_LIEN = 'LT'
        MANUFACTURED_HOME_LIEN = 'MH'
        FORESTRY_CONTRACTOR_LIEN = 'FL'
        FORESTRY_CONTRACTOR_CHARGE = 'FA'
        FORESTRY_SUBCONTRACTOR_LIEN = 'FS'
        MISCELLANEOUS = 'MR'

    __tablename__ = 'financing_statements'

    id = db.Column('id', db.Integer, db.Sequence('financing_id_seq'), primary_key=True)
    state_type = db.Column('state_type', db.String(3), db.ForeignKey('state_types.state_type'), nullable=False)
    life = db.Column('life', db.Integer, nullable=True)
    expire_date = db.Column('expire_date', db.DateTime, nullable=True)
    discharged = db.Column('discharged', db.String(1), nullable=True)
    renewed = db.Column('renewed', db.String(1), nullable=True)

    type_claim = db.Column('type_claim', db.String(2), nullable=True)
    crown_charge_type = db.Column('crown_charge_type', db.String(2), nullable=True)
    crown_charge_other = db.Column('crown_charge_other', db.String(70), nullable=True)

    # Parent keys

    # Relationships
    registration = db.relationship('Registration', order_by='asc(Registration.registration_ts)',
                                   back_populates='financing_statement')
    parties = db.relationship('Party', order_by='asc(Party.id)', back_populates='financing_statement')
    vehicle_collateral = db.relationship('VehicleCollateral',
                                         order_by='asc(VehicleCollateral.id)',
                                         back_populates='financing_statement')
    general_collateral = db.relationship('GeneralCollateral',
                                         order_by='asc(GeneralCollateral.id)',
                                         back_populates='financing_statement')
    general_collateral_legacy = db.relationship('GeneralCollateralLegacy',
                                                order_by='asc(GeneralCollateralLegacy.id)',
                                                back_populates='financing_statement')
    trust_indenture = db.relationship('TrustIndenture', back_populates='financing_statement')
    previous_statement = db.relationship('PreviousFinancingStatement', back_populates='financing_statement')
    # Relationships - StateType
    fin_state_type = db.relationship('StateType', foreign_keys=[state_type],
                                     back_populates='financing_statement', cascade='all, delete', uselist=False)

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
        statement = {
            'statusType': self.state_type
        }
        if self.state_type == model_utils.STATE_DISCHARGED:
            index = len(self.registration) - 1
            statement['dischargedDateTime'] = model_utils.format_ts(self.registration[index].registration_ts)

        if self.registration and self.registration[0]:
            reg = self.registration[0]
            registration_id = reg.id
            statement['type'] = reg.registration_type
            statement['baseRegistrationNumber'] = reg.registration_num
            if reg.registration_type:
                statement['registrationDescription'] = reg.reg_type.registration_desc
                statement['registrationAct'] = reg.reg_type.registration_act
                if reg.registration_type == model_utils.REG_TYPE_OTHER and self.crown_charge_other:
                    statement['otherTypeDescription'] = self.crown_charge_other

            statement['createDateTime'] = model_utils.format_ts(reg.registration_ts)

            if reg.client_reference_id:
                statement['clientReferenceId'] = reg.client_reference_id

#            if reg.document_number:
#                statement['documentId'] = reg.document_number

            statement['registeringParty'] = self.party_json(Party.PartyTypes.REGISTERING_PARTY.value, registration_id)
            statement['securedParties'] = self.party_json(Party.PartyTypes.SECURED_PARTY.value, registration_id)
            statement['debtors'] = self.party_json(Party.PartyTypes.DEBTOR_COMPANY.value, registration_id)

            general_collateral = self.general_collateral_json(registration_id)
            if general_collateral:
                statement['generalCollateral'] = general_collateral

            vehicle_collateral = self.vehicle_collateral_json(registration_id)
            if vehicle_collateral:
                statement['vehicleCollateral'] = vehicle_collateral

            if reg.registration_type == model_utils.REG_TYPE_REPAIRER_LIEN:
                if reg.lien_value:
                    statement['lienAmount'] = reg.lien_value
                if reg.surrender_date:
                    statement['surrenderDate'] = model_utils.format_ts(reg.surrender_date)

        if self.trust_indenture:
            for trust in self.trust_indenture:
                if not trust.registration_id_end:
                    if trust.trust_indenture == 'Y':
                        statement['trustIndenture'] = True
                    else:
                        statement['trustIndenture'] = False
        else:
            statement['trustIndenture'] = False

        if self.life and self.life == model_utils.LIFE_INFINITE:
            statement['lifeInfinite'] = True
        elif self.life:
            statement['lifeYears'] = self.life

        if self.expire_date:
            statement['expiryDate'] = model_utils.format_ts(self.expire_date)

        self.set_court_order_json(statement)
        self.set_payment_json(statement)
        return self.set_changes_json(statement)

    def set_court_order_json(self, statement):
        """Add court order info to the statement json if generating the current view and court order info exists."""
        if self.current_view_json:
            for registration in self.registration:
                if registration.court_order:
                    statement['courtOrderInformation'] = registration.court_order.json

    def set_changes_json(self, statement):
        """Add history of changes in reverse chronological order to financing statement json."""
        if self.include_changes_json and self.registration and len(self.registration) > 1:
            changes = []
            for reg in reversed(self.registration):
                if reg.registration_type_cl not in ('PPSALIEN', 'MISCLIEN', 'CROWNLIEN') and \
                   (self.verification_reg_id < 1 or reg.id <= self.verification_reg_id):
                    statement_json = reg.json
                    statement_json['statementType'] = \
                        model_utils.REG_CLASS_TO_STATEMENT_TYPE[reg.registration_type_cl]
                    changes.append(statement_json)
            statement['changes'] = changes
        return statement

    def set_payment_json(self, statement):
        """Add financing statement payment info json if payment exists."""
        if self.registration and self.registration[0].pay_invoice_id:
            payment = {
                'invoiceId': str(self.registration[0].pay_invoice_id),
                'receipt': self.registration[0].pay_path
            }
            statement['payment'] = payment
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
            if party.party_type == party_type or \
               (party_type == Party.PartyTypes.DEBTOR_COMPANY.value and
                party.party_type == Party.PartyTypes.DEBTOR_INDIVIDUAL.value):
                if not self.current_view_json and party.registration_id == registration_id:
                    party_json = party.json
                elif self.current_view_json and not party.registration_id_end:
                    party_json = party.json
                    if self.mark_update_json and party.registration_id != registration_id:
                        party_json['added'] = True

            if party_json:
                parties.append(party_json)

        return parties

    def general_collateral_json(self, registration_id):
        """Build general collateral JSON: current_view_json determines if current or original data is included."""
        if not self.general_collateral and not self.general_collateral_legacy:
            return None

        collateral_list = []
        for collateral in reversed(self.general_collateral):
            collateral_json = None
            if collateral.registration_id == registration_id:
                collateral_json = collateral.json
                collateral_list.append(collateral_json)
            elif self.current_view_json:
                collateral_json = collateral.current_json
                # Either adding gc only or deleting gc description only.
                if len(collateral.registration.general_collateral) == 1:
                    collateral_list.append(collateral_json)
                elif collateral.status and collateral.status == GeneralCollateralLegacy.StatusTypes.ADDED:
                    # Combine add and delete as one item.
                    delete_gc = collateral.registration.general_collateral[0]
                    if delete_gc.status and delete_gc.status == GeneralCollateralLegacy.StatusTypes.ADDED:
                        delete_gc = collateral.registration.general_collateral[1]
                        collateral_json['descriptionDelete'] = delete_gc.description
                    collateral_list.append(collateral_json)

        for collateral in reversed(self.general_collateral_legacy):
            collateral_json = None
            if collateral.registration_id == registration_id or not collateral.status:
                collateral_json = collateral.json
                collateral_list.append(collateral_json)
            elif self.current_view_json:  # Add only solution for legacy records identical to new.
                collateral_json = collateral.current_json
                # Either adding gc only or deleting gc description only.
                if len(collateral.registration.general_collateral_legacy) == 1:
                    collateral_list.append(collateral_json)
                elif collateral.status and collateral.status == GeneralCollateralLegacy.StatusTypes.ADDED:
                    # Combine add and delete as one item.
                    delete_gc = collateral.registration.general_collateral_legacy[0]
                    if delete_gc.status and delete_gc.status == GeneralCollateralLegacy.StatusTypes.ADDED:
                        delete_gc = collateral.registration.general_collateral_legacy[1]
                        collateral_json['descriptionDelete'] = delete_gc.description
                    collateral_list.append(collateral_json)
        return collateral_list

    def vehicle_collateral_json(self, registration_id):
        """Build vehicle collateral JSON: current_view_json determines if current or original data is included."""
        if not self.vehicle_collateral:
            return None

        collateral_list = []
        for collateral in self.vehicle_collateral:
            collateral_json = None
            if not self.current_view_json and collateral.registration_id == registration_id:
                collateral_json = collateral.json
            elif self.current_view_json and not collateral.registration_id_end:
                collateral_json = collateral.json
                if self.mark_update_json and collateral.registration_id != registration_id:
                    collateral_json['added'] = True

            if collateral_json:
                collateral_list.append(collateral_json)

        return collateral_list

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
        if 'businessName' in debtor_name_json:
            check_name = debtor_name_json['businessName'].upper()[:5]
        elif 'personName' in debtor_name_json and 'last' in debtor_name_json['personName']:
            check_name = debtor_name_json['personName']['last'].upper()[:5]
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

        max_results_size = int(current_app.config.get('ACCOUNT_REGISTRATIONS_MAX_RESULTS'))
        results = db.session.execute(model_utils.QUERY_ACCOUNT_FINANCING_STATEMENTS,
                                     {'query_account': account_id, 'max_results_size': max_results_size})
        rows = results.fetchall()
        if rows is not None:
            for row in rows:
                mapping = row._mapping  # pylint: disable=protected-access; follows documentation
                result = {
                    'registrationNumber': str(mapping['registration_number']),
                    'baseRegistrationNumber': str(mapping['registration_number']),
                    'createDateTime': model_utils.format_ts(mapping['registration_ts']),
                    'registrationType': str(mapping['registration_type']),
                    'registrationClass': str(mapping['registration_type_cl']),
                    'registrationDescription': str(mapping['registration_desc']),
                    'statusType': str(mapping['state']),
                    'expireDays': int(mapping['expire_days']),
                    'lastUpdateDateTime': model_utils.format_ts(mapping['last_update_ts']),
                    'registeringParty': str(mapping['registering_party']),
                    'securedParties': str(mapping['secured_party']),
                    'clientReferenceId': str(mapping['client_reference_id']),
                    'path': '/ppr/api/v1/financing-statements/' + str(mapping['registration_number'])
                }
                results_json.append(result)
        return results_json

    @classmethod
    def find_by_id(cls, financing_id: int = None):
        """Return a financing statement object by financing ID."""
        statement = None
        if financing_id:
            statement = db.session.query(FinancingStatement).\
                        filter(FinancingStatement.id == financing_id).one_or_none()

        return statement

    @classmethod
    def find_by_registration_number(cls, registration_num: str,
                                    account_id: str,
                                    staff: bool = False):
        """Return a financing statement by registration number."""
        statement = None
        if registration_num:
            statement = db.session.query(FinancingStatement).\
                        filter(FinancingStatement.id == Registration.financing_id,
                               Registration.registration_num == registration_num,
                               Registration.registration_type_cl.in_(['PPSALIEN', 'MISCLIEN', 'CROWNLIEN'])).\
                               one_or_none()

        if not statement:
            raise BusinessException(
                error=model_utils.ERR_FINANCING_NOT_FOUND.format(registration_num=registration_num),
                status_code=HTTPStatus.NOT_FOUND
            )

        if not staff and account_id and statement.registration[0].account_id != account_id:
            raise BusinessException(
                error=model_utils.ERR_REGISTRATION_ACCOUNT.format(account_id=account_id,
                                                                  registration_num=registration_num),
                status_code=HTTPStatus.BAD_REQUEST
            )

        if not staff and model_utils.is_historical(statement):
            raise BusinessException(
                error=model_utils.ERR_FINANCING_HISTORICAL.format(registration_num=registration_num),
                status_code=HTTPStatus.BAD_REQUEST
            )
        return statement

    @classmethod
    def find_by_financing_id(cls, financing_id: int = None):
        """Return a financing statement by financing statement ID."""
        statement = None
        if financing_id:
            statement = db.session.query(FinancingStatement).\
                        filter(FinancingStatement.id == Registration.financing_id,
                               FinancingStatement.id == financing_id).one_or_none()

        return statement

    @classmethod
    def find_debtor_names_by_registration_number(cls, registration_num: str = None):
        """Return a list of all debtor names fora base registration number."""
        names_json = []
        if not registration_num:
            return names_json

        statement = db.session.query(FinancingStatement).\
                    filter(FinancingStatement.id == Registration.financing_id,
                           Registration.registration_num == registration_num,
                           Registration.registration_type_cl.in_(['PPSALIEN', 'MISCLIEN', 'CROWNLIEN'])).\
                           one_or_none()
        if statement and statement.parties:
            for party in statement.parties:
                if party.party_type == model_utils.PARTY_DEBTOR_BUS:
                    name = {
                        'businessName': party.business_name
                    }
                    names_json.append(name)
                elif party.party_type == model_utils.PARTY_DEBTOR_IND:
                    person_name = {
                        'first': party.first_name,
                        'last': party.last_name
                    }
                    if party.middle_initial and party.middle_initial != '' and party.middle_initial.upper() != 'NONE':
                        person_name['middle'] = party.middle_initial
                    name = {
                        'personName': person_name
                    }
                    names_json.append(name)
        return names_json

    @staticmethod
    def create_from_json(json_data, account_id: str, user_id: str = None):
        """Create a financing statement object from a json Financing Statement schema object: map json to db."""
        statement = FinancingStatement()
        statement.state_type = model_utils.STATE_ACTIVE

        # Do this early as it also checks the party codes and may throw an exception
        statement.parties = Party.create_from_financing_json(json_data, None)

        reg_type = json_data['type']
        statement.registration = [Registration.create_financing_from_json(json_data, account_id, user_id)]
        statement.life = statement.registration[0].life
        if reg_type == model_utils.REG_TYPE_REPAIRER_LIEN:
            statement.expire_date = model_utils.expiry_dt_repairer_lien()
        elif statement.life and statement.life != model_utils.LIFE_INFINITE:
            statement.expire_date = model_utils.expiry_dt_from_years(statement.life)

        if reg_type == model_utils.REG_TYPE_OTHER and 'otherTypeDescription' in json_data:
            statement.crown_charge_other = json_data['otherTypeDescription']

        registration_id = statement.registration[0].id
        statement.trust_indenture = TrustIndenture.create_from_json(json_data, registration_id)
        if 'vehicleCollateral' in json_data:
            statement.vehicle_collateral = VehicleCollateral.create_from_financing_json(json_data, registration_id)
        if 'generalCollateral' in json_data:
            statement.general_collateral = GeneralCollateral.create_from_financing_json(json_data, registration_id)

        for party in statement.parties:
            party.registration_id = registration_id

        return statement
