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
"""This module holds data for the debtor individual name search nickname table."""

from .db import db


class Nickname(db.Model):
    """This class manages all of name search nicknames referenced by a database function. Managed by Alembic."""

    __tablename__ = 'nickname'

    name_id = db.Column('name_id', db.Integer, nullable=False, index=True)
    name = db.Column('name', db.String(25), nullable=False, index=True)

    # parent keys

    # relationships

    def save(self):
        """Save the object to the database immediately. Only used for unit testing."""
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, name_id: int):
        """Return the nickname matching the id."""
        nickname = None
        if name_id:
            nickname = cls.query.get(name_id)
        return nickname

    @property
    def json(self):
        """Return a dict of this object, with keys in JSON format."""
        nickname = {
            'name_id': self.name_id,
            'name': self.name
        }
        return nickname
