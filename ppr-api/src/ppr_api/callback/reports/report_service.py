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
"""This class maintains the callback handler report generation."""
from flask import current_app

from ppr_api.reports import ReportTypes, get_callback_pdf
from ppr_api.services.payment.client import SBCPaymentClient
from ppr_api.models import SearchResult
from ppr_api.callback.utils.exceptions import ReportException, ReportDataException


def get_search_report(search_id: str):
    """Generate a search result report."""
    current_app.logger.info('Search report request id=' + search_id)
    search_detail = SearchResult.find_by_search_id(int(search_id), False)
    if search_detail is None:
        current_app.logger.info('No search report data found for id=' + search_id)
        raise ReportDataException('No search report data found for id=' + search_id)

    try:
        report_data = search_detail.json
        account_id = search_detail.search.account_id
        account_name = search_detail.account_name
        token = SBCPaymentClient.get_sa_token()
        return get_callback_pdf(report_data, account_id, ReportTypes.SEARCH_DETAIL_REPORT.value, token, account_name)
    except Exception as err:  # pylint: disable=broad-except # noqa F841;
        current_app.logger.error('Search report generation failed for id=' + search_id)
        current_app.logger.error(repr(err))
        raise ReportException('Search report generation failed for id=' + search_id)
