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
from datetime import datetime
from enum import Enum
from http import HTTPStatus
from pathlib import Path

import pycountry
import pytz
import requests
from flask import current_app, jsonify

from ppr_api.utils.auth import jwt


# Map from API search type to report description
TO_SEARCH_DESCRIPTION = {
    'AIRCRAFT_DOT': 'Aircraft DOT',
    'BUSINESS_DEBTOR': 'Business Debtor',
    'INDIVIDUAL_DEBTOR': 'Individual Debtor',
    'MHR_NUMBER': 'Manufactured Home Registration Number',
    'REGISTRATION_NUMBER': 'Registration Number',
    'SERIAL_NUMBER': 'Serial Number'
}

# Map from API vehicle type to report description
TO_VEHICLE_TYPE_DESCRIPTION = {
    'AC': 'Aircraft (AC)',
    'AF': 'Aircraft Airframe (AF)',
    'AP': 'Airplane (AP)',
    'BO': 'Boat (BO)',
    'EV': 'Electric Motor Vehhicle (EV)',
    'MV': 'Motor Vehicle (MV)',
    'MH': 'Manufactured or Mobile Home (MH)',
    'OB': 'Outboard Boat Motor (OB)',
    'TR': 'Trailer (TR)'
}

# Map from API change/amendment registration change type to report description
TO_CHANGE_TYPE_DESCRIPTION = {
    'AC': 'ADDITION OF COLLATERAL / PROCEEDS',
    'AM': 'AMENDMENT / OTHER CHANGE',
    'CO': 'COURT ORDER',
    'DR': 'DEBTOR RELEASE',
    'DT': 'DEBTOR TRANSFER',
    'PD': 'PARTIAL DISCHARGE',
    'ST': 'SECURED PARTY TRANSFER',
    'SU': 'SUBSTITUTION OF COLLATERAL / PROCEEDS',
    'RC': 'REGISTRY CORRECTION'
}


class ReportTypes(Enum):
    """Render an Enum of the PPR PDF report types."""

    SEARCH_DETAIL_REPORT = 'searchDetail'
    FINANCING_STATEMENT_REPORT = 'financingStatement'
    RENEWAL_STATEMENT_REPORT = 'renewalStatement'
    DISCHARGE_STATEMENT_REPORT = 'dischargeStatement'
    CHANGE_STATEMENT_REPORT = 'changeStatement'
    AMENDMENT_STATEMENT_REPORT = 'amendmentStatement'


class Report:  # pylint: disable=too-few-public-methods
    """Service to create report outputs."""

    def __init__(self, report_data, account_id, report_type=None, account_name=None):
        """Create the Report instance."""
        self._report_data = report_data
        self._report_key = report_type
        self._account_id = account_id
        self._account_name = account_name

    def get_pdf(self, report_type=None):
        """Render a pdf for the report type and report data."""
        if report_type:
            self._report_key = report_type
        headers = {
            'Authorization': 'Bearer {}'.format(jwt.get_token_auth_header()),
            'Content-Type': 'application/json'
        }
        data = self._setup_report_data()
        current_app.logger.debug('Account {0} report type {1} setting up report data.'
                                 .format(self._account_id, self._report_key))
        url = current_app.config.get('REPORT_SVC_URL')
        current_app.logger.debug('Account {0} report type {1} calling report-api {2}.'
                                 .format(self._account_id, self._report_key, url))
        response = requests.post(url=url, headers=headers, data=json.dumps(data))
        current_app.logger.debug('Account {0} report type {1} response status: {2}.'
                                 .format(self._account_id, self._report_key, response.status_code))

        if response.status_code != HTTPStatus.OK:
            current_app.logger.error('Account {0} response status: {1} error: {2}.'
                                     .format(self._account_id, response.status_code, str(response.content)))
            return jsonify(message=str(response.content)), response.status_code
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
        if self._report_key == ReportTypes.SEARCH_DETAIL_REPORT.value:
            return self._report_data['searchDateTime']

        return self._report_data['createDateTime']

    def _get_report_id(self):
        """Get the report transaction ID for the filename from the report data."""
        report_id = ''
        if self._report_key == ReportTypes.SEARCH_DETAIL_REPORT.value and 'payment' in self._report_data:
            report_id = self._report_data['payment']['invoiceId']
        elif self._report_key == ReportTypes.FINANCING_STATEMENT_REPORT.value and \
                'baseRegistrationNumber' in self._report_data:
            report_id = self._report_data['baseRegistrationNumber']
        elif self._report_key == ReportTypes.RENEWAL_STATEMENT_REPORT.value and \
                'renewalRegistrationNumber' in self._report_data:
            report_id = self._report_data['renewalRegistrationNumber']
        elif self._report_key == ReportTypes.DISCHARGE_STATEMENT_REPORT.value and \
                'dischargeRegistrationNumber' in self._report_data:
            report_id = self._report_data['dischargeRegistrationNumber']
        elif self._report_key == ReportTypes.CHANGE_STATEMENT_REPORT.value and \
                'changeRegistrationNumber' in self._report_data:
            report_id = self._report_data['changeRegistrationNumber']
        elif self._report_key == ReportTypes.AMENDMENT_STATEMENT_REPORT.value and \
                'amendmentRegistrationNumber' in self._report_data:
            report_id = self._report_data['amendmentRegistrationNumber']

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
            'logo',
            'macros',
            'registration/securedParties',
            'registration/courtOrderInformation',
            'registration/debtors',
            'registration/registeringParty',
            'registration/vehicleCollateral',
            'registration/generalCollateral',
            'registration/amendmentStatement',
            'registration/changeStatement',
            'registration/dischargeStatement',
            'registration/renewalStatement',
            'search-result/selected',
            'search-result/financingStatement',
            'search-result/amendmentStatement',
            'search-result/changeStatement',
            'search-result/renewalStatement',
            'search-result/dischargeStatement',
            'search-result/securedParties',
            'search-result/courtOrderInformation',
            'search-result/debtors',
            'search-result/registeringParty',
            'search-result/vehicleCollateral',
            'search-result/generalCollateral'
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
        self._set_addresses()
        self._set_date_times()
        self._set_vehicle_collateral()
        self._set_meta_info()
        self._set_selected()
        return self._report_data

    def _set_addresses(self):
        """Replace address country code with description."""
        if self._report_key == ReportTypes.SEARCH_DETAIL_REPORT.value and self._report_data['totalResultsSize'] > 0:
            self._set_search_addresses()

        elif self._report_key == ReportTypes.FINANCING_STATEMENT_REPORT.value:
            self._set_financing_addresses(self._report_data)
            if 'changes' in self._report_data:
                for change in self._report_data['changes']:
                    if change['statementType'] == 'CHANGE_STATEMENT':
                        self._set_modified_parties(change)
                    elif change['statementType'] == 'AMENDMENT_STATEMENT':
                        self._set_modified_parties(change)
                    else:
                        self._format_address(change['registeringParty']['address'])
        elif self._report_key == ReportTypes.AMENDMENT_STATEMENT_REPORT.value:
            self._set_modified_parties(self._report_data)
        elif self._report_key == ReportTypes.CHANGE_STATEMENT_REPORT.value:
            self._set_modified_parties(self._report_data)
        elif self._report_key != ReportTypes.SEARCH_DETAIL_REPORT.value:
            self._format_address(self._report_data['registeringParty']['address'])

    def _set_search_addresses(self):
        """Replace search results addresses country code with description."""
        for detail in self._report_data['details']:
            self._set_financing_addresses(detail['financingStatement'])
            if 'changes' in detail['financingStatement']:
                for change in detail['financingStatement']['changes']:
                    if change['statementType'] == 'CHANGE_STATEMENT':
                        self._set_modified_parties(change)
                    elif change['statementType'] == 'AMENDMENT_STATEMENT':
                        self._set_modified_parties(change)
                    else:
                        self._format_address(change['registeringParty']['address'])

    def _set_financing_addresses(self, statement):
        """Replace financing statement addresses country code with description."""
        self._format_address(statement['registeringParty']['address'])
        for secured_party in statement['securedParties']:
            self._format_address(secured_party['address'])
        for debtor in statement['debtors']:
            self._format_address(debtor['address'])

    @staticmethod
    def _set_financing_vehicle_collateral(statement):
        """Replace financing statement vehicle collateral type code with description."""
        if 'vehicleCollateral' in statement:
            mh_count = 0
            for collateral in statement['vehicleCollateral']:
                if collateral['type'] == 'MH':
                    mh_count += 1
                desc = TO_VEHICLE_TYPE_DESCRIPTION[collateral['type']]
                collateral['type'] = desc
            statement['mhCollateralCount'] = mh_count

    @staticmethod
    def _set_amend_change_vehicle_collateral(statement):
        """Replace amendment/change statement vehicle collateral type code with description."""
        if 'deleteVehicleCollateral' in statement or 'addVehicleCollateral' in statement:
            mh_count = 0
            if 'deleteVehicleCollateral' in statement:
                for delete_collateral in statement['deleteVehicleCollateral']:
                    if delete_collateral['type'] == 'MH':
                        mh_count += 1
                    desc = TO_VEHICLE_TYPE_DESCRIPTION[delete_collateral['type']]
                    delete_collateral['type'] = desc
            if 'addVehicleCollateral' in statement:
                for add_collateral in statement['addVehicleCollateral']:
                    if add_collateral['type'] == 'MH':
                        mh_count += 1
                    desc = TO_VEHICLE_TYPE_DESCRIPTION[add_collateral['type']]
                    add_collateral['type'] = desc
            statement['mhCollateralCount'] = mh_count

    @staticmethod
    def _set_amend_vehicle_collateral(statement):
        """Replace amendment statement vehicle collateral type code with description. Set if change is an edit."""
        Report._set_amend_change_vehicle_collateral(statement)
        if 'deleteVehicleCollateral' in statement and 'addVehicleCollateral' in statement:
            for add in statement['addVehicleCollateral']:
                for delete in statement['deleteVehicleCollateral']:
                    if 'reg_id' in add and 'reg_id' in delete and add['reg_id'] == delete['reg_id']:
                        add['edit'] = True
                        delete['edit'] = True
        if 'deleteGeneralCollateral' in statement and 'addGeneralCollateral' in statement:
            for add in statement['addGeneralCollateral']:
                for delete in statement['deleteGeneralCollateral']:
                    if 'reg_id' in add and 'reg_id' in delete and add['reg_id'] == delete['reg_id']:
                        add['edit'] = True
                        delete['edit'] = True

    def _set_vehicle_collateral(self):
        """Replace vehicle collateral type codes with descriptions."""
        if self._report_key == ReportTypes.SEARCH_DETAIL_REPORT.value and self._report_data['totalResultsSize'] > 0:
            self._set_search_vehicle_collateral()
        elif self._report_key == ReportTypes.FINANCING_STATEMENT_REPORT.value:
            Report._set_financing_vehicle_collateral(self._report_data)
            if 'changes' in self._report_data:
                for change in self._report_data['changes']:
                    if change['statementType'] == 'CHANGE_STATEMENT':
                        Report._set_amend_change_vehicle_collateral(change)
                    elif change['statementType'] == 'AMENDMENT_STATEMENT':
                        Report._set_amend_vehicle_collateral(change)
        elif self._report_key == ReportTypes.AMENDMENT_STATEMENT_REPORT.value:
            Report._set_amend_vehicle_collateral(self._report_data)
        elif self._report_key == ReportTypes.CHANGE_STATEMENT_REPORT.value:
            Report._set_amend_change_vehicle_collateral(self._report_data)

    def _set_search_vehicle_collateral(self):
        """Replace search results vehicle collateral type codes with descriptions."""
        for detail in self._report_data['details']:
            Report._set_financing_vehicle_collateral(detail['financingStatement'])
            if 'changes' in detail['financingStatement']:
                for change in detail['financingStatement']['changes']:
                    if change['statementType'] == 'CHANGE_STATEMENT':
                        Report._set_amend_change_vehicle_collateral(change)
                    elif change['statementType'] == 'AMENDMENT_STATEMENT':
                        Report._set_amend_vehicle_collateral(change)

    def _set_amend_change_addresses(self, statement):
        """Replace amendment/change statement address country code with description."""
        self._format_address(statement['registeringParty']['address'])
        if 'deleteSecuredParties' in statement:
            for delete_secured in statement['deleteSecuredParties']:
                self._format_address(delete_secured['address'])
        if 'addSecuredParties' in statement:
            for add_secured in statement['addSecuredParties']:
                self._format_address(add_secured['address'])
        if 'deleteDebtors' in statement:
            for delete_debtor in statement['deleteDebtors']:
                self._format_address(delete_debtor['address'])
        if 'addDebtors' in statement:
            for add_debtor in statement['addDebtors']:
                self._format_address(add_debtor['address'])

    def _set_amend_party_addresses(self, statement):
        """Replace amendment statement address country code with description. Set if party edited."""
        self._set_amend_change_addresses(statement)
        if 'deleteSecuredParties' in statement and 'addSecuredParties' in statement:
            for add_secured in statement['addSecuredParties']:
                for delete_secured in statement['deleteSecuredParties']:
                    if add_secured['address'] == delete_secured['address']:
                        add_secured['name_change'] = True
                        delete_secured['edit'] = True
                    elif 'businessName' in add_secured and 'businessName' in delete_secured and \
                            add_secured['businessName'] == delete_secured['businessName']:
                        add_secured['address_change'] = True
                        delete_secured['edit'] = True
                    elif 'personName' in add_secured and 'personName' in delete_secured and \
                            add_secured['personName'] == delete_secured['personName']:
                        add_secured['address_change'] = True
                        delete_secured['edit'] = True
        if 'deleteDebtors' in statement and 'addDebtors' in statement:
            for add in statement['addDebtors']:
                for delete in statement['deleteDebtors']:
                    if add['address'] == delete['address']:
                        add['name_change'] = True
                        delete['edit'] = True
                    elif 'businessName' in add and 'businessName' in delete and \
                            add['businessName'] == delete['businessName']:
                        add['name_change'] = True
                        delete['edit'] = True
                    elif 'personName' in add and 'personName' in delete and \
                            add['personName'] == delete['personName']:
                        add['name_change'] = True
                        delete['edit'] = True

    @staticmethod
    def _set_modified_party(add_party, delete_party):
        """Set the update flags for a single party ."""
        if 'reg_id' in add_party and 'reg_id' in delete_party and add_party['reg_id'] == delete_party['reg_id']:
            delete_party['edit'] = True
            if add_party['address'] != delete_party['address']:
                add_party['address_change'] = True
            if 'businessName' in add_party and 'businessName' in delete_party and \
                    add_party['businessName'] != delete_party['businessName']:
                add_party['name_change'] = True
            elif 'personName' in add_party and 'personName' in delete_party and \
                    add_party['personName'] != delete_party['personName']:
                add_party['name_change'] = True

    def _set_modified_parties(self, statement):
        """Replace amendment or change address country code with description. Set if party edited."""
        self._set_amend_change_addresses(statement)
        if 'deleteSecuredParties' in statement and 'addSecuredParties' in statement:
            for add_secured in statement['addSecuredParties']:
                for delete_secured in statement['deleteSecuredParties']:
                    Report._set_modified_party(add_secured, delete_secured)
        if 'deleteDebtors' in statement and 'addDebtors' in statement:
            for add_debtor in statement['addDebtors']:
                for delete_debtor in statement['deleteDebtors']:
                    Report._set_modified_party(add_debtor, delete_debtor)

    @staticmethod
    def _set_financing_date_time(statement):
        """Replace financing statement API ISO UTC strings with local report format strings."""
        statement['createDateTime'] = Report._to_report_datetime(statement['createDateTime'])
        if 'expiryDate' in statement:
            statement['expiryDate'] = Report._to_report_datetime(statement['expiryDate'])
        if 'surrenderDate' in statement:
            statement['surrenderDate'] = Report._to_report_datetime(statement['surrenderDate'], False)
        if 'dischargedDateTime' in statement:
            statement['dischargedDateTime'] = Report._to_report_datetime(statement['dischargedDateTime'])
        if 'courtOrderInformation' in statement and 'orderDate' in statement['courtOrderInformation']:
            order_date = Report._to_report_datetime(statement['courtOrderInformation']['orderDate'], False)
            statement['courtOrderInformation']['orderDate'] = order_date

        for debtor in statement['debtors']:
            if 'birthDate' in debtor:
                debtor['birthDate'] = Report._to_report_datetime(debtor['birthDate'], False)

    @staticmethod
    def _set_change_date_time(statement):
        """Replace non-financing statement API ISO UTC strings with local report format strings."""
        statement['createDateTime'] = Report._to_report_datetime(statement['createDateTime'])
        if 'courtOrderInformation' in statement and 'orderDate' in statement['courtOrderInformation']:
            order_date = Report._to_report_datetime(statement['courtOrderInformation']['orderDate'], False)
            statement['courtOrderInformation']['orderDate'] = order_date
        if 'changeType' in statement:
            statement['changeType'] = TO_CHANGE_TYPE_DESCRIPTION[statement['changeType']]
        if 'expiryDate' in statement:
            statement['expiryDate'] = Report._to_report_datetime(statement['expiryDate'])
        if 'surrenderDate' in statement:
            statement['surrenderDate'] = Report._to_report_datetime(statement['surrenderDate'], False)
        if 'deleteDebtors' in statement:
            for delete_debtor in statement['deleteDebtors']:
                if 'birthDate' in delete_debtor:
                    delete_debtor['birthDate'] = Report._to_report_datetime(delete_debtor['birthDate'], False)
        if 'addDebtors' in statement:
            for add_debtor in statement['addDebtors']:
                if 'birthDate' in add_debtor:
                    add_debtor['birthDate'] = Report._to_report_datetime(add_debtor['birthDate'], False)

    def _set_date_times(self):
        """Replace API ISO UTC strings with local report format strings."""
        if self._report_key == ReportTypes.SEARCH_DETAIL_REPORT.value:
            self._report_data['searchDateTime'] = Report._to_report_datetime(self._report_data['searchDateTime'])
            if self._report_data['totalResultsSize'] > 0:
                for detail in self._report_data['details']:
                    Report._set_financing_date_time(detail['financingStatement'])
                    if 'changes' in detail['financingStatement']:
                        for change in detail['financingStatement']['changes']:
                            Report._set_change_date_time(change)
        elif self._report_key == ReportTypes.FINANCING_STATEMENT_REPORT.value:
            Report._set_financing_date_time(self._report_data)
            if 'changes' in self._report_data:
                for change in self._report_data['changes']:
                    Report._set_change_date_time(change)
        else:
            Report._set_change_date_time(self._report_data)

    def _set_selected(self):
        """Replace selection serial type code with description. Remove unselected items."""
        if 'selected' in self._report_data:
            new_selected = []
            for result in self._report_data['selected']:
                if result['matchType'] == 'EXACT' or 'selected' not in result or result['selected']:
                    if 'vehicleCollateral' in result:
                        code = result['vehicleCollateral']['type']
                        result['vehicleCollateral']['type'] = TO_VEHICLE_TYPE_DESCRIPTION[code]
                    new_selected.append(result)
            self._report_data['selected'] = new_selected

    @staticmethod
    def _format_address(address):
        """Replace address country code with description."""
        country = address['country']
        if country == 'CA':
            address['country'] = 'Canada'
        elif country == 'US':
            address['country'] = 'United States of America'
        else:
            country = pycountry.countries.search_fuzzy(country)[0].name
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
        if self._report_key == ReportTypes.SEARCH_DETAIL_REPORT.value:
            search_type = self._report_data['searchQuery']['type']
            search_desc = TO_SEARCH_DESCRIPTION[search_type]
            criteria = ''
            if search_type == 'BUSINESS_DEBTOR':
                criteria = self._report_data['searchQuery']['criteria']['debtorName']['business']
            elif search_type == 'INDIVIDUAL_DEBTOR':
                criteria = self._report_data['searchQuery']['criteria']['debtorName']['first'] + ' '
                if 'second' in self._report_data['searchQuery']['criteria']['debtorName']:
                    criteria += self._report_data['searchQuery']['criteria']['debtorName']['second'] + ' '
                criteria += self._report_data['searchQuery']['criteria']['debtorName']['last']
            else:
                criteria = self._report_data['searchQuery']['criteria']['value']
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
    def _to_report_datetime(date_time: str, include_time: bool = True):
        """Convert ISO formatted date time or date string to report format."""
        utc_datetime = datetime.fromisoformat(date_time)
        # local_datetime = datetime.fromtimestamp(utc_datetime.timestamp())
        local_datetime = utc_datetime.astimezone(pytz.timezone('Canada/Pacific'))
        if include_time:
            timestamp = local_datetime.strftime('%B %-d, %Y %-I:%M:%S %p Pacific Time')
            if timestamp.find(' AM ') > 0:
                return timestamp.replace(' AM ', ' am ')
            return timestamp.replace(' PM ', ' pm ')

        return local_datetime.strftime('%B %d, %Y')


class ReportMeta:  # pylint: disable=too-few-public-methods
    """Helper class to maintain the report meta information."""

    reports = {
        ReportTypes.SEARCH_DETAIL_REPORT.value: {
            'reportDescription': 'SearchResult',
            'fileName': 'searchResult',
            'metaTitle': 'Personal Property Registry Search Result',
            'metaSubject': ''
        },
        ReportTypes.FINANCING_STATEMENT_REPORT.value: {
            'reportDescription': 'FinancingStatement',
            'fileName': 'financingStatement',
            'metaTitle': 'Personal Property Registry Financing Statement',
            'metaSubject': 'Base Registration Number: {self._get_report_id()}'
        },
        ReportTypes.RENEWAL_STATEMENT_REPORT.value: {
            'reportDescription': 'RenewalStatement',
            'fileName': 'renewalStatement',
            'metaTitle': 'Personal Property Registry Renewal Statement',
            'metaSubject': 'Registration Number: {self._get_report_id()}'
        },
        ReportTypes.DISCHARGE_STATEMENT_REPORT.value: {
            'reportDescription': 'DischargeStatement',
            'fileName': 'dischargeStatement',
            'metaTitle': 'Personal Property Registry Discharge Statement',
            'metaSubject': 'Registration Number: {self._get_report_id()}'
        },
        ReportTypes.CHANGE_STATEMENT_REPORT.value: {
            'reportDescription': 'ChangeStatement',
            'fileName': 'changeStatement',
            'metaTitle': 'Personal Property Registry Change Statement',
            'metaSubject': 'Registration Number: {self._get_report_id()}'
        },
        ReportTypes.AMENDMENT_STATEMENT_REPORT.value: {
            'reportDescription': 'AmendmentStatement',
            'fileName': 'amendmentStatement',
            'metaTitle': 'Personal Property Registry Amendment Statement',
            'metaSubject': 'Registration Number: {self._get_report_id()}'
        }
    }
