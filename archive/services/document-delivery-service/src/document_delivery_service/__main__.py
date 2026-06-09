# Copyright © 2021 Province of British Columbia
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
"""This runs the service."""
from __future__ import annotations

from dotenv import find_dotenv, load_dotenv
from service_runner import run

from document_delivery_service.service import doc_service_callback

load_dotenv(find_dotenv())


if __name__ == '__main__':
    run(doc_service_callback)
