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
"""This module holds data for Securities Act registration and amendment court/commission order information."""
from .utils import format_ts, ts_from_date_iso_format
from .db import db


class SecuritiesActOrder(db.Model):
    """This class manages the Securities Act registration and amendment court/commission order information."""

    __tablename__ = 'securities_act_orders'

    id = db.mapped_column('id', db.Integer, db.Sequence('securities_act_order_id_seq'), primary_key=True)
    court_order_ind = db.mapped_column('court_order_ind', db.String(1), nullable=False)
    order_date = db.mapped_column('order_date', db.DateTime, nullable=True)
    court_name = db.mapped_column('court_name', db.String(256), nullable=True)
    court_registry = db.mapped_column('court_registry', db.String(64), nullable=True)
    file_number = db.mapped_column('file_number', db.String(20), nullable=True)
    effect_of_order = db.mapped_column('effect_of_order', db.String(512), nullable=True)
    registration_id_end = db.mapped_column('registration_id_end', db.Integer, nullable=True, index=True)

    # parent keys
    registration_id = db.mapped_column('registration_id', db.Integer,
                                       db.ForeignKey('registrations.id'),
                                       nullable=False,
                                       index=True)

    securities_act_notice_id = db.mapped_column('securities_act_notice_id', db.Integer,
                                                db.ForeignKey('securities_act_notices.id'),
                                                nullable=False,
                                                index=True)

    # Relationships - Registration
    securities_act_notice = db.relationship('SecuritiesActNotice', foreign_keys=[securities_act_notice_id],
                                            back_populates='securities_act_orders',
                                            cascade='all, delete', uselist=False)

    @property
    def json(self) -> dict:
        """Return the court_order as a json object."""
        order = {
            'courtOrder': self.court_order_ind == 'Y'
        }
        if self.court_name:
            order['courtName'] = self.court_name
        if self.court_registry:
            order['courtRegistry'] = self.court_registry
        if self.file_number:
            order['fileNumber'] = self.file_number
        if self.order_date:
            order['orderDate'] = format_ts(self.order_date)
        if self.effect_of_order:
            order['effectOfOrder'] = self.effect_of_order
        return order

    @classmethod
    def find_by_id(cls, order_id: int = None):
        """Return an Securities Act Order object by order ID."""
        order = None
        if order_id:
            order = db.session.query(SecuritiesActOrder).filter(SecuritiesActOrder.id == order_id).one_or_none()
        return order

    @classmethod
    def find_by_notice_id(cls, notice_id: int = None):
        """Return a list of Securities Act Order objects by notice ID."""
        orders = None
        if notice_id:
            orders = db.session.query(SecuritiesActOrder) \
                               .filter(SecuritiesActOrder.securities_act_notice_id == notice_id) \
                               .order_by(SecuritiesActOrder.id).all()
        return orders

    @staticmethod
    def create_from_json(json_data, registration_id: int, notice_id: int):
        """Create a Securities Act court/commission order object from a json schema object: map json to db."""
        order: SecuritiesActOrder = SecuritiesActOrder(registration_id=registration_id,
                                                       securities_act_notice_id=notice_id,
                                                       court_order_ind='Y')
        if not json_data.get('courtOrder'):
            order.court_order_ind = 'N'
        if json_data.get('courtName'):
            order.court_name = json_data['courtName']
        if json_data.get('courtRegistry'):
            order.court_registry = json_data['courtRegistry']
        if json_data.get('fileNumber'):
            order.file_number = json_data['fileNumber']
        if json_data.get('orderDate'):
            order.order_date = ts_from_date_iso_format(json_data['orderDate'])
        if json_data.get('effectOfOrder'):
            order.effect_of_order = json_data['effectOfOrder']

        return order
