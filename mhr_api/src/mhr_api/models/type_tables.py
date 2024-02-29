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
"""This module holds model definitions for the MHR type tables."""

from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM
from mhr_api.utils.base import BaseEnum

from .db import db


class CountryType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the country_type table."""

    __tablename__ = 'country_types'

    country_type = db.mapped_column('country_type', db.String(2), primary_key=True)
    country_desc = db.mapped_column('country_desc', db.String(75), nullable=False)

    # parent keys

    # Relationships - Address
    address = db.relationship('Address', back_populates='country_type')


class ProvinceType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the province_type table."""

    __tablename__ = 'province_types'

    province_type = db.mapped_column('province_type', db.String(2), primary_key=True)
    country_type = db.mapped_column('country_type', db.String(2),
                                    db.ForeignKey('country_types.country_type'), nullable=False)
    province_desc = db.mapped_column('province_desc', db.String(75), nullable=False)

    # parent keys

    # Relationships - Address
    address = db.relationship('Address', back_populates='province_type')


class PartyType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the party_type table."""

    __tablename__ = 'party_types'

    party_type = db.mapped_column('party_type', db.String(2), primary_key=True)
    party_type_desc = db.mapped_column('party_type_desc', db.String(30), nullable=False)

    # parent keys

    # Relationships - Party
    party = db.relationship('Party', back_populates='party_types')


class RegistrationTypeClass(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the registration_type_class table."""

    __tablename__ = 'registration_type_classes'

    registration_type_cl = db.mapped_column('registration_type_cl', db.String(10), primary_key=True)
    registration_desc = db.mapped_column('registration_desc', db.String(100), nullable=False)

    # parent keys

    # Relationships


class RegistrationType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the registration_type table."""

    __tablename__ = 'registration_types'

    registration_type = db.mapped_column('registration_type', db.String(2), primary_key=True)
    registration_type_cl = db.mapped_column('registration_type_cl', db.String(10),
                                            db.ForeignKey('registration_type_classes.registration_type_cl'),
                                            nullable=False)
    registration_desc = db.mapped_column('registration_desc', db.String(100), nullable=False)
    registration_act = db.mapped_column('registration_act', db.String(60), nullable=False)

    # parent keys

    # Relationships - Registration
    registration = db.relationship('Registration', back_populates='reg_type')


class EventTrackingType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the event_tracking_types table."""

    __tablename__ = 'event_tracking_types'

    event_tracking_type = db.mapped_column('event_tracking_type', db.String(20), primary_key=True)
    event_tracking_desc = db.mapped_column('event_tracking_desc', db.String(100), nullable=False)

    # parent keys

    # Relationships - EventTracking
    event_tracking = db.relationship('EventTracking', back_populates='tracking_type')


class SearchType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the search_type table."""

    __tablename__ = 'search_types'

    search_type = db.mapped_column('search_type', db.String(2), primary_key=True)
    search_type_desc = db.mapped_column('search_type_desc', db.String(60), nullable=False)

    # parent keys

    # Relationships - SearchRequest
    search_request = db.relationship('SearchRequest', back_populates='search_request_type')


class StateType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the state_type table."""

    __tablename__ = 'state_types'

    state_type = db.mapped_column('state_type', db.String(3), primary_key=True)
    state_type_desc = db.mapped_column('state_type_desc', db.String(30), nullable=False)

    # parent keys

    # Relationships - FinancingStatement
    financing_statement = db.relationship('FinancingStatement', back_populates='fin_state_type')


class SerialType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the serial_type table."""

    __tablename__ = 'serial_types'

    serial_type = db.mapped_column('serial_type', db.String(2), primary_key=True)
    serial_type_desc = db.mapped_column('serial_type_desc', db.String(30), nullable=False)

    # parent keys

    # Relationships - VehicleCollateral
    vehicle_collateral = db.relationship('VehicleCollateral', back_populates='serial_type')


# MHR specific type table enums below
class MhrDocumentTypes(BaseEnum):
    """Render an Enum of the MHR note status types."""

    REG_101 = 'REG_101'
    REG_102 = 'REG_102'
    REG_103 = 'REG_103'
    REG_103E = 'REG_103E'
    ABAN = 'ABAN'
    ADDI = 'ADDI'
    AFFE = 'AFFE'
    ATTA = 'ATTA'
    BANK = 'BANK'
    BCLC = 'BCLC'
    CAU = 'CAU'
    CAUC = 'CAUC'
    CAUE = 'CAUE'
    COMP = 'COMP'
    CONF = 'CONF'
    CONV = 'CONV'
    COU = 'COU'
    COUR = 'COUR'
    DEAT = 'DEAT'
    DNCH = 'DNCH'
    EXMN = 'EXMN'
    EXNR = 'EXNR'
    EXRE = 'EXRE'
    EXRS = 'EXRS'
    FORE = 'FORE'
    FZE = 'FZE'
    GENT = 'GENT'
    INTE = 'INTE'
    INTW = 'INTW'
    LETA = 'LETA'
    MAID = 'MAID'
    MAIL = 'MAIL'
    MARR = 'MARR'
    MEAM = 'MEAM'
    NAMV = 'NAMV'
    NCAN = 'NCAN'
    NCON = 'NCON'
    NPUB = 'NPUB'
    NRED = 'NRED'
    PDEC = 'PDEC'
    PUBA = 'PUBA'
    REBU = 'REBU'
    REGC = 'REGC'
    REIV = 'REIV'
    REPV = 'REPV'
    REST = 'REST'
    STAT = 'STAT'
    SZL = 'SZL'
    TAXN = 'TAXN'
    TAXS = 'TAXS'
    THAW = 'THAW'
    TRAN = 'TRAN'
    VEST = 'VEST'
    WHAL = 'WHAL'
    WILL = 'WILL'
    TRANS_LAND_TITLE = 'TRANS_LAND_TITLE'
    TRANS_FAMILY_ACT = 'TRANS_FAMILY_ACT'
    TRANS_INFORMAL_SALE = 'TRANS_INFORMAL_SALE'
    TRANS_QUIT_CLAIM = 'TRANS_QUIT_CLAIM'
    TRANS_SEVER_GRANT = 'TRANS_SEVER_GRANT'
    TRANS_RECEIVERSHIP = 'TRANS_RECEIVERSHIP'
    TRANS_WRIT_SEIZURE = 'TRANS_WRIT_SEIZURE'
    AMEND_PERMIT = 'AMEND_PERMIT'
    CANCEL_PERMIT = 'CANCEL_PERMIT'
    REGC_STAFF = 'REGC_STAFF'
    REGC_CLIENT = 'REGC_CLIENT'


class MhrLocationTypes(BaseEnum):
    """Render an Enum of the MHR location types."""

    MANUFACTURER = 'MANUFACTURER'
    MH_PARK = 'MH_PARK'
    OTHER = 'OTHER'
    RESERVE = 'RESERVE'
    STRATA = 'STRATA'


class MhrNoteStatusTypes(BaseEnum):
    """Render an Enum of the MHR note status types."""

    ACTIVE = 'ACTIVE'
    CANCELLED = 'CANCELLED'
    EXPIRED = 'EXPIRED'
    CORRECTED = 'CORRECTED'


class MhrOwnerStatusTypes(BaseEnum):
    """Render an Enum of the MHR owner/owner group status types."""

    ACTIVE = 'ACTIVE'
    EXEMPT = 'EXEMPT'
    PREVIOUS = 'PREVIOUS'


class MhrPartyTypes(BaseEnum):
    """Render an Enum of the MHR party types."""

    OWNER_BUS = 'OWNER_BUS'
    OWNER_IND = 'OWNER_IND'
    SUBMITTING = 'SUBMITTING'
    EXECUTOR = 'EXECUTOR'
    ADMINISTRATOR = 'ADMINISTRATOR'
    TRUSTEE = 'TRUSTEE'
    TRUST = 'TRUST'
    MANUFACTURER = 'MANUFACTURER'
    CONTACT = 'CONTACT'


class MhrRegistrationStatusTypes(BaseEnum):
    """Render an Enum of the MHR registration status types."""

    ACTIVE = 'ACTIVE'
    CANCELLED = 'CANCELLED'
    DRAFT = 'DRAFT'
    EXEMPT = 'EXEMPT'
    HISTORICAL = 'HISTORICAL'


class MhrRegistrationTypes(BaseEnum):
    """Render an Enum of the MHR registration types."""

    DECAL_REPLACE = 'DECAL_REPLACE'
    MHREG = 'MHREG'
    TRAND = 'TRAND'
    TRANS = 'TRANS'
    TRANS_AFFIDAVIT = 'TRANS_AFFIDAVIT'
    TRANS_ADMIN = 'TRANS_ADMIN'
    TRANS_WILL = 'TRANS_WILL'
    EXEMPTION_RES = 'EXEMPTION_RES'
    EXEMPTION_NON_RES = 'EXEMPTION_NON_RES'
    PERMIT = 'PERMIT'
    PERMIT_EXTENSION = 'PERMIT_EXTENSION'
    MANUFACTURER = 'MANUFACTURER'
    MHREG_CONVERSION = 'MHREG_CONVERSION'
    REG_STAFF_ADMIN = 'REG_STAFF_ADMIN'
    REG_NOTE = 'REG_STAFF_ADMIN'
    AMENDMENT = 'AMENDMENT'


class MhrStatusTypes(BaseEnum):
    """Render an Enum of the MHR general status types."""

    ACTIVE = 'ACTIVE'
    DRAFT = 'DRAFT'
    HISTORICAL = 'HISTORICAL'


class MhrTenancyTypes(BaseEnum):
    """Render an Enum of the MHR tenancy types."""

    COMMON = 'COMMON'
    JOINT = 'JOINT'
    NA = 'NA'
    SOLE = 'SOLE'


# MHR specific type tables below
class MhrDocumentType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the mhr_document_types table."""

    __tablename__ = 'mhr_document_types'

    document_type = db.mapped_column('document_type', PG_ENUM(MhrDocumentTypes, name='mhrdocumenttype'),
                                     primary_key=True)
    document_type_desc = db.mapped_column('document_type_desc', db.String(100), nullable=False)
    legacy_fee_code = db.mapped_column('legacy_fee_code', db.String(6), nullable=True)

    # Relationships -

    @classmethod
    def find_all(cls):
        """Return all the type records."""
        return db.session.query(MhrDocumentType).all()

    @classmethod
    def find_by_doc_type(cls, doc_type: str):
        """Return a specific record by type."""
        if not doc_type or doc_type not in MhrDocumentTypes:
            return None
        return db.session.query(MhrDocumentType).filter(MhrDocumentType.document_type == doc_type).one_or_none()


class MhrLocationType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the mhr_location_types table."""

    __tablename__ = 'mhr_location_types'

    location_type = db.mapped_column('location_type', PG_ENUM(MhrLocationTypes, name='mhrlocationtype'),
                                     primary_key=True)
    location_type_desc = db.mapped_column('location_type_desc', db.String(100), nullable=False)

    # Relationships -

    @classmethod
    def find_all(cls):
        """Return all the type records."""
        return db.session.query(MhrLocationType).all()


class MhrNoteStatusType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the mhr_note_status_types table."""

    __tablename__ = 'mhr_note_status_types'

    status_type = db.mapped_column('status_type', PG_ENUM(MhrNoteStatusTypes, name='mhrnotestatustype'),
                                   primary_key=True)
    status_type_desc = db.mapped_column('status_type_desc', db.String(100), nullable=False)
    legacy_status_type = db.mapped_column('legacy_status_type', db.String(1), nullable=False)

    # Relationships -

    @classmethod
    def find_all(cls):
        """Return all the type records."""
        return db.session.query(MhrNoteStatusType).all()


class MhrOwnerStatusType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the mhr_owner_status_types table."""

    __tablename__ = 'mhr_owner_status_types'

    status_type = db.mapped_column('status_type', PG_ENUM(MhrOwnerStatusTypes, name='mhrownerstatustype'),
                                   primary_key=True)
    status_type_desc = db.mapped_column('status_type_desc', db.String(100), nullable=False)
    legacy_status_type = db.mapped_column('legacy_status_type', db.String(1), nullable=False)

    # Relationships -

    @classmethod
    def find_all(cls):
        """Return all the type records."""
        return db.session.query(MhrOwnerStatusType).all()


class MhrPartyType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the mhr_party_types table."""

    __tablename__ = 'mhr_party_types'

    party_type = db.mapped_column('party_type', PG_ENUM(MhrPartyTypes, name='mhrpartytype'), primary_key=True)
    party_type_desc = db.mapped_column('party_type_desc', db.String(100), nullable=False)
    legacy_party_type = db.mapped_column('legacy_party_type', db.String(1), nullable=True)

    # Relationships -

    @classmethod
    def find_all(cls):
        """Return all the type records."""
        return db.session.query(MhrPartyType).all()


class MhrRegistrationStatusType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the mhr_registration_status_types table."""

    __tablename__ = 'mhr_registration_status_types'

    status_type = db.mapped_column('status_type',
                                   PG_ENUM(MhrRegistrationStatusTypes, name='mhrregistrationstatustype'),
                                   primary_key=True)
    status_type_desc = db.mapped_column('status_type_desc', db.String(100), nullable=False)
    legacy_status_type = db.mapped_column('legacy_status_type', db.String(1), nullable=False)

    # Relationships -

    @classmethod
    def find_all(cls):
        """Return all the type records."""
        return db.session.query(MhrRegistrationStatusType).all()


class MhrRegistrationType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the mhr_registration_types table."""

    __tablename__ = 'mhr_registration_types'

    registration_type = db.mapped_column('registration_type',
                                         PG_ENUM(MhrRegistrationTypes, name='mhrregistrationtype'),
                                         primary_key=True)
    registration_type_desc = db.mapped_column('registration_type_desc', db.String(100), nullable=False)
    legacy_registration_type = db.mapped_column('legacy_registration_type', db.String(4), nullable=False)

    # Relationships - MHR Registration
    registration = db.relationship('MhrRegistration', back_populates='reg_type')

    @classmethod
    def find_all(cls):
        """Return all the type records."""
        return db.session.query(MhrRegistrationType).all()


class MhrStatusType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the mhr_status_types table."""

    __tablename__ = 'mhr_status_types'

    status_type = db.mapped_column('status_type', PG_ENUM(MhrStatusTypes, name='mhrstatustype'), primary_key=True)
    status_type_desc = db.mapped_column('status_type_desc', db.String(100), nullable=False)
    legacy_status_type = db.mapped_column('legacy_status_type', db.String(1), nullable=False)

    # Relationships -

    @classmethod
    def find_all(cls):
        """Return all the type records."""
        return db.session.query(MhrStatusType).all()


class MhrTenancyType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the mhr_tenancy_types table."""

    __tablename__ = 'mhr_tenancy_types'

    tenancy_type = db.mapped_column('tenancy_type', PG_ENUM(MhrTenancyTypes, name='mhrtenancytype'), primary_key=True)
    tenancy_type_desc = db.mapped_column('tenancy_type_desc', db.String(100), nullable=False)
    legacy_tenancy_type = db.mapped_column('legacy_tenancy_type', db.String(2), nullable=False)

    # Relationships -

    @classmethod
    def find_all(cls):
        """Return all the type records."""
        return db.session.query(MhrTenancyType).all()
