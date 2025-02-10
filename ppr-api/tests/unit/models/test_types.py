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

"""Tests to assure the PPR Type Table Models.

Test-Suite to ensure that the PPR Type Table Models are working as expected.
"""

from ppr_api.models import type_tables
from ppr_api.models.type_tables import RegistrationTypes

import pytest


# testdata pattern is ({reg_type}, {exists})
TEST_REG_TYPES = [
    ('XX', False),
    (RegistrationTypes.RL.value, True),
    (RegistrationTypes.DC.value, True),
    (RegistrationTypes.AM.value, True),
    (RegistrationTypes.SA.value, True),
    (RegistrationTypes.CL.value, True),
]


def test_registration_type_find_all(session):
    """Assert that RegistrationType.find_all() contains all expected elements."""
    results = type_tables.RegistrationType.find_all()
    assert results
    assert len(results) > 60
    for result in results:
        assert result.registration_type in RegistrationTypes
        assert result.registration_desc
        assert result.registration_type_cl
        assert result.registration_act


@pytest.mark.parametrize('reg_type, exists', TEST_REG_TYPES)
def test_registration_type_find(session, reg_type, exists):
    """Assert that RegistrationType.find_by_registration_type() works as expected."""
    reg_result = type_tables.RegistrationType.find_by_registration_type(reg_type)
    if exists:
        assert reg_result
        assert reg_result.registration_type == reg_type
    else:
        assert not reg_result
