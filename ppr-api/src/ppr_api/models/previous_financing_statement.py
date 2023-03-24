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
"""This module holds data for legacy previous financing statement information only used in reports."""

from ppr_api.utils.base import BaseEnum

from .db import db


# Legacy registration types not allowed with new financing statements.
DATE_MONTH = {
    'JAN': '01',
    'FEB': '02',
    'MAR': '03',
    'APR': '04',
    'MAY': '05',
    'JUN': '06',
    'JUL': '07',
    'AUG': '08',
    'SEP': '09',
    'OCT': '10',
    'NOV': '11',
    'DEC': '12'
}


class PreviousFinancingStatement(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the previous financing statement information (legacy only)."""

    class PreviousRegistrationTypes(BaseEnum):
        """Render an Enum of the previous financing statement registration types."""

        ASSIGNMENT_OF_BOOK_ACCOUNTS = 'ASSIGNMENT OF BOOK ACCOUNTS'
        BILL_OF_SALE_ABSOLUTE = 'BILL OF SALE ABSOLUTE'
        CHATTEL_MORTGAGE = 'CHATTEL MORTGAGE'
        COMPANY_ACT_DOCUMENT = 'COMPANY ACT DOCUMENT'
        CONDITIONAL_SALE_AGREEMENT = 'CONDITIONAL SALE AGREEMENT'
        FARM_CREDIT_CHATTEL_MORTGAGE = 'FARM CREDIT CHATTEL MORTGAGE'
        MOBILE_HOME_ACT_DOCUMENT = 'MOBILE HOME ACT DOCUMENT'

    __tablename__ = 'previous_financing_statements'

    financing_id = db.Column('financing_id', db.Integer, db.ForeignKey('financing_statements.id'),
                             primary_key=True, nullable=False)
    # Free text description
    registration_type = db.Column('registration_type', db.String(30), nullable=False)
    # From Bob: need to change the data type from date for the 3 columns to varchar(7) as I am not able
    # to convert all of the values to a date those would have had to be a null value. Today all values
    # are displayed in the search result even ones that are not a date so the new search result must do the same.

    # cb is companies. Change from DateTime to String.
    cb_date = db.Column('cb_date', db.String(10), nullable=True)
    cb_number = db.Column('cb_number', db.String(10), nullable=True)
    # cr is central registry. Change from DateTime to String.
    cr_date = db.Column('cr_date', db.String(10), nullable=True)
    cr_number = db.Column('cr_number', db.String(10), nullable=True)
    # mhr is manufactured homes registry. Change from DateTime to String.
    mhr_date = db.Column('mhr_date', db.String(10), nullable=True)
    mhr_number = db.Column('mhr_number', db.String(10), nullable=True)

    # parent keys

    # Relationships - Registration
    financing_statement = db.relationship('FinancingStatement', foreign_keys=[financing_id],
                                          back_populates='previous_statement', cascade='all, delete', uselist=False)

    @property
    def json(self) -> dict:
        """Return the court_order as a json object."""
        previous_financing = {
            'transitionDescription': self.registration_type
        }
        if self.cb_date or self.mhr_date or self.cr_date:
            previous_financing['transitionDate'] = self.get_transition_date()
        if self.cb_number or self.mhr_number or self.cr_number:
            previous_financing['transitionNumber'] = self.get_transition_number()
        return previous_financing

    def get_transition_date(self):
        """Return a previous registration date in an ISO timestamp format."""
        date_iso: str = None
        transition_date: str = self.cr_date if self.cr_date else self.cb_date
        if not transition_date:
            transition_date = self.mhr_date
        if not transition_date:
            return date_iso
        if len(transition_date) == 10:
            date_iso = transition_date
        elif len(transition_date) == 6 or len(transition_date) == 7:
            date_iso = '19' + transition_date[0:2] + '-'
            if len(transition_date) == 7:
                date_iso += DATE_MONTH[transition_date[2:5]] + '-' + transition_date[5:]
            else:
                date_iso += transition_date[2:4] + '-' + transition_date[4:]
        if date_iso:
            date_iso = date_iso.replace(' ', '0')
            date_iso += 'T00:00:01-08:00'
        return date_iso

    def get_transition_number(self):
        """Return a previous registration number in the original format."""
        if self.cr_number:
            return self.cr_number
        if self.cb_number:
            return self.cb_number
        return self.mhr_number

    @classmethod
    def find_by_id(cls, financing_id: int = None):
        """Return a previous financing statement object by ID."""
        previous_financing = None
        if financing_id:
            previous_financing = cls.query.get(financing_id)

        return previous_financing
