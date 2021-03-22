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
"""This module holds model definitions for the PPR type tables."""

from __future__ import annotations

from .db import db


class RegistrationType(db.Model):  # pylint: disable=too-few-public-methods
    """This class defines the model for the registration_type table."""

    __tablename__ = 'registration_type'

    registration_type_cd = db.Column('registration_type_cd', db.String(2), primary_key=True)
    registration_type_cl = db.Column('registration_type_cl', db.String(10), nullable=False)
    registration_desc = db.Column('registration_desc', db.String(100), nullable=False)
    registration_act = db.Column('registration_act', db.String(60), nullable=False)

    # parent keys

    # Relationships - Registration
    registration = db.relationship('Registration', back_populates='registration_type')
