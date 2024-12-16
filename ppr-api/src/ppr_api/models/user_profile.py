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
"""This module holds model data and database operations for user UI preferences."""

from __future__ import annotations

from http import HTTPStatus

from ppr_api.exceptions import BusinessException
from ppr_api.utils.logging import logger

from .db import db

# Mapping from boolean to db value.
BOOLEAN_TO_DB_VALUE = {True: "Y", False: "N"}


class UserProfile(db.Model):
    """This class maintains user profile UI settings."""

    __tablename__ = "user_profiles"

    id = db.mapped_column(db.Integer, db.ForeignKey("users.id"), primary_key=True, nullable=False)
    payment_confirmation = db.mapped_column(db.String(1), nullable=False)
    search_selection_confirmation = db.mapped_column(db.String(1), nullable=False)
    default_drop_downs = db.mapped_column(db.String(1), nullable=False)
    default_table_filters = db.mapped_column(db.String(1), nullable=False)
    # user account my registrations table preferences: UI can pass whatever settings it wants; API stores as is.
    registrations_table = db.mapped_column("registrations_table", db.JSON, nullable=True)
    # Additional user account miscellaneous preferences: UI can pass whatever settings it wants; API stores as is.
    misc_preferences = db.mapped_column("misc_preferences", db.JSON, nullable=True)
    # Initially stored MHR service agreement required/accepted for qualified suppliers. Read only, set by the MHR API.
    service_agreements = db.mapped_column("service_agreements", db.JSON, nullable=True)

    # parent keys

    # Relationships - User
    user = db.relationship(
        "User", foreign_keys=[id], back_populates="user_profile", cascade="all, delete", uselist=False
    )

    @property
    def json(self) -> dict:
        """Return the user profile as a json object."""
        profile = {
            "paymentConfirmationDialog": bool(self.payment_confirmation == "Y"),
            "selectConfirmationDialog": bool(self.search_selection_confirmation == "Y"),
            "defaultDropDowns": bool(self.default_drop_downs == "Y"),
            "defaultTableFilters": bool(self.default_table_filters == "Y"),
        }
        if self.registrations_table:
            profile["registrationsTable"] = self.registrations_table
        if self.misc_preferences:
            profile["miscellaneousPreferences"] = self.misc_preferences
        return profile

    def save(self):
        """Render a user profile to the local cache."""
        try:
            db.session.add(self)
            db.session.commit()
            logger.debug("Created/updated user profile: {}".format(self.json))
        except Exception as db_exception:  # noqa: B902; just logging and wrapping
            logger.error("DB user_profile save exception: " + repr(db_exception))
            raise BusinessException(
                error="Database user_profile save failed: " + repr(db_exception),
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            ) from db_exception

    def update_profile(self, profile_json):
        """Update one or more user profile settings from the provided json."""
        if not profile_json:
            return

        if "paymentConfirmationDialog" in profile_json:
            self.payment_confirmation = BOOLEAN_TO_DB_VALUE[profile_json["paymentConfirmationDialog"]]
        if "selectConfirmationDialog" in profile_json:
            self.search_selection_confirmation = BOOLEAN_TO_DB_VALUE[profile_json["selectConfirmationDialog"]]
        if "defaultDropDowns" in profile_json:
            self.default_drop_downs = BOOLEAN_TO_DB_VALUE[profile_json["defaultDropDowns"]]
        if "defaultTableFilters" in profile_json:
            self.default_table_filters = BOOLEAN_TO_DB_VALUE[profile_json["defaultTableFilters"]]
        if "registrationsTable" in profile_json:
            self.registrations_table = profile_json["registrationsTable"]
        if "miscellaneousPreferences" in profile_json:
            self.misc_preferences = profile_json["miscellaneousPreferences"]

        logger.debug("Updating username " + self.user.username + " profile  to {}".format(self.json))
        self.save()

    @classmethod
    def find_by_id(cls, profile_id: int):
        """Return the user profile record matching the id."""
        user_profile = None
        if profile_id:
            # user_profile = cls.query.filter(UserProfile.id == profile_id).one_or_none()
            user_profile = db.session.query(UserProfile).filter(UserProfile.id == profile_id).one_or_none()

        return user_profile

    @staticmethod
    def create_from_json(profile_json, user_id: int):
        """Create a user profile object from dict/json specifying the user UI preferences."""
        user_profile = UserProfile(id=user_id)
        if profile_json is None:
            user_profile.payment_confirmation = "Y"
            user_profile.search_selection_confirmation = "Y"
            user_profile.default_drop_downs = "Y"
            user_profile.default_table_filters = "Y"
            return user_profile

        if "paymentConfirmationDialog" in profile_json and profile_json["paymentConfirmationDialog"]:
            user_profile.payment_confirmation = "Y"
        else:
            user_profile.payment_confirmation = "N"
        if "selectConfirmationDialog" in profile_json and profile_json["selectConfirmationDialog"]:
            user_profile.search_selection_confirmation = "Y"
        else:
            user_profile.search_selection_confirmation = "N"
        if "defaultDropDowns" in profile_json and profile_json["defaultDropDowns"]:
            user_profile.default_drop_downs = "Y"
        else:
            user_profile.default_drop_downs = "N"
        if "defaultTableFilters" in profile_json and profile_json["defaultTableFilters"]:
            user_profile.default_table_filters = "Y"
        else:
            user_profile.default_table_filters = "N"
        if "registrationsTable" in profile_json:
            user_profile.registrations_table = profile_json["registrationsTable"]
        if "miscellaneousPreferences" in profile_json:
            user_profile.misc_preferences = profile_json["miscellaneousPreferences"]
        return user_profile
