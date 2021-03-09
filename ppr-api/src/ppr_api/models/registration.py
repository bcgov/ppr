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

from ppr_api.exceptions import BusinessException
from ppr_api.models import utils as model_utils

from .db import db
from .draft import Draft
from .party import Party
from .court_order import CourtOrder
from .general_collateral import GeneralCollateral
from .vehicle_collateral import VehicleCollateral
# noqa: I003


class Registration(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all statement registration information."""

    class RegistrationTypes(Enum):
        """Render an Enum of the registration types."""

        REG_CLASS_AMEND = 'AMENDMENT'
        REG_CLASS_AMEND_COURT = 'COURTORDER'
        REG_CLASS_CHANGE = 'CHANGE'
        REG_CLASS_FINANCING = 'PPSALIEN'
        REG_CLASS_DISCHARGE = 'DISCHARGE'
        REG_CLASS_RENEWAL = 'RENEWAL'

    __tablename__ = 'registration'

#    registration_id = db.Column('registration_id', db.Integer, primary_key=True, server_default=db.FetchedValue())
#    registration_id = db.Column('registration_id', db.Integer, db.Sequence('registration_id_seq'), primary_key=True)
    # Always use get_generated_values() to generate PK.
    registration_id = db.Column('registration_id', db.Integer, primary_key=True)
    registration_type_cd = db.Column('registration_type_cd', db.String(2), nullable=False)
#                                     db.ForeignKey('registration_type.registration_type_cd'))
    registration_type_cl = db.Column('registration_type_cl', db.String(10), nullable=False)
#                                     db.ForeignKey('registration_type.registration_type_class'))
    registration_ts = db.Column('registration_ts', db.DateTime, nullable=False)
    registration_num = db.Column('registration_number', db.String(10), nullable=False, index=True,
                                 default=db.func.get_registration_num())
    base_registration_num = db.Column('base_reg_number', db.String(10), nullable=True)
    account_id = db.Column('account_id', db.String(20), nullable=True)
    client_reference_id = db.Column('client_reference_id', db.String(20), nullable=True)
    life = db.Column('life', db.Integer, nullable=True)
    lien_value = db.Column('lien_value', db.String(15), nullable=True)
    surrender_date = db.Column('surrender_date', db.DateTime, nullable=True)
    ver_bypassed = db.Column('ver_bypassed', db.String(1), nullable=True)
    pay_invoice_id = db.Column('pay_invoice_id', db.Integer, nullable=True)
    pay_path = db.Column('pay_path', db.String(256), nullable=True)

    user_id = db.Column('user_id', db.String(1000), nullable=True)
    detail_description = db.Column('detail_description', db.String(180), nullable=True)
    sp_number = db.Column('sp_number', db.Integer, nullable=True)
    de_number = db.Column('de_number', db.Integer, nullable=True)
    ve_number = db.Column('ve_number', db.Integer, nullable=True)

    # parent keys
    financing_id = db.Column('financing_id', db.Integer,
                             db.ForeignKey('financing_statement.financing_id'), nullable=False)
    document_number = db.Column('document_number', db.String(10),
                                db.ForeignKey('draft.document_number'), nullable=False)

    # relationships
    financing_statement = db.relationship('FinancingStatement', foreign_keys=[financing_id],
                                          back_populates='registration', cascade='all, delete', uselist=False)
    parties = db.relationship('Party', back_populates='registration')
    general_collateral = db.relationship('GeneralCollateral', back_populates='registration')
    vehicle_collateral = db.relationship('VehicleCollateral', back_populates='registration')
    draft = db.relationship('Draft', foreign_keys=[document_number], uselist=False)
    trust_indenture = db.relationship('TrustIndenture', back_populates='registration', uselist=False)
    court_order = db.relationship('CourtOrder', back_populates='registration', uselist=False)

    base_registration_num = None

    @property
    def json(self) -> dict:
        """Return the registration as a json object."""
        registration = {
            'baseRegistrationNumber': self.base_registration_num,
            'createDateTime': model_utils.format_ts(self.registration_ts)
        }
        if self.registration_type_cd == model_utils.REG_TYPE_DISCHARGE:
            registration['dischargeRegistrationNumber'] = self.registration_num
        elif self.registration_type_cd == model_utils.REG_TYPE_RENEWAL:
            registration['renewalRegistrationNumber'] = self.registration_num
        elif self.registration_type_cd in (model_utils.REG_TYPE_AMEND, model_utils.REG_TYPE_AMEND_COURT):
            registration['amendmentRegistrationNumber'] = self.registration_num
        else:
            registration['changeRegistrationNumber'] = self.registration_num

#        if self.registration_type_cd != model_utils.REG_TYPE_DISCHARGE and \
#               self.registration_type_cd != model_utils.REG_TYPE_RENEWAL:
#            registration['documentId'] = self.document_number

        if self.registration_type_cl in (model_utils.REG_CLASS_AMEND,
                                         model_utils.REG_CLASS_AMEND_COURT,
                                         model_utils.REG_CLASS_CHANGE):
            registration['changeType'] = self.registration_type_cd

        if self.client_reference_id:
            registration['clientReferenceId'] = self.client_reference_id

        registration_id = self.registration_id
        if self.parties:
            for party in self.parties:
                if party.party_type_cd == model_utils.PARTY_REGISTERING and \
                        party.registration_id == registration_id:
                    registration['registeringParty'] = party.json

        if self.registration_type_cd == model_utils.REG_TYPE_RENEWAL and \
                self.financing_statement.expire_date:
            registration['expiryDate'] = model_utils.format_ts(self.financing_statement.expire_date)

        if self.court_order:
            registration['courtOrderInformation'] = self.court_order.json

        # add debtors, secured parties
        if self.parties and \
                (self.registration_type_cl in (model_utils.REG_CLASS_AMEND,
                                               model_utils.REG_CLASS_AMEND_COURT,
                                               model_utils.REG_CLASS_CHANGE)):
            secured = []
            debtors = []
            for party in self.parties:
                if party.party_type_cd in (model_utils.PARTY_DEBTOR_BUS, model_utils.PARTY_DEBTOR_IND) and \
                        party.registration_id == registration_id:
                    debtors.append(party.json)
                elif party.party_type_cd == model_utils.PARTY_SECURED and party.registration_id == registration_id:
                    secured.append(party.json)

            if debtors:
                registration['addDebtors'] = debtors
            if secured:
                registration['addSecuredParties'] = secured

        # delete debtors, secured parties
        if self.financing_statement.parties and \
                (self.registration_type_cl in (model_utils.REG_CLASS_AMEND,
                                               model_utils.REG_CLASS_AMEND_COURT,
                                               model_utils.REG_CLASS_CHANGE)):
            secured = []
            debtors = []
            for party in self.financing_statement.parties:
                if party.party_type_cd in (model_utils.PARTY_DEBTOR_BUS, model_utils.PARTY_DEBTOR_IND) and \
                        party.registration_id_end == registration_id:
                    debtors.append(party.json)
                elif party.party_type_cd == model_utils.PARTY_SECURED and party.registration_id_end == registration_id:
                    secured.append(party.json)

            if debtors:
                registration['deleteDebtors'] = debtors
            if secured:
                registration['deleteSecuredParties'] = secured

        # add general collateral
        if self.general_collateral and \
                (self.registration_type_cl in (model_utils.REG_CLASS_AMEND,
                                               model_utils.REG_CLASS_AMEND_COURT,
                                               model_utils.REG_CLASS_CHANGE)):
            collateral = []
            for gen_c in self.general_collateral:
                if gen_c.registration_id == registration_id:
                    collateral.append(gen_c.json)
            if collateral:
                registration['addGeneralCollateral'] = collateral

        # delete general collateral
        if self.financing_statement.general_collateral and \
                (self.registration_type_cl in (model_utils.REG_CLASS_AMEND,
                                               model_utils.REG_CLASS_AMEND_COURT,
                                               model_utils.REG_CLASS_CHANGE)):
            collateral = []
            for gen_c in self.financing_statement.general_collateral:
                if gen_c.registration_id_end == registration_id:
                    collateral.append(gen_c.json)
            if collateral:
                registration['deleteGeneralCollateral'] = collateral

        # add vehicle collateral
        if self.vehicle_collateral and \
                (self.registration_type_cl in (model_utils.REG_CLASS_AMEND,
                                               model_utils.REG_CLASS_AMEND_COURT,
                                               model_utils.REG_CLASS_CHANGE)):
            collateral = []
            for vehicle_c in self.vehicle_collateral:
                if vehicle_c.registration_id == registration_id:
                    collateral.append(vehicle_c.json)
            if collateral:
                registration['addVehicleCollateral'] = collateral

        # delete vehicle collateral
        if self.financing_statement.general_collateral and \
                (self.registration_type_cl in (model_utils.REG_CLASS_AMEND,
                                               model_utils.REG_CLASS_AMEND_COURT,
                                               model_utils.REG_CLASS_CHANGE)):
            collateral = []
            for vehicle_c in self.financing_statement.vehicle_collateral:
                if vehicle_c.registration_id_end == registration_id:
                    collateral.append(vehicle_c.json)
            if collateral:
                registration['deleteVehicleCollateral'] = collateral

        return registration

    def save(self):
        """Render a registration to the local cache."""
        db.session.add(self)
        db.session.commit()

        # Now save draft.registration_id
        draft = self.draft
        draft.registration_id = self.registration_id
        db.session.add(draft)
        db.session.commit()

    @classmethod
    def find_by_id(cls, registration_id: int):
        """Return the registration matching the id."""
        registration = None
        if registration_id:
            registration = cls.query.get(registration_id)
        return registration

    @classmethod
    def find_by_registration_number(cls, registration_num: str):
        """Return the registration matching the registration number."""
        registration = None
        if registration_num:
            registration = cls.query.filter(Registration.registration_num == registration_num).one_or_none()

        return registration

    @staticmethod
    def create_from_json(json_data,
                         registration_type_cl: str,
                         financing_statement,
                         base_registration_num: str,
                         account_id: str = None):
        """Create a registration object for an existing financing statement from dict/json."""
        # Perform all addtional data validation checks.
        Registration.validate(json_data, financing_statement, registration_type_cl)

        # Create or update draft.
        draft = Registration.find_draft(json_data, None, None)
        reg_vals = Registration.get_generated_values(draft)
        registration = Registration()
        registration.registration_id = reg_vals.registration_id
        registration.registration_num = reg_vals.registration_num
        registration.registration_ts = model_utils.now_ts()
        registration.financing_id = financing_statement.financing_id
        registration.financing_statement = financing_statement
        registration.account_id = account_id
        if not draft:
            registration.document_number = reg_vals.document_number
            draft = Draft.create_from_registration(registration, json_data)
        else:
            registration.document_number = draft.document_number
        registration.draft = draft
        registration.registration_type_cl = registration_type_cl
        if registration_type_cl in (model_utils.REG_CLASS_AMEND,
                                    model_utils.REG_CLASS_AMEND_COURT,
                                    model_utils.REG_CLASS_CHANGE):
            registration.registration_type_cd = json_data['changeType']
            if registration.registration_type_cd == model_utils.REG_TYPE_AMEND_COURT:
                registration.registration_type_cl = model_utils.REG_CLASS_AMEND_COURT
        if registration_type_cl == model_utils.REG_CLASS_RENEWAL:
            registration.registration_type_cd = model_utils.REG_TYPE_RENEWAL
        elif registration_type_cl == model_utils.REG_CLASS_DISCHARGE:
            registration.registration_type_cd = model_utils.REG_TYPE_DISCHARGE

        registration.base_registration_num = base_registration_num
        registration.ver_bypassed = 'Y'
        registration.draft.registration_type_cd = registration.registration_type_cd
        registration.draft.registration_type_cl = registration.registration_type_cl

        if 'clientReferenceId' in json_data:
            registration.client_reference_id = json_data['clientReferenceId']

        # All registrations have at least one party (registering).
        registration.parties = Party.create_from_statement_json(json_data,
                                                                registration_type_cl,
                                                                registration.financing_id)

        # If get to here all data should be valid: get reg id to close out updated entities.
        registration_id = registration.registration_id
        financing_reg_type = registration.financing_statement.registration[0].registration_type_cd
        if registration_type_cl == model_utils.REG_CLASS_DISCHARGE:
            registration.financing_statement.state_type_cd = model_utils.STATE_DISCHARGED
            registration.financing_statement.discharged = 'Y'
        elif registration_type_cl == model_utils.REG_CLASS_RENEWAL:
            registration.life = model_utils.REPAIRER_LIEN_YEARS
            registration.financing_statement.life = registration.life
            if financing_reg_type == model_utils.REG_TYPE_REPAIRER_LIEN:
                registration.financing_statement.expiry_date = \
                    model_utils.now_ts_offset(model_utils.REPAIRER_LIEN_DAYS, True)
            elif 'expiryDate' in json_data:
                registration.financing_statement.expiry_date = \
                    model_utils.expiry_ts_from_iso_format(json_data['expiryDate'])

        # Repairer's lien renewal or amendment can have court order information.
        if (registration.registration_type_cd == model_utils.REG_TYPE_AMEND_COURT or
                registration.registration_type_cd == model_utils.REG_TYPE_RENEWAL) and \
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
            # Close out deleted parties and collateral
            Registration.delete_from_json(json_data, registration, financing_statement)

        return registration

    @staticmethod
    def create_financing_from_json(json_data, account_id: str = None):
        """Create a registraion object from dict/json."""
        registration = Registration()
        registration.account_id = account_id
        registration.registration_ts = model_utils.now_ts()
        reg_type = json_data['type']
        registration.registration_type_cl = model_utils.REG_TYPE_TO_REG_CLASS[reg_type]
        registration.registration_type_cd = reg_type
        registration.ver_bypassed = 'Y'

        if reg_type == model_utils.REG_TYPE_REPAIRER_LIEN:
            if 'lienAmount' in json_data:
                registration.lien_value = json_data['lienAmount'].strip()
            if 'surrenderDate' in json_data:
                registration.surrender_date = model_utils.ts_from_date_iso_format(json_data['surrenderDate'])
            registration.life = model_utils.REPAIRER_LIEN_YEARS
        elif 'lifeInfinite' in json_data and json_data['lifeInfinite']:
            registration.life = model_utils.LIFE_INFINITE
        elif 'lifeYears' in json_data:
            registration.life = json_data['lifeYears']

        if 'clientReferenceId' in json_data:
            registration.client_reference_id = json_data['clientReferenceId']

        # Create or update draft.
        draft = Registration.find_draft(json_data, registration.registration_type_cl, reg_type)
        reg_vals = Registration.get_generated_values(draft)
        registration.registration_id = reg_vals.registration_id
        registration.registration_num = reg_vals.registration_num
        if not draft:
            registration.document_number = reg_vals.document_number
            draft = Draft.create_from_registration(registration, json_data)
        else:
            registration.document_number = draft.document_number
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
                    existing.registration_id_end = registration.registration_id

        if 'deleteSecuredParties' in json_data and json_data['deleteSecuredParties']:
            for party in json_data['deleteSecuredParties']:
                existing = Registration.find_party_by_id(party['partyId'],
                                                         model_utils.PARTY_SECURED,
                                                         financing_statement.parties)
                if existing:
                    existing.registration_id_end = registration.registration_id

        if 'deleteGeneralCollateral' in json_data and json_data['deleteGeneralCollateral']:
            for gen_c in json_data['deleteGeneralCollateral']:
                collateral = Registration.find_general_collateral_by_id(gen_c['collateralId'],
                                                                        financing_statement.general_collateral)
                if collateral:
                    collateral.registration_id_end = registration.registration_id

        if 'deleteVehicleCollateral' in json_data and json_data['deleteVehicleCollateral']:
            for vehicle_c in json_data['deleteVehicleCollateral']:
                collateral = Registration.find_vehicle_collateral_by_id(vehicle_c['vehicleId'],
                                                                        financing_statement.vehicle_collateral)
                if collateral:
                    collateral.registration_id_end = registration.registration_id

    @staticmethod
    def validate(json_data, financing_statement, registration_type_cl: str):
        """Perform any extra data validation here, either because it is too complicated for the schema.

        Or because it requires existing data.
        """
        error_msg = ''

        # Verify the party codes and delete party ID's.
        error_msg = error_msg + Registration.validate_parties(json_data, financing_statement)

        if registration_type_cl in (model_utils.REG_CLASS_AMEND,
                                    model_utils.REG_CLASS_AMEND_COURT,
                                    model_utils.REG_CLASS_CHANGE):
            # Check delete vehicle ID's
            if 'deleteVehicleCollateral' in json_data:
                for collateral in json_data['deleteVehicleCollateral']:
                    if 'vehicleId' not in collateral:
                        error_msg = error_msg + 'Required vehicleId missing in deleteVehicleCollateral. '
                    else:
                        collateral_id = collateral['vehicleId']
                        existing = Registration.find_vehicle_collateral_by_id(collateral_id,
                                                                              financing_statement.vehicle_collateral)
                        if not existing:
                            error_msg = error_msg + 'Invalid vehicleId ' + str(collateral_id) + \
                                                    ' in deleteVehicleCollateral. '

            # Check delete general collateral ID's
            if 'deleteGeneralCollateral' in json_data:
                for collateral in json_data['deleteGeneralCollateral']:
                    if 'collateralId' not in collateral:
                        error_msg = error_msg + 'Required collateralId missing in deleteGeneralCollateral. '
                    else:
                        collateral_id = collateral['collateralId']
                        existing = Registration.find_general_collateral_by_id(collateral_id,
                                                                              financing_statement.general_collateral)
                        if not existing:
                            error_msg = error_msg + 'Invalid collateralId ' + str(collateral_id) + \
                                                    ' in deleteGeneralCollateral. '

        if error_msg != '':
            raise BusinessException(
                error=error_msg,
                status_code=HTTPStatus.BAD_REQUEST
            )

    @staticmethod
    def validate_parties(json_data, financing_statement):
        """Verify party codes and delete party ID's."""
        error_msg = ''
        code = None

        if 'registeringParty' in json_data and 'code' in json_data['registeringParty']:
            code = json_data['registeringParty']['code']
            if not Party.verify_party_code(code):
                error_msg = error_msg + 'No registering party client party found for code ' + code + '. '

        if 'addSecuredParties' in json_data:
            for party in json_data['addSecuredParties']:
                if 'code' in party:
                    code = party['code']
                    if not Party.verify_party_code(code):
                        error_msg = error_msg + 'No secured party client party found for code ' + code + '. '

        if 'deleteSecuredParties' in json_data:
            for party in json_data['deleteSecuredParties']:
                if 'partyId' not in party:
                    error_msg = error_msg + 'Required partyId missing in deleteSecuredParties.'
                else:
                    existing = Registration.find_party_by_id(party['partyId'],
                                                             model_utils.PARTY_SECURED,
                                                             financing_statement.parties)
                    if not existing:
                        error_msg = error_msg + 'Invalid partyId ' + str(party['partyId']) + \
                                                ' in deleteSecuredParties. '

        if 'deleteDebtors' in json_data:
            for party in json_data['deleteDebtors']:
                if 'partyId' not in party:
                    error_msg = error_msg + 'Required partyId missing in deleteDebtors.'
                else:
                    existing = Registration.find_party_by_id(party['partyId'],
                                                             model_utils.PARTY_DEBTOR_BUS,
                                                             financing_statement.parties)
                    if not existing:
                        error_msg = error_msg + 'Invalid partyId ' + str(party['partyId']) + \
                                                ' in deleteDebtors. '

        return error_msg

    @staticmethod
    def find_party_by_id(party_id: int, party_type: str, parties):
        """Search existing list of party objects for a matching party id and type."""
        party = None

        if party_id and party_type and parties:
            for eval_party in parties:
                if eval_party.party_id == party_id and party_type == eval_party.party_type_cd and \
                        not eval_party.registration_id_end:
                    party = eval_party
                elif eval_party.party_id == party_id and party_type == model_utils.PARTY_DEBTOR_BUS and \
                        eval_party.party_type_cd == model_utils.PARTY_DEBTOR_IND and \
                        not eval_party.registration_id_end:
                    party = eval_party

        return party

    @staticmethod
    def find_vehicle_collateral_by_id(vehicle_id: int, vehicle_collateral):
        """Search existing list of vehicle_collateral objects for a matching vehicle id."""
        collateral = None

        if vehicle_id and vehicle_collateral:
            for v_collateral in vehicle_collateral:
                if v_collateral.vehicle_id == vehicle_id and not v_collateral.registration_id_end:
                    collateral = v_collateral

        return collateral

    @staticmethod
    def find_general_collateral_by_id(collateral_id: int, general_collateral):
        """Search existing list of general_collateral objects for a matching collateral id."""
        collateral = None

        if collateral_id and general_collateral:
            for g_collateral in general_collateral:
                if g_collateral.collateral_id == collateral_id and not g_collateral.registration_id_end:
                    collateral = g_collateral

        return collateral

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
                        draft.registration_type_cl = registration_class
                        draft.registration_type_cd = registration_type
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
        query = 'select registration_id_seq.nextval, get_registration_num(), get_draft_document_number() from dual'
        if draft:
            query = 'select registration_id_seq.nextval, get_registration_num() from dual'

        result = db.session.execute(query)
        row = result.first()
        values = row.values()
        registration.registration_id = int(values[0])
        registration.registration_num = str(values[1])
        if not draft:
            registration.document_number = str(values[2])

        return registration
