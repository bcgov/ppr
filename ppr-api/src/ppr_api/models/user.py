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
"""This manages a User record that can be used in an audit trail.

Actual user data is kept in the OIDC and IDP services, this data is
here as a convenience for audit and db reporting.
"""
from flask import current_app

from ppr_api.exceptions import BusinessException
from ppr_api.models import utils as model_utils

from .db import db


class User(db.Model):
    """Used to hold the audit information for a User of this service."""

    __versioned__ = {}
    __tablename__ = 'users'

    id = db.Column(db.Integer, db.Sequence('user_id_seq'), primary_key=True)
    creation_date = db.Column(db.DateTime, nullable=False)
    username = db.Column(db.String(1000), index=True, nullable=False)
    sub = db.Column(db.String(36), unique=True, nullable=False)
    account_id = db.Column(db.String(20), nullable=True)
    firstname = db.Column(db.String(1000), nullable=True)
    lastname = db.Column(db.String(1000), nullable=True)
    email = db.Column(db.String(1024), nullable=True)
    iss = db.Column(db.String(1024), nullable=True)
    idp_userid = db.Column(db.String(256), index=True)
    login_source = db.Column(db.String(200), nullable=True)

    # Relationships - UserProfile
    user_profile = db.relationship('UserProfile', back_populates='user', uselist=False)

    @property
    def display_name(self):
        """Display name of user; do not show sensitive data like BCSC username.

        If there is actual name info, return that; otherwise username.
        """
        if self.firstname or self.lastname:
            return ' '.join([self.firstname, self.lastname]).strip()

        # parse off idir\ or @idir
        if self.username[:4] == 'idir':
            return self.username[5:]
        if self.username[-4:] == 'idir':
            return self.username[:-5]

        # do not show services card usernames
        if self.username[:4] == 'bcsc':
            return None

        return self.username if self.username else None

    @classmethod
    def find_by_id(cls, submitter_id: int = None):
        """Return a User if they exist and match the provided submitter id."""
        # return cls.query.filter_by(id=submitter_id).one_or_none()
        return db.session.query(User).filter(User.id == submitter_id).one_or_none()

    @classmethod
    def find_by_jwt_token(cls, token: dict, account_id: str = None):
        """Return a User if they exist and match the provided JWT."""
        current_app.logger.debug(f'Running query to look up user profile for account {account_id}.')
        return db.session.query(User).filter(User.idp_userid == token['idp_userid'] or
                                             User.sub == token['sub']).first()

    @classmethod
    def create_from_jwt_token(cls, token: dict, account_id: str = None):
        """Create a user record from the provided JWT token.

        Use the values found in the vaild JWT for the realm
        to populate the User audit data
        """
        if token:
            # TODO: schema doesn't parse from token need to figure that out ... LATER!
            # s = KeycloakUserSchema()
            # u = s.load(data=token, partial=True)
            firstname = token.get('given_name', None)
            if not firstname:
                firstname = token.get('firstname', None)
            lastname = token.get('family_name', None)
            if not lastname:
                lastname = token.get('lastname', None)
            user = User(
                username=token.get('username', None),
                firstname=firstname,
                lastname=lastname,
                iss=token['iss'],
                sub=token['sub'],
                account_id=account_id,
                idp_userid=token['idp_userid'],
                login_source=token['loginSource']
            )
            user.creation_date = model_utils.now_ts()
            current_app.logger.debug('Creating user from JWT:{}; User:{}'.format(token, user))
            db.session.add(user)
            db.session.commit()
            return user
        return None

    @classmethod
    def get_or_create_user_by_jwt(cls, jwt_oidc_token, account_id: str = None):
        """Return a valid user for audit tracking purposes."""
        # GET existing or CREATE new user based on the JWT info
        try:
            user = User.find_by_jwt_token(jwt_oidc_token)
            current_app.logger.debug(f'finding user: {jwt_oidc_token}')
            if not user:
                current_app.logger.debug(f'didnt find user, attempting to create new user:{jwt_oidc_token}')
                user = User.create_from_jwt_token(jwt_oidc_token, account_id)

            return user
        except Exception as err:  # noqa: B902; just logging and wrapping as BusinessException
            current_app.logger.error(err.with_traceback(None))
            raise BusinessException('unable_to_get_or_create_user',
                                    '{"code": "unable_to_get_or_create_user",'
                                    '"description": "Unable to get or create user from the JWT, ABORT"}'
                                    )

    @classmethod
    def find_by_username(cls, username):
        """Return the oldest User record for the provided username."""
        # return cls.query.filter_by(username=username).order_by(User.creation_date.desc()).first()
        return db.session.query(User).filter(User.username == username).order_by(User.creation_date.desc()).first()

    @classmethod
    def find_by_sub(cls, sub):
        """Return a User based on the unique sub field."""
        # return cls.query.filter_by(sub=sub).one_or_none()
        return db.session.query(User).filter(User.sub == sub).one_or_none()

    def save(self):
        """Store the User into the local cache."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Cannot delete User records."""
        return self
        # need to intercept the ORM and stop Users from being deleted
