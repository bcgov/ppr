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
"""This module holds data for legacy DB2 compressed serial number information."""
from flask import current_app

from mhr_api.exceptions import DatabaseException
from mhr_api.models import db


class Db2Cmpserno(db.Model):
    """This class manages all of the legacy DB2 MHR compressed serial number information."""

    __bind_key__ = 'db2'
    __tablename__ = 'cmpserno'

    manuhome_id = db.Column('MANHOMID', db.Integer, primary_key=True)
    compressed_id = db.Column('CMPSERID', db.Integer, primary_key=True)
    compressed_key = db.Column('SERIALNO', db.String(3), nullable=False)

    # parent keys

    # Relationships

    def save(self):
        """Save the object to the database immediately."""
        try:
            db.session.add(self)
            db.session.commit()
            # current_app.logger.debug(f'Saved {self.json}')
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB2Cmpserno.save exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

    @classmethod
    def find_by_manuhome_id(cls, manuhome_id: int):
        """Return the compressed keys matching the manuhome id."""
        serial_keys = None
        if manuhome_id and manuhome_id > 0:
            try:
                serial_keys = cls.query.filter(Db2Cmpserno.manuhome_id == manuhome_id).all()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB2Cmpserno.find_by_manuhome_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        return serial_keys

    @property
    def json(self):
        """Return a dict of this object, with keys in JSON format."""
        key = {
            'compressedKeyId': self.compressed_id,
            'compressedKey': self.compressed_key
        }
        return key

    @property
    def registration_json(self):
        """Return a search registration dict of this object, with keys in JSON format."""
        # Response legacy data: allow for any column to be null.
        return self.json

    @staticmethod
    def create_from_dict(new_info: dict):
        """Create a compressed serial number key object from dict/json."""
        key = Db2Cmpserno(compressed_id=new_info.get('compressedKeyId', ''),
                          compressed_key=new_info.get('compressedKey', ''))
        return key

    @staticmethod
    def create_from_json(json_data):
        """Create a a compressed serial number key object from a json document schema object: map json to db."""
        key = Db2Cmpserno.create_from_dict(json_data)
        return key

    @staticmethod
    def create_from_registration(registration_id, key_id, compressed_key):
        """Create a new description object from a new MH registration."""
        key = Db2Cmpserno(manuhome_id=registration_id,
                          compressed_id=key_id,
                          compressed_key=compressed_key)
        return key
