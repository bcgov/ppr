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
#import pycountry

from enum import Enum
from http import HTTPStatus

#from sqlalchemy import event

from .db import db

from ppr_api.utils.datetime import format_ts, now_ts
from ppr_api.exceptions import BusinessException

from .party import Party  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
from .expiry import Expiry  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
from .court_order import CourtOrder  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
from .general_collateral import GeneralCollateral  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
from .vehicle_collateral import VehicleCollateral  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
from .draft import Draft  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship


class Registration(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all statement registration information."""

    class RegistrationTypes(Enum):
        """Render an Enum of the registration types."""

        AMENDMENT_STATEMENT = 'AS'
        CHANGE_STATEMENT = 'CS'
        DISCHARGE_STATEMENT = 'DS'
        FINANCINNG_STATEMENT = 'FS'
        RENEWAL_STATEMENT = 'RS'

    __versioned__ = {}
    __tablename__ = 'registration'

#    registration_id = db.Column('registration_id', db.Integer, primary_key=True, server_default=db.FetchedValue())
#    registration_id = db.Column('registration_id', db.Integer, db.Sequence('registration_id_seq'), primary_key=True)
    # Always use get_next_registration_id() to generate PK.
    registration_id = db.Column('registration_id', db.Integer, primary_key=True)
    registration_num = db.Column('registration_num', db.String(12), nullable=False, index=True,  default=db.func.get_registration_num())
    registration_type_cd = db.Column('registration_type_cd', db.String(3), nullable=False) 
#                                     db.ForeignKey('registration_type.registration_type_cd'))
    registration_ts = db.Column('registration_ts', db.DateTime, nullable=False)
    account_id = db.Column('account_id', db.String(20), nullable=True)
    client_reference_id = db.Column('client_reference_id', db.String(20), nullable=True)
    change_type_cd = db.Column('change_type_cd', db.String(3), nullable=True) 
#                                     db.ForeignKey('change_type.change_type_cd'))
    pay_invoice_id = db.Column('pay_invoice_id', db.Integer, nullable=True)
    pay_path = db.Column('pay_path', db.String(256), nullable=True)

    # parent keys
    financing_id = db.Column('financing_id', db.Integer, 
                             db.ForeignKey('financing_statement.financing_id'), nullable=False)

    # relationships
    financing_statement = db.relationship("FinancingStatement", foreign_keys=[financing_id],
                                          back_populates="registration", cascade='all, delete', uselist=False)
    parties = db.relationship("Party", back_populates="registration")
    general_collateral = db.relationship("GeneralCollateral", back_populates="registration")
    vehicle_collateral = db.relationship("VehicleCollateral", back_populates="registration")
    draft = db.relationship("Draft", back_populates="registration", uselist=False)
    expiry = db.relationship("Expiry", back_populates="registration", uselist=False)
    trust_indenture = db.relationship("TrustIndenture", back_populates="registration", uselist=False)
    court_order = db.relationship("CourtOrder", back_populates="registration", uselist=False)

    base_registration_num = None


    @property
    def json(self) -> dict:
        """Return the registration as a json object."""
        registration = {
            'baseRegistrationNumber': self.base_registration_num,
            'createDateTime': format_ts(self.registration_ts)
        }
        if self.registration_type_cd == 'DS':
            registration['dischargeRegistrationNumber'] = self.registration_num
        elif self.registration_type_cd == 'RS':
            registration['renewalRegistrationNumber'] = self.registration_num
        elif self.registration_type_cd == 'AS':
            registration['amendmentRegistrationNumber'] = self.registration_num
        elif self.registration_type_cd == 'CS':
            registration['changeRegistrationNumber'] = self.registration_num

        if (self.registration_type_cd == 'CS' or self.registration_type_cd == 'AS') and \
                self.draft and self.draft.document_id:
            registration['documentId'] = self.draft.document_id

        if self.change_type_cd and (self.registration_type_cd == 'AS' or self.registration_type_cd == 'CS'):
            registration['changeType'] = self.change_type_cd
    
        if self.client_reference_id:
            registration['clientReferenceId'] = self.client_reference_id


        registration_id = self.registration_id
        if self.parties:
            for party in self.parties:
                if party.party_type_cd == 'RP' and party.registration_id == registration_id:
                    registration['registeringParty'] = party.json

        if self.registration_type_cd == 'RS' and self.expiry:
            registration['expiryDate'] = self.expiry.expiry_dt.isoformat()

        if (self.registration_type_cd == 'RS' or self.registration_type_cd == 'AS') and self.court_order:
            registration['courtOrderInformation'] = self.court_order.json

        # add debtors, secured parties
        if self.parties and (self.registration_type_cd == 'AS' or self.registration_type_cd == 'CS'):
            secured = []
            debtors = []
            for party in self.parties:
                if (party.party_type_cd == 'DC' or party.party_type_cd == 'DI') and \
                        party.registration_id == registration_id:
                    debtors.append(party.json)    
                elif party.party_type_cd == 'SP' and party.registration_id == registration_id:
                    secured.append(party.json) 

            if len(debtors) > 0:
                registration['addDebtors'] = debtors
            if len(secured) > 0:
                registration['addSecuredParties'] = secured

        # delete debtors, secured parties
        if self.financing_statement.parties and (self.registration_type_cd == 'AS' or self.registration_type_cd == 'CS'):
            secured = []
            debtors = []
            for party in self.financing_statement.parties:
                if (party.party_type_cd == 'DC' or party.party_type_cd == 'DI') and \
                        party.registration_id_end == registration_id:
                    debtors.append(party.json)    
                elif party.party_type_cd == 'SP' and party.registration_id_end == registration_id:
                    secured.append(party.json) 

            if len(debtors) > 0:
                registration['deleteDebtors'] = debtors
            if len(secured) > 0:
                registration['deleteSecuredParties'] = secured

        # add general collateral
        if self.general_collateral and (self.registration_type_cd == 'AS' or self.registration_type_cd == 'CS'):
            collateral = []
            for gc in self.general_collateral:
                if gc.registration_id == registration_id:
                    collateral.append(gc.json)
            if len(collateral) > 0:
                registration['addGeneralCollateral'] = collateral

        # delete general collateral
        if self.financing_statement.general_collateral and \
                (self.registration_type_cd == 'AS' or self.registration_type_cd == 'CS'):
            collateral = []
            for gc in self.financing_statement.general_collateral:
                if gc.registration_id_end == registration_id:
                    collateral.append(gc.json)
            if len(collateral) > 0:
                registration['deleteGeneralCollateral'] = collateral

        # add vehicle collateral
        if self.vehicle_collateral and (self.registration_type_cd == 'AS' or self.registration_type_cd == 'CS'):
            collateral = []
            for vc in self.vehicle_collateral:
                if vc.registration_id == registration_id:
                    collateral.append(vc.json)
            if len(collateral) > 0:
                registration['addVehicleCollateral'] = collateral

        # delete vehicle collateral
        if self.financing_statement.general_collateral and \
                (self.registration_type_cd == 'AS' or self.registration_type_cd == 'CS'):
            collateral = []
            for vc in self.financing_statement.vehicle_collateral:
                if vc.registration_id_end == registration_id:
                    collateral.append(vc.json)
            if len(collateral) > 0:
                registration['deleteVehicleCollateral'] = collateral

        return registration


    def save(self):
        """Render a registration to the local cache."""

        db.session.add(self)
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
                         registration_type: str,
                         financing_statement,
                         base_registration_num: str, 
                         account_id: str = None):
        """Create a registration object for an existing financing statement from dict/json."""

        # Perform all addtional data validation checks. 
        Registration.validate(json_data, financing_statement, registration_type)

        registration = Registration()
        registration.registration_ts = now_ts()
        registration.financing_id = financing_statement.financing_id
        registration.financing_statement = financing_statement
        registration.account_id = account_id
        registration.registration_type_cd = registration_type
        registration.base_registration_num = base_registration_num

        if 'clientReferenceId' in json_data:
            registration.client_reference_id = json_data['clientReferenceId']
        if (registration_type == 'AS' or registration_type == 'CS') and 'changeType' in json_data:
            registration.change_type_cd = json_data['changeType']


        # All registrations have at least one party (registering). 
        registration.parties = Party.create_from_statement_json(json_data, 
                                                                registration_type, 
                                                                registration.financing_id)

        # If get to here all data should be valid: get reg id to close out updated entities.
        registration_id = Registration.get_next_registration_id()
        registration.registration_id = registration_id
        if registration_type == 'DS':
            registration.financing_statement.state_type_cd = 'H'
        elif registration_type == 'RS':
            registration.expiry = Expiry.create_from_renewal_json(json_data, 
                                                                  financing_statement.financing_id,
                                                                  financing_statement.financing_type_cd,
                                                                  registration_id)
            if financing_statement.expiry:
                for exp in financing_statement.expiry:
                    if exp.registration_id != registration_id and not exp.registration_id_end:
                        exp.registration_id_end = registration_id

        # Repairer's lien renewal or amendment can have court order information.
        if (registration_type == 'AS' or registration_type == 'RS') and \
                'courtOrderInformation' in json_data:
            registration.court_order = CourtOrder.create_from_json(json_data['courtOrderInformation'],
                                                                    registration_id)

        if (registration_type == 'AS' or registration_type == 'CS'):
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

            # try and mark draft as consumed if document ID present.
            if 'documentId' in json_data:
                try:
                    doc_id = json_data['documentId'].strip()
                    if doc_id != '':
                        draft = Draft.find_by_document_id(doc_id, False)
                        if draft:
                            draft.registration_id = registration_id
                            registration.draft = draft
                except BusinessException:
                    registration.draft = None

        return registration


    @staticmethod
    def create_financing_from_json(json_data, account_id: str = None, registration_id: int = None):
        """Create a registraion object from dict/json."""
        registration = Registration()
        registration.account_id = account_id
        registration.registration_ts = now_ts()
        registration.registration_type_cd = 'FS'
        if registration_id:
            registration.registration_id = registration_id

        if 'clientReferenceId' in json_data:
            registration.client_reference_id = json_data['clientReferenceId']

        # try and mark draft as consumed if document ID present.
        if 'documentId' in json_data:
            try:
                doc_id = json_data['documentId'].strip()
                if doc_id != '':
                    draft = Draft.find_by_document_id(doc_id, False)
                    if draft:
                        draft.registration_id = registration_id
                        registration.draft = draft
            except BusinessException:
                registration.draft = None

        return registration



    @staticmethod
    def delete_from_json(json_data, registration, financing_statement):
        """For deleted parties and collateral in change/amendment registrations set registration_id_end 
           from dict/json."""

        if 'deleteDebtors' in json_data and len(json_data['deleteDebtors']) > 0:
            for party in json_data['deleteDebtors']:
                existing = Registration.find_party_by_id(party['partyId'], 
                                                        'DC', 
                                                        financing_statement.parties)
                if existing:
                    existing.registration_id_end = registration.registration_id

        if 'deleteSecuredParties' in json_data and len(json_data['deleteSecuredParties']) > 0:
            for party in json_data['deleteSecuredParties']:
                existing = Registration.find_party_by_id(party['partyId'], 
                                                        'SP',
                                                        financing_statement.parties)
                if existing:
                    existing.registration_id_end = registration.registration_id

        if 'deleteGeneralCollateral' in json_data and len(json_data['deleteGeneralCollateral']) > 0:
            for gc in json_data['deleteGeneralCollateral']:
                collateral = Registration.find_general_collateral_by_id(gc['collateralId'],
                                                                        financing_statement.general_collateral)
                if collateral:
                    collateral.registration_id_end = registration.registration_id

        if 'deleteVehicleCollateral' in json_data and len(json_data['deleteVehicleCollateral']) > 0:
            for vc in json_data['deleteVehicleCollateral']:
                collateral = Registration.find_vehicle_collateral_by_id(vc['vehicleId'],
                                                                       financing_statement.vehicle_collateral)
                if collateral:
                    collateral.registration_id_end = registration.registration_id


    @staticmethod
    def validate(json_data, financing_statement, registration_type: str):
        """Perform any extra data validation here, either because it is too

        complicated for the schema, or because it requires existing data.
        """

        error_msg = ''

        # Verify the party codes and delete party ID's.
        error_msg = error_msg + Registration.validate_parties(json_data, financing_statement)

        if (registration_type == 'AS' or registration_type == 'CS'):
            # Check delete vehicle ID's
            if 'deleteVehicleCollateral' in json_data:
                for collateral in json_data['deleteVehicleCollateral']:
                    if 'vehicleId' not in collateral:
                        error_msg = error_msg + 'Required vehicleId missing in deleteVehicleCollateral. '
                    else:
                        id = collateral['vehicleId']
                        existing = Registration.find_vehicle_collateral_by_id(id, 
                                                                              financing_statement.vehicle_collateral)
                        if not existing:
                            error_msg = error_msg + 'Invalid vehicleId ' + str(id) + \
                                                    ' in deleteVehicleCollateral. '

            # Check delete general collateral ID's
            if 'deleteGeneralCollateral' in json_data:
                for collateral in json_data['deleteGeneralCollateral']:
                    if 'collateralId' not in collateral:
                        error_msg = error_msg + 'Required collateralId missing in deleteGeneralCollateral. '
                    else:
                        id = collateral['collateralId']
                        existing = Registration.find_general_collateral_by_id(id, 
                                                                              financing_statement.general_collateral)
                        if not existing:
                            error_msg = error_msg + 'Invalid collateralId ' + str(id) + \
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
            if Party.verify_party_code(code) != True:
                error_msg = error_msg + 'No registering party client party found for code ' + code + '. '

        if 'addSecuredParties' in json_data:
            for party in json_data['addSecuredParties']:
                if 'code' in party:
                    code = party['code']
                    if Party.verify_party_code(code) != True:
                        error_msg = error_msg + 'No secured party client party found for code ' + code + '. '

        if 'deleteSecuredParties' in json_data:
            for party in json_data['deleteSecuredParties']:
                if 'partyId' not in party:
                    error_msg = error_msg + 'Required partyId missing in deleteSecuredParties.'
                else:
                    existing = Registration.find_party_by_id(party['partyId'], 
                                                             'SP', 
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
                                                            'DC',
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
            for p in parties:
                if p.party_id == party_id and party_type == p.party_type_cd and not p.registration_id_end:
                    party = p
                elif p.party_id == party_id and party_type == 'DC' and \
                        p.party_type_cd == 'DI' and not p.registration_id_end:
                    party = p

        return party


    @staticmethod
    def find_vehicle_collateral_by_id(vehicle_id: int, vehicle_collateral):
        """Search existing list of vehicle_collateral objects for a matching vehicle id."""

        collateral = None

        if vehicle_id and vehicle_collateral:
            for vc in vehicle_collateral:
                if vc.vehicle_id == vehicle_id and not vc.registration_id_end:
                    collateral = vc

        return collateral


    @staticmethod
    def find_general_collateral_by_id(collateral_id: int, general_collateral):
        """Search existing list of general_collateral objects for a matching collateral id."""

        collateral = None

        if collateral_id and general_collateral:
            for gc in general_collateral:
                if gc.collateral_id == collateral_id and not gc.registration_id_end:
                    collateral = gc

        return collateral


    @staticmethod
    def get_next_registration_id():
        """Generate a new registration ID from the database."""
        id = None
        result = db.session.execute("select registration_id_seq.nextval from dual")
        row = result.first()
        values = row.values()
        id = int(values[0])

        return id
