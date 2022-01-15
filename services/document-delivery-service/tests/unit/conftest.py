import datetime
import time
from contextlib import contextmanager, suppress

import pytest

from service_http import create_app


@contextmanager
def not_raises(exception):
    """Corallary to the pytest raises builtin.
    Assures that an exception is NOT thrown.
    """
    try:
        yield
    except exception:
        raise pytest.fail(f'DID RAISE {exception}')


# fixture to freeze utcnow to a fixed date-time
@pytest.fixture
def freeze_datetime_utcnow(monkeypatch):
    """Fixture to return a static time for utcnow()."""
    class _Datetime:
        @classmethod
        def utcnow(cls):
            return FROZEN_DATETIME

    monkeypatch.setattr(datetime, 'datetime', _Datetime)


@pytest.fixture(scope='session')
def app():
    """Return a session-wide application configured in TEST mode."""
    _app = create_app('testing')

    return _app


@pytest.fixture(scope='session')
def client(app):  # pylint: disable=redefined-outer-name
    """Return a session-wide Flask test client."""
    return app.test_client()

@pytest.fixture(scope='session', autouse=True)
def auto(docker_services, app):  # pylint: disable=redefined-outer-name
    """Spin up docker instances."""
    docker_services.start('sftp')
    time.sleep(2)


@pytest.fixture(scope='session')
def docker_compose_files(pytestconfig):
    """Get the docker-compose.yml absolute path."""
    import os  # pylint: disable=import-outside-toplevel
    return [
        os.path.join(str(pytestconfig.rootdir), 'tests/unit/docker', 'docker-compose.yml')
    ]
