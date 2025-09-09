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
"""This module holds data for MHR review registration workflow steps."""
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

from mhr_api.exceptions import DatabaseException
from mhr_api.models import utils as model_utils
from mhr_api.utils.logging import logger

from .db import db
from .type_tables import MhrReviewStatusTypes


class MhrReviewStep(db.Model):
    """This class manages all of the activity for the MHR staff review of a registration."""

    __tablename__ = "mhr_review_steps"

    id = db.mapped_column("id", db.Integer, db.Sequence("mhr_review_step_id_seq"), primary_key=True)
    create_ts = db.mapped_column("create_ts", db.DateTime, nullable=False, index=True)
    staff_note = db.mapped_column("staff_note", db.String(4000), nullable=True)
    client_note = db.mapped_column("client_note", db.String(4000), nullable=True)
    change_note = db.mapped_column("change_note", db.String(1000), nullable=True)
    username = db.mapped_column("username", db.String(1000), nullable=True)

    # parent keys
    review_registration_id = db.mapped_column(
        "review_registration_id", db.Integer, db.ForeignKey("mhr_review_registrations.id"), nullable=False, index=True
    )
    status_type = db.mapped_column(
        "status_type",
        PG_ENUM(MhrReviewStatusTypes, name="mhr_review_status_type"),
        db.ForeignKey("mhr_review_status_types.status_type"),
        nullable=False,
        index=True,
    )

    # Relationships - MhrReviewRegistration
    review_registration = db.relationship(
        "MhrReviewRegistration",
        foreign_keys=[review_registration_id],
        back_populates="review_steps",
        cascade="all, delete",
        uselist=False,
    )

    @property
    def json(self) -> dict:
        """Return the note as a json object."""
        step = {
            "createDateTime": model_utils.format_ts(self.registration.registration_ts),
            "statusType": self.status_type,
            "staffNote": self.staff_note if self.staff_note else "",
            "username": self.username if self.username else "",
            "clientNote": self.client_note if self.client_note else "",
            "changeNote": self.change_note if self.change_note else "",
        }
        return step

    def save(self):
        """Render a record of mhr review registration step information to the local cache."""
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as db_exception:  # noqa: B902; just logging
            logger.error("DB mhr review registration step save exception: " + str(db_exception))
            raise DatabaseException(db_exception) from db_exception

    @classmethod
    def find_by_id(cls, pkey: int = None):
        """Return a review step object by primary key."""
        step = None
        if pkey:
            try:
                step = db.session.query(MhrReviewStep).filter(MhrReviewStep.id == pkey).one_or_none()
            except Exception as db_exception:  # noqa: B902; return nicer error
                logger.error(f"MhrReviewStep.find_by_id exception: {db_exception}")
                raise DatabaseException(db_exception) from db_exception
        return step

    @classmethod
    def find_by_registration_id(cls, registration_id: int):
        """Return a list of review step objects by review registration id."""
        steps = None
        if registration_id:
            try:
                steps = (
                    db.session.query(MhrReviewStep)
                    .filter(MhrReviewStep.review_registration_id == registration_id)
                    .order_by(MhrReviewStep.id)
                    .all()
                )
            except Exception as db_exception:  # noqa: B902; return nicer error
                logger.error(f"MhrReviewStep.find_by_registration_id exception: {db_exception}")
                raise DatabaseException(db_exception) from db_exception
        return steps
