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
"""This table manages an account's ability to view additional MH registrations.

Users may add and remove the visibility of MH registrations in their account registrations table
to include registrations that were not created with their account.
"""

from .db import db


class MhrExtraRegistration(db.Model):
    """Used to hold the registrations visible to the user that were created with another account."""

    __tablename__ = 'mhr_extra_registrations'
    REMOVE_IND = 'Y'

    id = db.Column('id', db.Integer, db.Sequence('mhr_extra_registration_seq'), primary_key=True)
    account_id = db.Column('account_id', db.String(20), nullable=False, index=True)
    mhr_number = db.Column('mhr_number', db.String(6), nullable=False, index=True)
    # Only set when the account removes its own registration from the list to be viewed.
    removed_ind = db.Column('removed_ind', db.String(1), nullable=True)

    def save(self):
        """Store the User into the local cache."""
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, extra_registration_id: int):
        """Return the user extra registration matching the id."""
        return db.session.query(MhrExtraRegistration).\
            filter(MhrExtraRegistration.id == extra_registration_id).one_or_none()

    @classmethod
    def find_by_mhr_number(cls, mhr_number: str, account_id: str):
        """Return the user extra registration matching the MHR number and account id."""
        if mhr_number and account_id:
            return db.session.query(MhrExtraRegistration).\
                                    filter(MhrExtraRegistration.mhr_number == mhr_number,
                                           MhrExtraRegistration.account_id == account_id).one_or_none()
        return None

    @classmethod
    def find_by_account_id(cls, account_id: str):
        """Return an list of user extra registration matching the account id."""
        if account_id:
            return db.session.query(MhrExtraRegistration).\
                                    filter(MhrExtraRegistration.account_id == account_id).all()
        return None

    @classmethod
    def find_mhr_numbers_by_account_id(cls, account_id: str):
        """Return an list of user extra registration MHR numbers matching the account id."""
        mhr_numbers = []
        if account_id:
            registrations = db.session.query(MhrExtraRegistration).\
                                             filter(MhrExtraRegistration.account_id == account_id).all()
            if registrations:
                for reg in registrations:
                    mhr = {'mhr_number': reg.mhr_number}
                    mhr_numbers.append(mhr)
        return mhr_numbers

    @classmethod
    def delete(cls, mhr_number: str, account_id: str):
        """Delete a user extra registation record by account ID and MHR number."""
        registration = None
        if mhr_number and account_id:
            registration = cls.find_by_mhr_number(mhr_number, account_id)

        if registration:
            db.session.delete(registration)
            db.session.commit()

        return registration
