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
import re

from flask import current_app
from sqlalchemy import text

from mhr_api.exceptions import DatabaseException
from mhr_api.models import db


UPDATE_SEARCH_KEY = """
update cmpserno
   set serialno = EBCDIC_CHR({int_1}) || EBCDIC_CHR({int_2}) || EBCDIC_CHR({int_3})
 where manhomid = {id}
   and cmpserid = {sequence_id}
"""


class Db2Cmpserno(db.Model):
    """This class manages all of the legacy DB2 MHR compressed serial number information."""

    __bind_key__ = 'db2'
    __tablename__ = 'cmpserno'

    manuhome_id = db.Column('MANHOMID', db.Integer, db.ForeignKey('manuhome.manhomid'), primary_key=True)
    compressed_id = db.Column('CMPSERID', db.Integer, primary_key=True)
    compressed_key = db.Column('SERIALNO', db.String(3), nullable=False)

    # parent keys

    # Relationships
    registration = db.relationship('Db2Manuhome', foreign_keys=[manuhome_id],
                                   back_populates='serial_nums', cascade='all, delete', uselist=False)
    serial_number: str = None

    def save(self):
        """Save the object to the database immediately."""
        try:
            db.session.add(self)
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

    def get_search_serial_number_key_hex(self) -> str:
        """Get the compressed search serial number key for the MH serial number."""
        key: str = ''

        if not self.serial_number:
            return key
        key = self.serial_number.strip().upper()
        # 1. Remove all non-alphanumberic characters.
        key = re.sub('[^0-9A-Z]+', '', key)
        # current_app.logger.debug(f'1: key={key}')
        # 2. Add 6 zeroes to the start of the serial number.
        key = '000000' + key
        # current_app.logger.debug(f'2: key={key}')
        # 3. Determine the value of I as last position in the serial number that contains a numeric value.
        last_pos: int = 0
        for index, char in enumerate(key):
            if char.isdigit():
                last_pos = index
        # 4. Replace alphas with the corresponding integers:
        # 08600064100100000050000042  where A=0, B=8, C=6…Z=2
        key = key.replace('B', '8')
        key = key.replace('C', '6')
        key = key.replace('G', '6')
        key = key.replace('H', '4')
        key = key.replace('I', '1')
        key = key.replace('L', '1')
        key = key.replace('S', '5')
        key = key.replace('Y', '4')
        key = key.replace('Z', '2')
        key = re.sub('[A-Z]', '0', key)
        # 5. Take 6 characters of the string beginning at position I – 5 and ending with the position determined by I
        # in step 3.
        start_pos = last_pos - 5
        key = key[start_pos:(last_pos + 1)]
        # 6. Convert it to bytes and return the last 3.
        key_bytes: bytes = int(key).to_bytes(3, 'big')
        key_hex = key_bytes.hex().upper()
        current_app.logger.debug(f'key={key} last 3 bytes={key_bytes} hex={key_hex}')
        return key_hex

    def update_serial_key(self):
        """Set the serial number compressed key value for searching."""
        if not self.serial_number:
            return
        try:
            query_s = UPDATE_SEARCH_KEY
            key_hex = self.get_search_serial_number_key_hex()
            char_1 = key_hex[0:2]
            char_2 = key_hex[2:4]
            char_3 = key_hex[4:]
            current_app.logger.info(f'char_1={char_1} char_2={char_2} char_3={char_3}')
            int_1: int = int(char_1, 16)
            int_2: int = int(char_2, 16)
            int_3: int = int(char_3, 16)
            current_app.logger.info(f'int_1={int_1} int_2={int_2} int_3={int_3}')
            query_s = query_s.format(int_1=int_1,
                                     int_2=int_2,
                                     int_3=int_3,
                                     id=self.manuhome_id,
                                     sequence_id=self.compressed_id)
            current_app.logger.debug(f'Executing update query {query_s}')
            query = text(query_s)
            db.get_engine(current_app, 'db2').execute(query)
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB2 update_serial_key exception: ' + str(db_exception))
