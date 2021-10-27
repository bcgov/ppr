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
"""This table manages a the mapping of BCRS account ID's to BCOL numbers.

Link an account id to a legacy BCOL number to associate the account with a client party code.
All crown charge accounts must have at least one record.
"""

from .db import db


class AccountBcolId(db.Model):
    """Map a user account ID to one or more BCOL account numbers."""

    __versioned__ = {}
    __tablename__ = 'account_bcol_ids'
    CROWN_CHARGE_YES = 'Y'

    id = db.Column('id', db.Integer, db.Sequence('account_bcol_id_seq'), primary_key=True)
    account_id = db.Column('account_id', db.String(20), nullable=False, index=True)
    bconline_account = db.Column('bconline_account', db.Integer, nullable=False)
    # Only set when account is a crown charge account.
    crown_charge_ind = db.Column('crown_charge_ind', db.String(1), nullable=True)

    def save(self):
        """Store the User into the local cache."""
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, account_bcol_id: int):
        """Return the mapping record matching the id."""
        return db.session.query(AccountBcolId).\
            filter(AccountBcolId.id == account_bcol_id).one_or_none()

    @classmethod
    def find_by_account_id(cls, account_id: str):
        """Return the account bcol numbers matching the account id."""
        if account_id:
            return db.session.query(AccountBcolId).\
                                    filter(AccountBcolId.account_id == account_id).all()
        return None

    @classmethod
    def find_by_account_id_bcol_number(cls, account_id: str, bconline_account: int):
        """Return the account bcol numbers matching the account id and bcol number."""
        if account_id:
            return db.session.query(AccountBcolId).\
                                    filter(AccountBcolId.account_id == account_id,
                                           AccountBcolId.bconline_account == bconline_account).one_or_none()
        return None

    @classmethod
    def delete(cls, account_id: str, bconline_account: int):
        """Future maintenance: delete an account bcol number mapping record by account ID and bcol number."""
        account_mapping = None
        if bconline_account and account_id:
            account_mapping = cls.find_by_account_id_bcol_number(account_id, bconline_account)

        if account_mapping:
            db.session.delete(account_mapping)
            db.session.commit()

        return account_mapping

    @staticmethod
    def crown_charge_account(account_id: str) -> bool:
        """Check if an account is configured for crown charge request types."""
        account_mappings = db.session.query(AccountBcolId).\
            filter(AccountBcolId.account_id == account_id,
                   AccountBcolId.crown_charge_ind == AccountBcolId.CROWN_CHARGE_YES).all()
        if account_mappings:
            return True
        return False
