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
"""This table manages a User ability to view additional financing statements.

Users may add and remove the visibility of financing statements in their registrations table
for financing statements that were not created with their account.
"""

from .db import db


class UserExtraRegistration(db.Model):
    """Used to hold the audit information for a User of this service."""

    __versioned__ = {}
    __tablename__ = 'user_extra_registrations'
    REMOVE_IND = 'Y'

    id = db.Column('id', db.Integer, db.Sequence('user_extra_registration_seq'), primary_key=True)
    account_id = db.Column('account_id', db.String(20), nullable=False, index=True)
    registration_number = db.Column('registration_number', db.String(10), nullable=False, index=True)
    # Only set when account is remove it's own registration from the list to be viewed.
    removed_ind = db.Column('removed_ind', db.String(1), nullable=True)

    def save(self):
        """Store the User into the local cache."""
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, extra_registration_id: int):
        """Return the user extra registration matching the id."""
        return db.session.query(UserExtraRegistration).\
            filter(UserExtraRegistration.id == extra_registration_id).one_or_none()

    @classmethod
    def find_by_registration_number(cls, registration_number: str, account_id: str):
        """Return the user extra registration matching the registration number and account id."""
        if registration_number and account_id:
            return db.session.query(UserExtraRegistration).\
                                    filter(UserExtraRegistration.registration_number == registration_number,
                                           UserExtraRegistration.account_id == account_id).one_or_none()
        return None

    @classmethod
    def delete(cls, registration_number: str, account_id: str):
        """Delete a user extra registation record by account ID and base registration number."""
        registration = None
        if registration_number and account_id:
            registration = cls.find_by_registration_number(registration_number, account_id)

        if registration:
            db.session.delete(registration)
            db.session.commit()

        return registration
