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
"""Exceptions defined for the Queue Service."""


class ReportException(Exception):
    """Exception for queue event listener report generation."""


class ReportDataException(Exception):
    """No data found for report exception."""


class QueueException(Exception):
    """Base exception for the Queue Services."""


class TokenException(Exception):
    """Exception obtaining token for a queue related service."""


class StorageException(Exception):
    """Exception for queue event listener storage related errors."""


class EmailException(Exception):
    """No email processor to match queue payload."""


class FileTransferException(Exception):
    """Base exception for the file transfer Services."""
