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
"""This module wraps the calls to external services used by the API."""

from .authz import BASIC_USER, MHR_ROLE, STAFF_ROLE, SYSTEM_ROLE, authorized, is_staff
from .document_storage.storage_service import GoogleStorageService
from .gcp_auth.auth_service import GoogleAuthService
from .queue_service import GoogleQueueService

auth_service = GoogleAuthService()
queue_service = GoogleQueueService()
storage_service = GoogleStorageService()
