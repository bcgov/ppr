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
