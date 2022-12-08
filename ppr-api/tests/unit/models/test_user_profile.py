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

"""Tests to assure the User and UserProfile Model.

Test-Suite to ensure that the User and User Profile Models are working as expected.
"""
import pytest

from ppr_api.models import User, UserProfile


# Properties can be anything, using show* for testing.
REGISTRATIONS_TABLE = {
    'showColumn1': True,
    'showColumn2': False,
    'showColumn3': True,
    'showColumn4': False
}
UPDATED_REGISTRATIONS_TABLE = {
    'showColumn1': False,
    'showColumn2': True,
    'showColumn3': False,
    'showColumn4': True
}
# Properties can be anything, using misc* for testing.
MISC_PREFERENCES = {
    'preference1': 'A',
    'preference2': False,
    'preference3': 3
}
UPDATED_MISC_PREFERENCES = {
    'preference1': 'B',
    'preference2': True,
    'preference3': 10
}

ALL_JSON = {
    'paymentConfirmationDialog': True,
    'selectConfirmationDialog': False,
    'defaultDropDowns': True,
    'defaultTableFilters': True,
    'registrationsTable': REGISTRATIONS_TABLE,
    'miscellaneousPreferences': MISC_PREFERENCES
}
PAYMENT_JSON = {
    'paymentConfirmationDialog': True
}
SELECT_JSON = {
    'selectConfirmationDialog': False
}
COMBO_JSON = {
    'paymentConfirmationDialog': True,
    'selectConfirmationDialog': False,
    'registrationsTable': UPDATED_REGISTRATIONS_TABLE,
    'miscellaneousPreferences': UPDATED_MISC_PREFERENCES
}

TOKEN1 = {
    'username': 'username',
    'given_name': 'given_name',
    'family_name': 'family_name',
    'iss': 'issuer',
    'sub': 'subject',
    'idp_userid': 'idp_userid',
    'loginSource': 'source'
}
TOKEN2 = {
    'username': 'username',
    'firstname': 'given_name',
    'lastname': 'family_name',
    'iss': 'issuer',
    'sub': 'subject',
    'idp_userid': 'idp_userid',
    'loginSource': 'source'
}
TEST_TOKEN = {
    'username': 'username_TEST1',
    'firstname': 'given_name_TEST1',
    'lastname': 'family_name_TEST1',
    'iss': 'issuer_TEST1',
    'sub': 'subject_TEST1',
    'idp_userid': 'idp_userid_TEST1',
    'loginSource': 'source_TEST1'
}

TEST_VALID_DATA = [
    (ALL_JSON),
    (PAYMENT_JSON),
    (SELECT_JSON),
    (COMBO_JSON)
]

TEST_TOKEN_DATA = [
    (TOKEN1),
    (TOKEN2)
]


@pytest.mark.parametrize('json_data', TEST_VALID_DATA)
def test_create_from_json(session, client, jwt, json_data):
    """Assert that creating a UserProfile object from JSON works as expected."""
    profile = UserProfile.create_from_json(json_data, 12343)
    assert profile
    assert profile.payment_confirmation
    assert profile.search_selection_confirmation
    assert profile.default_table_filters
    assert profile.default_drop_downs
    if 'registrationsTable' in json_data:
        assert 'showColumn1' in profile.registrations_table
        assert 'showColumn2' in profile.registrations_table
        assert 'showColumn3' in profile.registrations_table
        assert 'showColumn4' in profile.registrations_table
    if 'miscellaneousPreferences' in json_data:
        assert 'preference1' in profile.misc_preferences
        assert 'preference2' in profile.misc_preferences
        assert 'preference3' in profile.misc_preferences


@pytest.mark.parametrize('token', TEST_TOKEN_DATA)
def test_jwt_properties(session, client, jwt, token):
    """Assert that user jwt properties are as expected."""
    assert jwt
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
        idp_userid=token['idp_userid'],
        login_source=token['loginSource']
    )
    assert user.username == 'username'
    assert user.iss == 'issuer'
    assert user.sub == 'subject'
    assert user.firstname == 'given_name'
    assert user.lastname == 'family_name'
    assert user.idp_userid == 'idp_userid'
    assert user.login_source == 'login_source'


def test_find_by_id(session, client, jwt):
    """Assert that user find by id is working as expected."""
    user = User.find_by_id(1)
    if not user:
        user2 = User.create_from_jwt_token(TEST_TOKEN, 'PS12345')
        user = User.find_by_id(user2.id)

    assert user
    assert user.id
    assert user.username == 'username_TEST1'
    assert user.iss == 'issuer_TEST1'
    assert user.sub == 'subject_TEST1'
    assert user.firstname == 'given_name_TEST1'
    assert user.lastname == 'family_name_TEST1'
    assert user.idp_userid == 'idp_userid_TEST1'
    assert user.login_source == 'source_TEST1'

def test_find_by_jwt_token(session, client, jwt):
    """Assert that user find by jwt token is working as expected."""
    user = User.find_by_jwt_token(TEST_TOKEN)
    if not user:
        User.create_from_jwt_token(TEST_TOKEN, 'PS12345')
        user = User.find_by_jwt_token(TEST_TOKEN)

    assert user
    assert user.id
    assert user.username == 'username_TEST1'
    assert user.iss == 'issuer_TEST1'
    assert user.sub == 'subject_TEST1'
    assert user.firstname == 'given_name_TEST1'
    assert user.lastname == 'family_name_TEST1'
    assert user.idp_userid == 'idp_userid_TEST1'
    assert user.login_source == 'source_TEST1'

def test_find_by_username(session, client, jwt):
    """Assert that user find by username is working as expected."""
    user = User.find_by_username(TEST_TOKEN['username'])
    if not user:
        User.create_from_jwt_token(TEST_TOKEN, 'PS12345')
        user = User.find_by_username(TEST_TOKEN['username'])

    assert user
    assert user.id
    assert user.username == 'username_TEST1'
    assert user.iss == 'issuer_TEST1'
    assert user.sub == 'subject_TEST1'
    assert user.firstname == 'given_name_TEST1'
    assert user.lastname == 'family_name_TEST1'
    assert user.idp_userid == 'idp_userid_TEST1'
    assert user.login_source == 'source_TEST1'

def test_find_by_subject(session, client, jwt):
    """Assert that user find by subject is working as expected."""
    user = User.find_by_sub(TEST_TOKEN['sub'])
    if not user:
        User.create_from_jwt_token(TEST_TOKEN, 'PS12345')
        user = User.find_by_sub(TEST_TOKEN['sub'])

    assert user
    assert user.id
    assert user.username == 'username_TEST1'
    assert user.iss == 'issuer_TEST1'
    assert user.sub == 'subject_TEST1'
    assert user.firstname == 'given_name_TEST1'
    assert user.lastname == 'family_name_TEST1'
    assert user.idp_userid == 'idp_userid_TEST1'
    assert user.login_source == 'source_TEST1'

def test_get_or_create(session, client, jwt):
    """Assert that get or create user is working as expected."""
    user = User.get_or_create_user_by_jwt(TEST_TOKEN, 'PS12345')

    assert user
    assert user.id
    assert user.username == 'username_TEST1'
    assert user.iss == 'issuer_TEST1'
    assert user.sub == 'subject_TEST1'
    assert user.firstname == 'given_name_TEST1'
    assert user.lastname == 'family_name_TEST1'
    assert user.idp_userid == 'idp_userid_TEST1'
    assert user.login_source == 'source_TEST1'

def test_create_user_profile(session, client, jwt):
    """Assert that creating a user profile is working as expected."""
    user = User.find_by_jwt_token(TEST_TOKEN)
    if not user:
        user = User.create_from_jwt_token(TEST_TOKEN, 'PS12345')

    user_profile = UserProfile.create_from_json(ALL_JSON, user.id)
    user_profile.save()
    save_json = user_profile.json
    assert save_json['paymentConfirmationDialog'] == ALL_JSON['paymentConfirmationDialog']
    assert save_json['selectConfirmationDialog'] == ALL_JSON['selectConfirmationDialog']
    assert save_json['defaultDropDowns'] == ALL_JSON['defaultDropDowns']
    assert save_json['defaultTableFilters'] == ALL_JSON['defaultTableFilters']
    assert save_json['registrationsTable'] == ALL_JSON['registrationsTable']
    assert save_json['miscellaneousPreferences'] == ALL_JSON['miscellaneousPreferences']


def test_update_user_profile(session, client, jwt):
    """Assert that updating a user profile is working as expected."""
    user = User.find_by_jwt_token(TEST_TOKEN)
    if not user:
        user = User.create_from_jwt_token(TEST_TOKEN, 'PS12345')
        user.user_profile = UserProfile.create_from_json(ALL_JSON, user.id)

    user_profile = user.user_profile
    user_profile.update_profile(COMBO_JSON)
    save_json = user_profile.json
    assert save_json['paymentConfirmationDialog'] == COMBO_JSON['paymentConfirmationDialog']
    assert save_json['selectConfirmationDialog'] == COMBO_JSON['selectConfirmationDialog']
    assert save_json['registrationsTable'] == COMBO_JSON['registrationsTable']
    assert save_json['miscellaneousPreferences'] == COMBO_JSON['miscellaneousPreferences']
