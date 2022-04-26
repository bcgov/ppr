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
"""This module holds data for legacy DB2 MHR document descriptions."""
from flask import current_app

from mhr_api.exceptions import DatabaseException
from mhr_api.models import db


class Db2Docdes(db.Model):
    """This class manages all of the legacy DB2 MHR document descriptions."""

    __bind_key__ = 'db2'
    __tablename__ = 'docdes'

    doc_type = db.Column('docutype', db.String(4), primary_key=True)
    doc_name = db.Column('docuname', db.String(18), nullable=False)
    fee_code = db.Column('fee_code', db.String(6), nullable=False)

    # parent keys

    # relationships

    def save(self):
        """Save the object to the database immediately. Only used for unit testing."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as db_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB2 docdes.save exception: ' + str(db_exception))
            raise DatabaseException(db_exception)

    @classmethod
    def find_by_id(cls, doc_type: str):
        """Return the docdes matching the doc type."""
        docdes = None
        if doc_type:
            try:
                docdes = cls.query.get(doc_type)
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB2 docdes.find_by_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        if docdes:
            docdes.doc_type = docdes.doc_type.strip()
            docdes.doc_name = docdes.doc_name.strip()
            docdes.fee_code = docdes.fee_code.strip()
        return docdes

    @property
    def json(self):
        """Return a dict of this object, with keys in JSON format."""
        # Response legacy data: allow for any column to be null.
        doc_description = {
            'documentType': self.doc_type,
            'documentName': self.doc_name,
            'feeCode': self.fee_code
        }
        return doc_description

    @staticmethod
    def create_from_dict(new_info: dict):
        """Create a document description object from dict/json."""
        docdes = Db2Docdes(doc_type=new_info['documentType'],
                           doc_name=new_info['documentName'],
                           fee_code=new_info['feeCode'])
        return docdes

    @staticmethod
    def create_from_json(json_data):
        """Create a document description object from a json Docdes schema object: map json to db."""
        docdes = Db2Docdes.create_from_dict(json_data)
        if docdes.doc_type:
            docdes.doc_type = docdes.doc_type.strip()
        if docdes.doc_name:
            docdes.doc_name = docdes.doc_name.strip()
        if docdes.fee_code:
            docdes.fee_code = docdes.fee_code.strip()

        return docdes
