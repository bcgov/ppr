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
from __future__ import annotations

from enum import Enum
from http import HTTPStatus
from datetime import date

#from sqlalchemy import event

from ppr_api.exceptions import BusinessException
from ppr_api.utils.datetime import format_ts, now_ts, now_ts_offset

from .db import db
from .registration import Registration  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
from .expiry import Expiry  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
from .trust_indenture import TrustIndenture  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
from .party import Party  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
from .general_collateral import GeneralCollateral  # noqa: F401 pylint: disable=unused-import; needed by the SQLAlchemy relationship
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

    __versioned__ = {}
    __tablename__ = 'financing_statement'

    financing_id = db.Column('financing_id', db.Integer, primary_key=True, server_default=db.FetchedValue())
    financing_type_cd = db.Column('financing_type_cd', db.String(3), nullable=False) #, db.ForeignKey('financing_type.financing_type_cd'))
    state_type_cd = db.Column('state_type_cd', db.String(3), nullable=False) #, db.ForeignKey('state_type.state_type_cd'))
    lien_amount = db.Column('lien_amount', db.Numeric, nullable=True)
    surrender_dt = db.Column('surrender_dt', db.Date, nullable=True)

    # Parent keys

    # Relationships
    registration = db.relationship("Registration", order_by="asc(Registration.registration_ts)", 
                                   back_populates="financing_statement")
    parties = db.relationship("Party", back_populates="financing_statement")
    vehicle_collateral = db.relationship("VehicleCollateral", back_populates="financing_statement")
    general_collateral = db.relationship("GeneralCollateral", back_populates="financing_statement")
    expiry = db.relationship("Expiry", back_populates="financing_statement")
    trust_indenture = db.relationship("TrustIndenture", back_populates="financing_statement")


    @property
    def json(self) -> dict:
        """Return the financing statement as a json object."""
        statement = {
            'type': self.financing_type_cd
        }

        if self.registration and self.registration[0]:
            reg = self.registration[0]
            registration_id = reg.registration_id
            statement['baseRegistrationNumber'] = reg.registration_num
            statement['createDateTime'] = format_ts(reg.registration_ts)

            if reg.client_reference_id:
                statement['clientReferenceId'] = reg.client_reference_id
            
            if reg.draft and reg.draft.document_id:
                statement['documentId'] = reg.draft.document_id

            if self.parties:
                debtors = []
                secured = []
                for party in self.parties:
                    if party.party_type_cd == 'RP' and party.registration_id == registration_id:
                        statement['registeringParty'] = party.json
                    elif party.party_type_cd == 'SP' and not party.registration_id_end:
                        secured.append(party.json)
                    elif (party.party_type_cd == 'DC' or party.party_type_cd == 'DI') and \
                            not party.registration_id_end:
                        debtors.append(party.json)

                statement['securedParties'] = secured
                statement['debtors'] = debtors

            if self.general_collateral:
                gen_collateral = []
                for collateral in self.general_collateral:
                    if not collateral.registration_id_end:
                        gen_collateral.append(collateral.json)

                if len(gen_collateral) > 0:
                    statement['generalCollateral'] = gen_collateral

            if self.vehicle_collateral:
                v_collateral = []
                for collateral in self.vehicle_collateral:
                    if not collateral.registration_id_end:
                        v_collateral.append(collateral.json)

                if len(v_collateral) > 0:
                    statement['vehicleCollateral'] = v_collateral

        if self.trust_indenture:
            for trust in self.trust_indenture:
                if not trust.registration_id_end:
                    if trust.trust_indenture == 'Y':
                        statement['trustIndenture'] = True
                    else:
                        statement['trustIndenture'] = False
        else:
            statement['trustIndenture'] = False

        if self.expiry:
            for expiry_info in self.expiry:
                if not expiry_info.registration_id_end:
                    if expiry_info.life_infinite and expiry_info.life_infinite == 'Y':
                        statement['lifeInfinite'] = True
                    else:
                        statement['lifeYears'] = expiry_info.life_years
                        if expiry_info.expiry_dt:
                            statement['expiryDate'] = expiry_info.expiry_dt.isoformat()

        if self.financing_type_cd == 'RL':
            if self.lien_amount and self.lien_amount > 0:
                statement['lienAmount'] = str(self.lien_amount)

            if self.surrender_dt:
                statement['surrenderDate'] = self.surrender_dt.isoformat()

        return statement


    def validate_base_debtor(self, base_debtor_json, staff: bool = False):
        """Verify supplied base debtor when registering non-financing statements. Bypass the check for staff."""
        valid = False

        if staff and staff == True:
            return True

        if base_debtor_json:
            bus_name = None
            last = None
            first = None
            middle = None
            if 'businessName' in base_debtor_json:
                bus_name = base_debtor_json['businessName'].strip().upper()
            elif 'personName' in base_debtor_json:
                last = base_debtor_json['personName']['last'].strip().upper()
                first = base_debtor_json['personName']['first'].strip().upper()
                if 'middle' in base_debtor_json['personName']:
                    middle = base_debtor_json['personName']['middle'].strip().upper()

            if self.parties:
                for party in self.parties:
                    if (party.party_type_cd == 'DC' or party.party_type_cd == 'DI') and \
                            not party.registration_id_end:
                        if bus_name and party.business_name and \
                                bus_name == party.business_name.upper():
                            return True
                        elif last and party.last_name and last == party.last_name.upper() and \
                             first and party.first_name and first == party.first_name.upper():
                            if not middle and not party.middle_name:
                                return True
                            elif middle and party.middle_name and middle == party.middle_name.upper():
                                return True

        return valid


    def save(self):
        """Save the object to the database immediately."""

        db.session.add(self)
        db.session.commit()


    @classmethod
    def find_all_by_account_id(cls, account_id: str = None, staff: bool = False):
        """Return a summary list of recent financing statements belonging to an account."""
        statement_list = None
        if account_id:
            # No date range restriction for staff?
            if staff:
                statement_list = db.session.query(Registration.registration_ts, \
                                                Registration.registration_num, 
                                                FinancingStatement.financing_type_cd, \
                                                FinancingStatement.state_type_cd). \
                                    filter(FinancingStatement.financing_id == Registration.financing_id, \
                                           Registration.account_id == account_id, \
                                           Registration.registration_type_cd == 'FS'). \
                                    order_by(FinancingStatement.financing_id).all()
            else:
                days_ago = now_ts_offset(10, False)
                statement_list = db.session.query(Registration.registration_ts, \
                                                Registration.registration_num, 
                                                FinancingStatement.financing_type_cd, \
                                                FinancingStatement.state_type_cd). \
                                    filter(FinancingStatement.financing_id == Registration.financing_id, \
                                           Registration.account_id == account_id, \
                                           Registration.registration_type_cd == 'FS', \
                                           Registration.registration_ts > days_ago). \
                                    order_by(FinancingStatement.financing_id).all()

        if not statement_list:
            raise BusinessException(
                error=f'No Financing Statements found for Account ID {account_id}.',
                status_code=HTTPStatus.NOT_FOUND
            )

        results_json = []
        # only staff may view historical
        for statement in statement_list:
            if staff or statement.state_type_cd != 'H':
                statement_json = {
                    'matchType': 'EXACT',
                    'createDateTime': format_ts(statement.registration_ts),
                    'baseRegistrationNumber': statement.registration_num,
                    'registrationType': statement.financing_type_cd
                }            
                results_json.append(statement_json)

        # Non-staff, all historical/discharged
        if len(results_json) == 0:
            raise BusinessException(
                error=f'No active Financing Statements found for Account ID {account_id}.',
                status_code=HTTPStatus.NOT_FOUND
            )

        return results_json


    @classmethod
    def find_by_id(cls, financing_id: int = None):
        """Return a financing statement object by financing ID."""
        statement = None
        if financing_id:
            statement = cls.query.get(financing_id)

        return statement


    @classmethod
    def find_by_registration_number(cls, registration_num: str = None, 
                                    account_id: str = None,
                                    staff: bool = False):
        """Return a financing statement by registration number."""
        statement = None
        if registration_num:
            statement = cls.query.filter(FinancingStatement.financing_id == Registration.financing_id, \
                                          Registration.registration_num == registration_num, \
                                          Registration.registration_type_cd == 'FS').one_or_none()

        if not statement:
            raise BusinessException(
                error=f'No Financing Statement found for registration number {registration_num}.',
                status_code=HTTPStatus.NOT_FOUND
            )

        if not staff and statement.state_type_cd != 'A':
            raise BusinessException(
                error=f'The Financing Statement for registration number {registration_num} has been discharged.',
                status_code=HTTPStatus.BAD_REQUEST
            )
    
        return statement


    @classmethod
    def find_by_financing_id(cls, financing_id: int = None):
        """Return a financing statement by financing statement ID."""
        statement = None
        if financing_id:
            statement = cls.query.filter(FinancingStatement.financing_id == Registration.financing_id, \
                                         FinancingStatement.financing_id == financing_id).one_or_none()

        return statement


    @staticmethod
    def create_from_json(json_data, account_id:str):
        """Create a draft object from a json Draft schema object: map json to db."""
        # Perform all addtional data validation checks.
        FinancingStatement.validate(json_data)

        statement = FinancingStatement()
        statement.financing_type_cd = json_data['type']
        statement.state_type_cd = 'A'
        if statement.financing_type_cd == 'RL':
            if 'lienAmount' in json_data:
                amount = json_data['lienAmount'].strip()
                amount = amount.replace(',', '').replace('$', '')
                statement.lien_amount =  float(amount)
            if 'surrenderDate' in json_data:
                statement.surrender_dt =  date.fromisoformat(json_data['surrenderDate'])

        # Do this early as it also checks the party codes and may throw an exception
        statement.parties = Party.create_from_financing_json(json_data, None)

        registration_id = Registration.get_next_registration_id()
        statement.registration = [Registration.create_financing_from_json(json_data, account_id, registration_id)]
        statement.trust_indenture = TrustIndenture.create_from_json(json_data, registration_id)
        statement.expiry = Expiry.create_from_json(json_data, statement.financing_type_cd, registration_id)
        statement.expiry[0].registration_id = registration_id
        if 'vehicleCollateral' in json_data:
            statement.vehicle_collateral = VehicleCollateral.create_from_financing_json(json_data, registration_id)
        if 'generalCollateral' in json_data:
            statement.general_collateral = GeneralCollateral.create_from_financing_json(json_data, registration_id)

        for party in statement.parties:
            party.registration_id = registration_id

        return statement



    @staticmethod
    def validate(json_data):
        """Perform any extra data validation here, either because it is too

        complicated for the schema, or because it requires existing data (client party codes).
        """

        error_msg = ''

        # Verify the party codes.
        error_msg = error_msg + FinancingStatement.validate_parties(json_data)

        if error_msg != '':
            raise BusinessException(
                error=error_msg,
                status_code=HTTPStatus.BAD_REQUEST
            )


    @staticmethod
    def validate_parties(json_data):
        """Verify party codes."""
        error_msg = ''
        code = None

        if 'registeringParty' in json_data and 'code' in json_data['registeringParty']:
            code = json_data['registeringParty']['code']
            if Party.verify_party_code(code) != True:
                error_msg = error_msg + 'No registering party client party found for code ' + code + '. '

        if 'securedParties' in json_data:
            for party in json_data['securedParties']:
                if 'code' in party:
                    code = party['code']
                    if Party.verify_party_code(code) != True:
                        error_msg = error_msg + 'No secured party client party found for code ' + code + '. '

        return error_msg
