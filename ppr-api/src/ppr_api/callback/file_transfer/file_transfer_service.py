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
"""This class transfers reports to a mail service for printing and mailing."""
from flask import current_app

from ppr_api.callback.utils.exceptions import FileTransferException
from ppr_api.models import utils as model_utils


class BCMailFileTransferService():
    """File transfer client for verification statement surface mail.

    Transfer individual verification statement reports to BC Mail+ for printing and mailing.
    """

    # File name format is: PPRVER.XXXXXXXXXXXXX.DD.MM.YYYY.PDF, statement key max length 13.
    VERIFICATION_FILENAME = 'PPRVER.{statement_key}.{day}.{month}.{year}.PDF'

    def __init__(self):
        """Initialize the file transfer client. Add ssh credentials."""
        self.mail_host = str(current_app.config.get('SURFACE_MAIL_HOST'))
        self.target_path = str(current_app.config.get('SURFACE_MAIL_TARGET_PATH'))

    def transfer_verification_statement(self, binary_data, registration_id, party_id):
        """Publish the search report request json payload to the Queue Service."""
        try:
            filename = self.get_filename(registration_id, party_id)
            self.transfer_file(binary_data, filename)
        except FileTransferException as ft_err:
            raise ft_err
        except Exception as err:  # pylint: disable=broad-except # noqa F841;
            msg = 'Transfer verification statement failed: ' + repr(err)
            current_app.logger.error(msg)
            raise FileTransferException(msg)

    def transfer_file(self, binary_data, file_name: str):
        """Transfer the binary_data to the folder saving as the file name."""
        msg = f'Transferring data to host {self.mail_host}, path={self.target_path}, filename={file_name}.'
        current_app.logger.info(msg)
        if not self.mail_host or self.mail_host.strip() == '':
            raise FileTransferException('No host configured to transfer files to.')

    def get_filename(self, registration_id, party_id):
        """Build a correctly formatted unique name."""
        reg_key = str(registration_id) + '.' + str(party_id)
        reg_key = reg_key[:13]
        today_local = model_utils.today_local()
        filename = self.VERIFICATION_FILENAME.format(statement_key=reg_key,
                                                     day=str(today_local.day),
                                                     month=str(today_local.month),
                                                     year=str(today_local.year))
        return filename
