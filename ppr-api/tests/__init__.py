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
"""The Test Suites to ensure that the service is built and operating correctly."""
from collections import MutableMapping, MutableSequence
from typing import Dict, List

from .pytest_marks import (
    integration_authorization,
    integration_nats,
    integration_payment,
    integration_sentry,
    not_github_ci,
)


def strip_keys_from_dict(orig_dict: Dict, keys: List) -> Dict:
    """Return a deep copy of the dict with the keys stripped out."""
    def del_key_in_dict(orig_dict, keys):
        """Remove keys from dictionaires."""
        modified_dict = {}
        for key, value in orig_dict.items():
            if key not in keys:
                if isinstance(value, MutableMapping):  # or
                    modified_dict[key] = del_key_in_dict(value, keys)
                elif isinstance(value, MutableSequence):
                    if rv := scan_list(value, keys):
                        modified_dict[key] = rv
                else:
                    modified_dict[key] = value  # or copy.deepcopy(value) if a copy is desired for non-dicts.
        return modified_dict

    def scan_list(orig_list, keys):
        """Remove keys from lists."""
        modified_list = []
        for item in orig_list:
            if isinstance(item, MutableMapping):
                if rv := del_key_in_dict(item, keys):
                    modified_list.append(rv)
            elif isinstance(item, MutableSequence):
                if rv := scan_list(item, keys):
                    modified_list.append(rv)
            else:
                try:
                    if item not in keys:
                        modified_list.append(item)
                except:  # noqa: E722
                    modified_list.append(item)
        return modified_list

    key_set = set(keys)
    return del_key_in_dict(orig_dict, key_set)
