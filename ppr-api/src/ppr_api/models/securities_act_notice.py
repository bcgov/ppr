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
"""This module holds specific securities act registration information."""
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

from .utils import format_ts, ts_from_iso_format
from .db import db
from .securities_act_order import SecuritiesActOrder
from .type_tables import SecuritiesActTypes


class SecuritiesActNotice(db.Model):
    """This class manages the securities act registration extra information."""

    __tablename__ = 'securities_act_notices'

    id = db.mapped_column('id', db.Integer, db.Sequence('securities_act_notice_id_seq'), primary_key=True)
    effective_ts = db.mapped_column('effective_ts', db.DateTime, nullable=False)
    detail_description = db.mapped_column('detail_description', db.String(4000), nullable=True)
    registration_id_end = db.mapped_column('registration_id_end', db.Integer, nullable=True, index=True)

    # parent keys
    registration_id = db.mapped_column('registration_id', db.Integer, db.ForeignKey('registrations.id'),
                                       nullable=False,
                                       index=True)
    securities_act_type = db.mapped_column('securities_act_type',
                                           PG_ENUM(SecuritiesActTypes, name='securitiesacttype'),
                                           db.ForeignKey('securities_act_types.securities_act_type'),
                                           nullable=False)
    # For amendment distinguishing notice edit from remove/add
    previous_notice_id = db.mapped_column('previous_notice_id', db.Integer, nullable=True)

    # Relationships - Registration
    registration = db.relationship('Registration', foreign_keys=[registration_id],
                                   back_populates='securities_act_notices', cascade='all, delete', uselist=False)
    sec_act_type = db.relationship('SecuritiesActType', foreign_keys=[securities_act_type],
                                   back_populates='securities_act_notice', cascade='all, delete', uselist=False)
    securities_act_orders = db.relationship('SecuritiesActOrder', order_by='asc(SecuritiesActOrder.id)',
                                            back_populates='securities_act_notice')

    @property
    def json(self) -> dict:
        """Return the securities act as a json object."""
        securities_act = {
            'noticeId': self.id,   # Needed by amendment delete notices.
            'securitiesActNoticeType': self.securities_act_type
        }
        if self.effective_ts:
            securities_act['effectiveDateTime'] = format_ts(self.effective_ts)
        if self.detail_description:
            securities_act['description'] = self.detail_description
        if self.sec_act_type:
            securities_act['registrationDescription'] = self.sec_act_type.securities_act_type_desc
        if self.securities_act_orders:
            orders = []
            for order in self.securities_act_orders:
                orders.append(order.json)
            securities_act['securitiesActOrders'] = orders
        if self.previous_notice_id is not None:
            securities_act['amendNoticeId'] = self.previous_notice_id
        return securities_act

    @classmethod
    def find_by_id(cls, sec_id: int):
        """Return an securities act object by primary key ID."""
        securities_act = None
        if sec_id:
            securities_act = db.session.query(SecuritiesActNotice).filter(SecuritiesActNotice.id == sec_id) \
                                       .one_or_none()

        return securities_act

    @classmethod
    def find_by_registration_id(cls, reg_id: int):
        """Return a list of securities act objects by registration id."""
        securities_acts = None
        if reg_id:
            securities_acts = db.session.query(SecuritiesActNotice) \
                                        .filter(SecuritiesActNotice.registration_id == reg_id) \
                                        .order_by(SecuritiesActNotice.id).all()
        return securities_acts

    @staticmethod
    def create_from_json(json_data, registration_id: int):
        """Create a securities act object from a registration json schema object: map json to db."""
        securities_act = SecuritiesActNotice(securities_act_type=json_data.get('securitiesActNoticeType'),
                                             registration_id=registration_id)
        if json_data.get('effectiveDateTime'):
            securities_act.effective_ts = ts_from_iso_format(json_data.get('effectiveDateTime'))
        # if json_data.get('description'):
        #    securities_act.detail_description = str(json_data.get('description')).strip()
        if json_data.get('securitiesActOrders'):
            orders = []
            for order_json in json_data.get('securitiesActOrders'):
                securities_act_order: SecuritiesActOrder = SecuritiesActOrder.create_from_json(order_json,
                                                                                               registration_id,
                                                                                               securities_act.id)
                orders.append(securities_act_order)
            securities_act.securities_act_orders = orders
        return securities_act

    @staticmethod
    def create_from_statement_json(json_data, registration_id: int):
        """Create a list of new notice objects from an amendment statement json schema object: map json to db."""
        if not json_data.get('addSecuritiesActNotices'):
            return None
        notices = []
        for notice_json in json_data.get('addSecuritiesActNotices'):
            notice = SecuritiesActNotice.create_from_json(notice_json, registration_id)
            if notice_json.get('amendNoticeId'):
                notice.previous_notice_id = notice_json.get('amendNoticeId')
            notices.append(notice)
        return notices
