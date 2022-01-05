# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""File Transfer Service tests."""
import pytest
from flask import current_app

from ppr_api.callback.utils.exceptions import FileTransferException
from ppr_api.callback.file_transfer.file_transfer_service import BCMailFileTransferService
from ppr_api.models import utils as model_utils


def test_properties(session):
    """Assert that loading environent properties works as expected."""
    service: BCMailFileTransferService = BCMailFileTransferService()
    assert service.mail_host == str(current_app.config.get('SURFACE_MAIL_HOST'))
    assert service.target_path == str(current_app.config.get('SURFACE_MAIL_TARGET_PATH'))


def test_filename(session):
    """Assert that building a file transfer filename works as expected."""
    test_name = 'PPRVER.999999.111111.{day}.{month}.{year}.PDF'
    today_local = model_utils.today_local()
    test_name = test_name.format(day=str(today_local.day), month=str(today_local.month), year=str(today_local.year))
    # current_app.logger.info('Test name=' + test_name)
    service: BCMailFileTransferService = BCMailFileTransferService()

    filename = service.get_filename(999999, 111111)
    assert test_name == filename
    assert len(filename) <= 35


def test_file_transfer(session):
    """Assert that a dev attempt to transfer file data throws a FileTransferException."""
    raw_data = None

    with pytest.raises(FileTransferException) as transfer_err:
        BCMailFileTransferService().transfer_verification_statement(raw_data, 9999999, 1111111)

    # check
    assert transfer_err
