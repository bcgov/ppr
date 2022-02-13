# Copyright © 2022 Province of British Columbia
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
"""Tests to assure the Flag Services.

Test-Suite to ensure that the Flag Service is working as expected.
"""
import os

import pytest
from flask import Flask

from ppr_api.models import User
from ppr_api.services import Flags

from tests import integration_ldarkly


@integration_ldarkly
@pytest.mark.parametrize('test_name,flag_name,expected', [
    ('ppr-test-boolean', 'ppr-test-boolean', True),
    ('ppr-test-number', 'ppr-test-number', 10),
])
def test_flags_bool_value(test_name, flag_name, expected):
    """Assert that a boolean (True) is returned, when using the local Flag.json file.
    
    This requires the flags.json file at the root of the project.
    """
    app = Flask(__name__)
    app.env = 'production'
    app.config['LD_SDK_KEY'] = os.getenv('LD_SDK_KEY')
    flags = Flags()
    flags.init_app(app)

    with app.app_context():
        val = flags.value(flag_name)

    assert val == expected

@integration_ldarkly
@pytest.mark.parametrize('test_name,flag_user,expected_bool,expected_val', [
    ('valid-user',
     User(username='bcregistries.devops@daxiom.ca', firstname='bcregistries', lastname='test', sub='bcregistries-test', iss='iss'),
     True, 10),
    ('invalid-user',
     (User(username='bcregistries', firstname='x', lastname='y', sub='bcregistries', iss='iss')),
     False, -1),
])
def test_flag_unique_user(test_name, flag_user, expected_bool, expected_val):
    """Assert that a unique user can retrieve a flag, when using the local Flag.json file."""
    app = Flask(__name__)
    app.env = 'production'
    app.config['LD_SDK_KEY'] = os.getenv('LD_SDK_KEY')

    app_env = app.env
    try:
        with app.app_context():
            flags = Flags()
            flags.init_app(app)
            val = flags.value('ppr-test-number', flag_user)
            flag_on = flags.is_on('ppr-test-boolean', flag_user)

        assert val == expected_val
        assert flag_on == expected_bool
    except:  # pylint: disable=bare-except; # noqa: B901, E722
        # for tests we don't care
        assert False
    finally:
        app.env = app_env