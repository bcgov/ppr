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
"""Common setup and fixtures for the pytest suite used by this service."""
import datetime
from contextlib import contextmanager

import pytest

from ppr_api import create_app
from ppr_api import jwt as _jwt
from ppr_api.models import db as _db

from . import FROZEN_DATETIME


@contextmanager
def not_raises(exception):
    """Corallary to the pytest raises builtin.

    Assures that an exception is NOT thrown.
    """
    try:
        yield
    except AttributeError:
        print('Test rolled back')
    except exception:
        raise pytest.fail(f"DID RAISE {exception}")  # pylint: disable=raise-missing-from


# fixture to freeze utcnow to a fixed date-time
@pytest.fixture
def freeze_datetime_utcnow(monkeypatch):
    """Fixture to return a static time for utcnow()."""

    class _Datetime:
        @classmethod
        def utcnow(cls):
            """UTC NOW"""
            return FROZEN_DATETIME

    monkeypatch.setattr(datetime, "datetime", _Datetime)


@pytest.fixture(scope="session")
def app():
    """Return a session-wide application configured in TEST mode."""
    _app = create_app("unitTesting")

    with _app.app_context():
        yield _app


@pytest.fixture(scope="function")
def client(app):  # pylint: disable=redefined-outer-name
    """Return a session-wide Flask test client."""
    return app.test_client()


@pytest.fixture(scope="session")
def jwt():
    """Return a session-wide jwt manager."""
    return _jwt


@pytest.fixture(scope="session")
def db(app, request):  # pylint: disable=redefined-outer-name
    """Session-wide test database."""

    #    def teardown():
    #        _db.drop_all()

    #    _db.app = app

    #    _db.create_all()
    #    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope="function")
def session(db, request):  # pylint: disable=redefined-outer-name
    """Return a function-scoped session."""
    db.session.begin_nested()

    def commit():
        db.session.flush()
        db.session.expire_all()

    # patch commit method
    old_commit = db.session.commit
    db.session.commit = commit

    def teardown():
        db.session.rollback()
        db.session.close()
        db.session.commit = old_commit

    request.addfinalizer(teardown)
    return db.session
