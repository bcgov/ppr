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
"""This module holds data for ppr queue event tracking."""
from __future__ import annotations

from enum import Enum

from ppr_api.models import utils as model_utils

from .db import db


class EventTracking(db.Model):  # pylint: disable=too-many-instance-attributes
    """This class manages all of the event tracking information."""

    class EventTrackingTypes(str, Enum):
        """Render an Enum of the event tracking types."""

        SEARCH_REPORT = 'SEARCH_REPORT'
        API_NOTIFICATION = 'API_NOTIFICATION'
        EMAIL = 'EMAIL'
        SURFACE_MAIL = 'SURFACE_MAIL'
        EMAIL_REPORT = 'EMAIL_REPORT'
        REGISTRATION_REPORT = 'REGISTRATION_REPORT'

    __tablename__ = 'event_tracking'

    id = db.Column('id', db.Integer, db.Sequence('event_tracking_id_seq'), primary_key=True)
    key_id = db.Column('key_id', db.Integer, nullable=False, index=True)
    event_ts = db.Column('event_ts', db.DateTime, nullable=False, index=True)
    event_tracking_type = db.Column('event_tracking_type', db.String(20),
                                    db.ForeignKey('event_tracking_types.event_tracking_type'),
                                    nullable=False, index=True)
    status = db.Column('status', db.Integer, nullable=True)
    message = db.Column('message', db.String(2000), nullable=True)
    email_id = db.Column('email_address', db.String(250), nullable=True)

    # Relationships - SerialType
    tracking_type = db.relationship('EventTrackingType', foreign_keys=[event_tracking_type],
                                    back_populates='event_tracking', cascade='all, delete', uselist=False)

    def save(self):
        """Save the object to the database immediately."""
        db.session.add(self)
        db.session.commit()

    @property
    def json(self) -> dict:
        """Return the event tracking record as a json object."""
        event_tracking = {
            'eventTrackingId': self.id,
            'keyId': self.key_id,
            'type': self.event_tracking_type,
            'createDateTime': model_utils.format_ts(self.event_ts)
        }
        if self.status:
            event_tracking['status'] = self.status
        if self.message:
            event_tracking['message'] = self.message
        if self.email_id:
            event_tracking['emailAddress'] = self.email_id

        return event_tracking

    @classmethod
    def find_by_id(cls, event_id: int):
        """Return a tracking object by ID."""
        if event_id:
            return cls.query.get(event_id)

        return None

    @classmethod
    def find_by_key_id(cls, key_id: int):
        """Return a list of event tracking objects by key id."""
        event_tracking = None
        if key_id:
            event_tracking = cls.query.filter(EventTracking.key_id == key_id) \
                                      .order_by(EventTracking.id).all()

        return event_tracking

    @classmethod
    def find_by_key_id_type(cls, key_id: int, event_tracking_type: str, extra_key: str = None):
        """Return a list of event tracking objects by key id and event tracking type."""
        event_tracking = None
        if key_id and event_tracking_type:
            event_tracking = cls.query.filter(EventTracking.key_id == key_id,
                                              EventTracking.event_tracking_type == event_tracking_type) \
                                      .order_by(EventTracking.id).all()

            if event_tracking is not None and extra_key:
                events = []
                for event in event_tracking:
                    if event.message and event.message.find(extra_key) > 0:
                        events.append(event)
                return events
        return event_tracking

    @staticmethod
    def create(key_id: int, event_type: str, status: int = None, message: str = None):
        """Create an EventTracking record."""
        event_tracking = EventTracking(key_id=key_id, event_tracking_type=event_type, status=status, message=message)
        event_tracking.event_ts = model_utils.now_ts()
        event_tracking.save()

        return event_tracking
