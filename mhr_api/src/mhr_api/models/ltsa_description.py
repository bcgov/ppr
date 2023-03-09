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
"""This module holds data for LTSA legal description information."""
from flask import current_app

from mhr_api.models.utils import now_ts
from mhr_api.exceptions import DatabaseException

from .db import db


class LtsaDescription(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the LTSA legal description information."""

    __tablename__ = 'ltsa_descriptions'

    id = db.Column('id', db.Integer, db.Sequence('ltsa_description_id_seq'), primary_key=True)
    pid_number = db.Column('pid_number', db.String(11), nullable=False, index=True)
    ltsa_description = db.Column('ltsa_description', db.String(1000), nullable=False)
    update_ts = db.Column('update_ts', db.DateTime, nullable=True)

    # Relationships - none

    def save(self):
        """Save the object to the database immediately."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as save_exception:   # noqa: B902; return nicer error
            current_app.logger.error('DB save exception: ' + str(save_exception))
            raise DatabaseException(save_exception)

    @classmethod
    def find_by_id(cls, ltsa_id: int):
        """Return a ltsa description object by primary key (ID)."""
        ltsa_description = None
        if ltsa_id:
            try:
                ltsa_description = cls.query.get(ltsa_id)
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB find_by_id exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        return ltsa_description

    @classmethod
    def find_by_pid_number(cls, pid_number: str):
        """Return a ltsa description object by pid number."""
        ltsa_description = None
        if pid_number and len(pid_number.strip()) >= 9:
            pid: str = pid_number.strip().replace('-', '')
            try:
                ltsa_description = cls.query.filter(LtsaDescription.pid_number == pid).one_or_none()
            except Exception as db_exception:   # noqa: B902; return nicer error
                current_app.logger.error('DB find_by_pid_number exception: ' + str(db_exception))
                raise DatabaseException(db_exception)
        return ltsa_description

    @classmethod
    def update(cls, pid_number: str, description: str):
        """Update an existing ltsa description by pid number."""
        ltsa_description = None
        if pid_number and description and len(pid_number.strip()) >= 9:
            pid: str = pid_number.strip().replace('-', '')
            ltsa_description = cls.find_by_pid_number(pid)
        if ltsa_description:
            ltsa_description.update_ts = now_ts()
            ltsa_description.ltsa_description = description
        return ltsa_description

    @classmethod
    def create(cls, pid_number: str, description: str):
        """Create a ltsa description."""
        ltsa_description = LtsaDescription(pid_number=pid_number,
                                           ltsa_description=description,
                                           update_ts=now_ts())
        if pid_number and len(pid_number.strip()) > 9:
            ltsa_description.pid_number = pid_number.strip().replace('-', '')
        return ltsa_description
