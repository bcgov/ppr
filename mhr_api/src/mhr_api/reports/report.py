# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
"""Produces a PDF output based on templates and JSON messages."""
import base64
import json
from datetime import timedelta
from http import HTTPStatus
from pathlib import Path

import pycountry
import requests
from flask import current_app, jsonify

from mhr_api.exceptions import ResourceErrorCodes
from mhr_api.models import utils as model_utils
from mhr_api.reports import ppr_report_utils
from mhr_api.utils.auth import jwt
from mhr_api.utils.base import BaseEnum


# Map from API search type to report description
TO_SEARCH_DESCRIPTION = {
    'OWNER_NAME': 'Owner Name',
    'ORGANIZATION_NAME': 'Organization Name',
    'MHR_NUMBER': 'MHR Number',
    'SERIAL_NUMBER': 'Serial Number'
}
TO_NOTE_DESCRIPTION = {
    '101': 'Register New Unit',
    '102': 'Decal Replacement',
    '103': 'Transport Permit',
    '103E': 'Extend Tran Permit',
    'CAU': 'Caution',
    'CAUC': 'Continue Caution',
    'CAUE': 'Extend Caution',
    'EXNR': 'Non-Res. Exemption',
    'EXRS': 'Res. Exemption',
    'FZE': 'Registrars Freeze',
    'NCON': 'Confidential Note',
    'NPUB': 'Public Note',
    'REGC': 'Reg. Correction',
    'REST': 'Restraining Order',
    'STAT': 'Dec./Illegal Move',
    'TAXN': 'Tax Sale Notice'
}


class ReportTypes(BaseEnum):
    """Render an Enum of the PPR PDF report types."""

    SEARCH_DETAIL_REPORT = 'searchDetail'


class Report:  # pylint: disable=too-few-public-methods
    """Service to create report outputs."""

    def __init__(self, report_data, account_id, report_type=None, account_name=None):
        """Create the Report instance."""
        self._report_data = report_data
        self._report_key = report_type
        self._account_id = account_id
        self._account_name = account_name

    def get_payload_data(self):
        """Generate report data including template data for report api call."""
        return self._setup_report_data()

    def get_pdf(self, report_type=None, token=None):
        """Render a pdf for the report type and report data."""
        if report_type:
            self._report_key = report_type
        headers = {
            'Content-Type': 'application/json'
        }
        if token is not None:
            headers['Authorization'] = 'Bearer {}'.format(token)
        else:
            headers['Authorization'] = 'Bearer {}'.format(jwt.get_token_auth_header())
        current_app.logger.debug('Account {0} report type {1} setting up report data.'
                                 .format(self._account_id, self._report_key))
        data = self._setup_report_data()
        url = current_app.config.get('REPORT_SVC_URL')
        current_app.logger.debug('Account {0} report type {1} calling report-api {2}.'
                                 .format(self._account_id, self._report_key, url))
        response = requests.post(url=url, headers=headers, data=json.dumps(data))
        current_app.logger.debug('Account {0} report type {1} response status: {2}.'
                                 .format(self._account_id, self._report_key, response.status_code))

        if response.status_code != HTTPStatus.OK:
            content = ResourceErrorCodes.REPORT_ERR + ': ' + response.content.decode('ascii')
            current_app.logger.error('Account {0} response status: {1} error: {2}.'
                                     .format(self._account_id, response.status_code, content))
            return jsonify(message=content), response.status_code, None
        return response.content, response.status_code, {'Content-Type': 'application/pdf'}

    def _setup_report_data(self):
        """Set up the report service request data."""
        # current_app.logger.debug('Setup report data template starting.')
        template = base64.b64encode(bytes(self._get_template(), 'utf-8')).decode() + "'"
        current_app.logger.debug('Setup report data template completed, setup data starting.')
        data = {
            'reportName': self._get_report_filename(),
            'template': template,
            'templateVars': self._get_template_data()
        }
        current_app.logger.debug('Setup report data completed.')
        return data

    def _get_report_filename(self):
        """Generate the pdf filename from the report type and report data."""
        report_date = self._get_report_date()
        report_id = self._get_report_id()
        description = ReportMeta.reports[self._report_key]['reportDescription']
        return '{}_{}_{}.pdf'.format(report_id, report_date, description).replace(' ', '_')

    def _get_report_date(self):
        """Get the report date for the filename from the report data."""
        if self._report_key == ReportTypes.SEARCH_DETAIL_REPORT:
            return self._report_data['searchDateTime']

        return self._report_data['createDateTime']

    def _get_report_id(self):
        """Get the report transaction ID for the filename from the report data."""
        report_id = ''
        if self._report_key == ReportTypes.SEARCH_DETAIL_REPORT and 'payment' in self._report_data:
            report_id = self._report_data['payment']['invoiceId']

        return report_id

    def _get_template(self):
        """Load from the local file system the template matching the report type."""
        try:
            template_path = current_app.config.get('REPORT_TEMPLATE_PATH')
            template_code = Path(f'{template_path}/{self._get_template_filename()}').read_text()
            # substitute template parts
            template_code = self._substitute_template_parts(template_code)
        except Exception as err:  # noqa: B902; just logging
            current_app.logger.error(err)
            raise err
        return template_code

    @staticmethod
    def _substitute_template_parts(template_code):
        """Substitute template parts in main template.

        Template parts are marked by [[partname.html]] in templates.

        This functionality is restricted by:
        - markup must be exactly [[partname.html]] and have no extra spaces around file name
        - template parts can only be one level deep, ie: this rudimentary framework does not handle nested template
        parts. There is no recursive search and replace.

        :param template_code: string
        :return: template_code string, modified.
        """
        template_path = current_app.config.get('REPORT_TEMPLATE_PATH')
        template_parts = [
            'footer',
            'style',
            'stylePage',
            'stylePageDraft',
            'stylePageMail',
            'logo',
            'macros',
            'registrarSignature',
            'search-result/details',
            'search-result/location',
            'search-result/notes',
            'search-result/owners',
            'search-result/pprRegistrations',
            'search-result/selected',
            'search-result/sections',
            'search-result/registration',
            'search-result-ppr/financingStatement',
            'search-result-ppr/amendmentStatement',
            'search-result-ppr/changeStatement',
            'search-result-ppr/renewalStatement',
            'search-result-ppr/dischargeStatement',
            'search-result-ppr/securedParties',
            'search-result-ppr/courtOrderInformation',
            'search-result-ppr/debtors',
            'search-result-ppr/registeringParty',
            'search-result-ppr/vehicleCollateral',
            'search-result-ppr/generalCollateral'
        ]

        # substitute template parts - marked up by [[filename]]
        for template_part in template_parts:
            if template_code.find('[[{}.html]]'.format(template_part)) >= 0:
                template_part_code = Path(f'{template_path}/template-parts/{template_part}.html').read_text()
                for template_part_nested in template_parts:
                    template_reference = '[[{}.html]]'.format(template_part_nested)
                    if template_part_code.find(template_reference) >= 0:
                        path = Path(f'{template_path}/template-parts/{template_part_nested}.html')
                        template_nested_code = path.read_text()
                        template_part_code = template_part_code.replace(template_reference, template_nested_code)
                template_code = template_code.replace('[[{}.html]]'.format(template_part), template_part_code)

        return template_code

    def _get_template_filename(self):
        """Get the report template filename from the report type."""
        file_name = ReportMeta.reports[self._report_key]['fileName']
        return '{}.html'.format(file_name)

    def _get_template_data(self):
        """Get the data for the report, modifying the original for the template output."""
        self._set_meta_info()
        self._set_addresses()
        self._set_date_times()
        self._set_notes()
        if self._report_key == ReportTypes.SEARCH_DETAIL_REPORT:
            self._set_selected()
            # Add MHR search template setup here:
            self._set_ppr_search()
        return self._report_data

    def _set_ppr_search(self):  # pylint: disable=too-many-branches, too-many-statements
        """PPR search result setup for combined searches."""
        for detail in self._report_data['details']:
            if detail.get('pprRegistrations'):                
                for registration in detail['pprRegistrations']:
                    current_app.logger.debug('Setting up ppr registration for ' +
                                             registration['financingStatement']['baseRegistrationNumber'])
                    if 'registrationAct' in registration['financingStatement']:
                        act: str = registration['financingStatement']['registrationAct']
                        registration['financingStatement']['registrationAct'] = act.title() 
                    ppr_report_utils.set_ppr_template_data(registration['financingStatement'])

    def _set_notes(self):
        """Add note type descriptions and dates."""
        if self._report_key == ReportTypes.SEARCH_DETAIL_REPORT and self._report_data['totalResultsSize'] > 0:
            self._set_search_notes()

    def _set_search_notes(self):
        """Add search note document type description and dates."""
        if self._report_data and self._report_data['details']:
            for detail in self._report_data['details']:
                if detail.get('notes'):
                    for note in detail['notes']:
                        if note.get('documentType') and TO_NOTE_DESCRIPTION.get(note.get('documentType')):
                            note['documentDescription'] = TO_NOTE_DESCRIPTION.get(note.get('documentType'))
                        elif note.get('documentType'):
                            note['documentDescription'] = note.get('documentType')
                        else:
                            note['documentDescription'] = ''
                        if note.get('createDateTime'):
                            note['createDateTime'] = Report._to_report_datetime(note.get('createDateTime'))
                        if note.get('expiryDate') and note['expiryDate'] == '0001-01-01':
                            note['expiryDate'] = ''
                        elif note.get('expiryDate'):
                            note['expiryDate'] = Report._to_report_datetime(note['expiryDate'], False)

    def _set_addresses(self):
        """Replace address country code with description."""
        if self._report_key == ReportTypes.SEARCH_DETAIL_REPORT and self._report_data['totalResultsSize'] > 0:
            self._set_search_addresses()

    def _set_search_addresses(self):
        """Replace search results addresses country code with description."""
        if self._report_data and self._report_data['details']:
            for detail in self._report_data['details']:
                for owner in detail['owners']:
                    Report._format_address(owner['address'])
                if detail.get('location') and 'address' in detail['location']:
                    Report._format_address(detail['location']['address'])
                if detail.get('notes'):
                    for note in detail['notes']:
                        if note.get('contactAddress'):
                            Report._format_address(note['contactAddress'])

    def _set_date_times(self):
        """Replace API ISO UTC strings with local report format strings."""
        if self._report_key == ReportTypes.SEARCH_DETAIL_REPORT:
            self._report_data['searchDateTime'] = Report._to_report_datetime(self._report_data['searchDateTime'])
            if self._report_data['totalResultsSize'] > 0:
                for detail in self._report_data['details']:
                    detail['createDateTime'] = Report._to_report_datetime(detail['createDateTime'])
                    if detail.get('declaredDateTime'):
                        detail['declaredDateTime'] = Report._to_report_datetime(detail['declaredDateTime'], False)
                    declared_value = str(detail['declaredValue'])
                    if declared_value.isnumeric() and declared_value != '0':
                        detail['declaredValue'] = '$' + '{:0,.2f}'.format(float(declared_value))
                    else:
                        detail['declaredValue'] = ''
                    if detail.get('description') and 'engineerDate' in detail['description']:
                        if detail['description']['engineerDate'] == '0001-01-01':
                            detail['description']['engineerDate'] = ''
                        else:
                            detail['description']['engineerDate'] = \
                                Report._to_report_datetime(detail['description']['engineerDate'], False)

    def _set_selected(self):
        """Replace selection serial type code with description. Remove unselected items."""
        if 'selected' in self._report_data:
            for index, result in enumerate(self._report_data['selected'], start=0):
                result['createDateTime'] = Report._to_report_datetime(result['createDateTime'], False)
                result['index'] = (index + 1)
                if result.get('status'):
                    result['status'] = str(result['status']).capitalize()
            self._report_data['totalResultsSize'] = len(self._report_data['selected'])

    @staticmethod
    def _format_address(address):
        """Replace address country code with description."""
        if 'country' in address and address['country']:
            country = address['country']
            if country == 'CA':
                address['country'] = 'Canada'
            elif country == 'US':
                address['country'] = 'United States of America'
            else:
                try:
                    country = pycountry.countries.search_fuzzy(country)[0].name
                    address['country'] = country
                except (AttributeError, TypeError):
                    address['country'] = country

        return address

    def _set_meta_info(self):
        """Identify environment in report if non-production."""
        self._report_data['environment'] = f'{self._get_environment()}'.lstrip()
        self._report_data['meta_account_id'] = self._account_id
        if self._account_name:
            self._report_data['meta_account_name'] = self._account_name

        # Get source ???
        # Appears in the Description section of the PDF Document Properties as Title.
        self._report_data['meta_title'] = ReportMeta.reports[self._report_key]['metaTitle'].upper()

        # Appears in the Description section of the PDF Document Properties as Subject.
        if self._report_key == ReportTypes.SEARCH_DETAIL_REPORT:
            search_type: str = self._report_data['searchQuery']['type']
            search_desc: str = TO_SEARCH_DESCRIPTION[search_type]
            criteria: str = ''
            if search_type == 'OWNER_NAME':
                criteria = self._report_data['searchQuery']['criteria']['ownerName']['last'] + ', '
                criteria += self._report_data['searchQuery']['criteria']['ownerName']['first']
                if 'middle' in self._report_data['searchQuery']['criteria']['ownerName']:
                    criteria += ' ' + self._report_data['searchQuery']['criteria']['ownerName']['middle']
            else:
                criteria = self._report_data['searchQuery']['criteria']['value'].upper()
            self._report_data['meta_subject'] = f'{search_desc} - "{criteria}"'

    @staticmethod
    def _get_environment():
        """Identify environment in report if non-production."""
        namespace = current_app.config.get('POD_NAMESPACE').lower()
        if namespace.endswith('dev'):
            return 'DEV'
        if namespace.endswith('test'):
            return 'TEST'
        if namespace.endswith('tools'):
            return 'SANDBOX'
        return ''

    @staticmethod
    def _to_report_datetime(date_time: str, include_time: bool = True, expiry: bool = False):
        """Convert ISO formatted date time or date string to report format."""
        local_datetime = model_utils.to_local_timestamp(model_utils.ts_from_iso_format(date_time))
        if expiry and local_datetime.hour != 23:  # Expiry dates 15+ years in the future are not ajdusting for DST.
            offset = 23 - local_datetime.hour
            local_datetime = local_datetime + timedelta(hours=offset)
        if include_time:
            timestamp = local_datetime.strftime('%B %-d, %Y at %-I:%M:%S %p Pacific time')
            if timestamp.find(' AM ') > 0:
                return timestamp.replace(' AM ', ' am ')
            return timestamp.replace(' PM ', ' pm ')

        return local_datetime.strftime('%B %-d, %Y')


class ReportMeta:  # pylint: disable=too-few-public-methods
    """Helper class to maintain the report meta information."""

    reports = {
        ReportTypes.SEARCH_DETAIL_REPORT: {
            'reportDescription': 'SearchResult',
            'fileName': 'searchResult',
            'metaTitle': 'Manufacutered Home Registry Search Result',
            'metaSubject': ''
        }
    }
