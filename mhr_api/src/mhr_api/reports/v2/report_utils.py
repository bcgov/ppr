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
"""Helper/utility functions for report generation."""
import copy
import io
from pathlib import Path

from flask import current_app
from jinja2 import Template
import PyPDF2

from mhr_api.utils.base import BaseEnum


HEADER_PATH = '/static/v2/header_replace.html'
HEADER_COVER_PATH = '/static/v2/header_cover.html'
HEADER_MAIL_PATH = '/static/v2/header_mail.html'
HEADER_REG_PATH = '/static/v2/header_registration.html'
FOOTER_PATH = '/static/v2/footer.html'
FOOTER_COVER_PATH = '/static/v2/footer_cover.html'
FOOTER_MAIL_PATH = '/static/v2/footer_mail.html'
HEADER_TITLE_REPLACE = '{{TITLE}}'
HEADER_SUBTITLE_REPLACE = '{{SUBTITLE}}'
HEADER_SUBJECT_REPLACE = '{{SUBJECT}}'
FOOTER_TEXT_REPLACE = '{{FOOTER-TEXT}}'
MARGIN_TOP_REG_REPORT = 1.93
# marginTop 1.5 bottom 0.75
REPORT_META_DATA = {
    'marginTop': 1.25,
    'marginBottom': 0.9,
    'marginLeft': 0.4,
    'marginRight': 0.4,
    'printBackground': True
}
REPORT_FILES = {
    'index.html': '',
    'header.html': '',
    'footer.html': ''
}
REG_PAGE_PREFIX = 'Manufactured Home Registration Number: '


class ReportTypes(BaseEnum):
    """Render an Enum of the MHR PDF report types."""

    MHR_COVER = 'mhrCover'
    MHR_EXEMPTION = 'mhrExemption'
    MHR_REGISTRATION = 'mhrRegistration'
    MHR_REGISTRATION_MAIL = 'mhrRegistrationMail'
    MHR_TRANSFER = 'mhrTransfer'
    MHR_TRANSPORT_PERMIT = 'mhrTransportPermit'
    SEARCH_DETAIL_REPORT = 'searchDetail'
    # Gotenberg
    SEARCH_TOC_REPORT = 'searchTOC'
    SEARCH_BODY_REPORT = 'searchBody'


class Config:  # pylint: disable=too-few-public-methods
    """Configuration that loads report template static data."""

    HEADER_TEMPLATE: str = None
    HEADER_COVER_TEMPLATE: str = None
    HEADER_MAIL_TEMPLATE: str = None
    HEADER_REG_TEMPLATE: str = None
    FOOTER_TEMPLATE: str = None
    FOOTER_COVER_TEMPLATE: str = None
    FOOTER_MAIL_TEMPLATE: str = None

    @classmethod
    def get_header_template(cls) -> str:
        """Fetch header template data from the file system."""
        if not cls.HEADER_TEMPLATE:
            file_path = current_app.config.get('REPORT_TEMPLATE_PATH', '') + HEADER_PATH
            try:
                cls.HEADER_TEMPLATE = Path(file_path).read_text()
                current_app.logger.info(f'Loaded header file from path {file_path}')
            except Exception as err:  # noqa: B902; just logging
                current_app.logger.error(f'Error loading header template from path={file_path}: ' + str(err))
        return cls.HEADER_TEMPLATE

    @classmethod
    def get_reg_header_template(cls) -> str:
        """Fetch registration header template data from the file system."""
        if not cls.HEADER_REG_TEMPLATE:
            file_path = current_app.config.get('REPORT_TEMPLATE_PATH', '') + HEADER_REG_PATH
            try:
                cls.HEADER_REG_TEMPLATE = Path(file_path).read_text()
                current_app.logger.info(f'Loaded registration header file from path {file_path}')
            except Exception as err:  # noqa: B902; just logging
                current_app.logger.error(f'Error loading reg header template from path={file_path}: ' + str(err))
        return cls.HEADER_REG_TEMPLATE

    @classmethod
    def get_cover_header_template(cls) -> str:
        """Fetch mail cover letter header template data from the file system."""
        if not cls.HEADER_COVER_TEMPLATE:
            file_path = current_app.config.get('REPORT_TEMPLATE_PATH', '') + HEADER_COVER_PATH
            try:
                cls.HEADER_COVER_TEMPLATE = Path(file_path).read_text()
                current_app.logger.info(f'Loaded mail cover header file from path {file_path}')
            except Exception as err:  # noqa: B902; just logging
                current_app.logger.error(f'Error loading mail cover header template from path={file_path}: ' + str(err))
        return cls.HEADER_COVER_TEMPLATE

    @classmethod
    def get_mail_header_template(cls) -> str:
        """Fetch mail registration header template data from the file system."""
        if not cls.HEADER_MAIL_TEMPLATE:
            file_path = current_app.config.get('REPORT_TEMPLATE_PATH', '') + HEADER_MAIL_PATH
            try:
                cls.HEADER_MAIL_TEMPLATE = Path(file_path).read_text()
                current_app.logger.info(f'Loaded mail registration header file from path {file_path}')
            except Exception as err:  # noqa: B902; just logging
                current_app.logger.error(f'Error loading mail reg header template from path={file_path}: ' + str(err))
        return cls.HEADER_MAIL_TEMPLATE

    @classmethod
    def get_footer_template(cls) -> str:
        """Fetch footer template data from the file system."""
        if not cls.FOOTER_TEMPLATE:
            file_path = current_app.config.get('REPORT_TEMPLATE_PATH', '') + FOOTER_PATH
            try:
                cls.FOOTER_TEMPLATE = Path(file_path).read_text()
                current_app.logger.info(f'Loaded footer file from path {file_path}')
            except Exception as err:  # noqa: B902; just logging
                current_app.logger.error(f'Error loading footer template from path={file_path}: ' + str(err))
        return cls.FOOTER_TEMPLATE

    @classmethod
    def get_cover_footer_template(cls) -> str:
        """Fetch cover letter footer template data from the file system."""
        if not cls.FOOTER_COVER_TEMPLATE:
            file_path = current_app.config.get('REPORT_TEMPLATE_PATH', '') + FOOTER_COVER_PATH
            try:
                cls.FOOTER_COVER_TEMPLATE = Path(file_path).read_text()
                current_app.logger.info(f'Loaded mail cover footer file from path {file_path}')
            except Exception as err:  # noqa: B902; just logging
                current_app.logger.error(f'Error loading mail cover footer template from path={file_path}: ' + str(err))
        return cls.FOOTER_COVER_TEMPLATE

    @classmethod
    def get_mail_footer_template(cls) -> str:
        """Fetch footer template data from the file system."""
        if not cls.FOOTER_MAIL_TEMPLATE:
            file_path = current_app.config.get('REPORT_TEMPLATE_PATH', '') + FOOTER_MAIL_PATH
            try:
                cls.FOOTER_MAIL_TEMPLATE = Path(file_path).read_text()
                current_app.logger.info(f'Loaded mail footer file from path {file_path}')
            except Exception as err:  # noqa: B902; just logging
                current_app.logger.error(f'Error loading mail footer template from path={file_path}: ' + str(err))
        return cls.FOOTER_MAIL_TEMPLATE


def get_header_data(title: str, subtitle: str = '') -> str:
    """Get report header with the provided titles."""
    template = Config().get_header_template()
    if template:
        return template.replace(HEADER_TITLE_REPLACE, title).replace(HEADER_SUBTITLE_REPLACE, subtitle)
    return None


def get_reg_header_data(title: str, subtitle: str, subject: str, mail: bool = False) -> str:
    """Get registration report header with the provided titles and subject."""
    if mail:
        return get_mail_header_data(title, subtitle, subject)
    template = Config().get_reg_header_template()
    if template:
        rep_template = template.replace(HEADER_TITLE_REPLACE, title).replace(HEADER_SUBTITLE_REPLACE, subtitle)
        return rep_template.replace(HEADER_SUBJECT_REPLACE, subject)
    return None


def get_mail_header_data(title: str, subtitle: str, subject: str) -> str:
    """Get a mail registration report header with the provided titles and subject."""
    template = Config().get_mail_header_template()
    if template:
        rep_template = template.replace(HEADER_TITLE_REPLACE, title).replace(HEADER_SUBTITLE_REPLACE, subtitle)
        return rep_template.replace(HEADER_SUBJECT_REPLACE, subject)
    return None


def get_cover_header_data(title: str, subtitle: str, subject: str) -> str:
    """Get a mail cover letter report header with the provided titles and subject."""
    template = Config().get_cover_header_template()
    if template:
        rep_template = template.replace(HEADER_TITLE_REPLACE, title).replace(HEADER_SUBTITLE_REPLACE, subtitle)
        return rep_template.replace(HEADER_SUBJECT_REPLACE, subject)
    return None


def get_footer_data(footer_text: str, mail: bool = False) -> str:
    """Get report footer with the provided text."""
    if mail:
        return get_mail_footer_data(footer_text)
    template = Config().get_footer_template()
    if template:
        return template.replace(FOOTER_TEXT_REPLACE, footer_text)
    return None


def get_mail_footer_data(footer_text: str) -> str:
    """Get mail report footer with the provided text."""
    template = Config().get_mail_footer_template()
    if template:
        return template.replace(FOOTER_TEXT_REPLACE, footer_text)
    return None


def get_cover_footer_data(footer_text: str) -> str:
    """Get mail cover letter report footer with the provided text."""
    template = Config().get_cover_footer_template()
    if template:
        return template.replace(FOOTER_TEXT_REPLACE, footer_text)
    return None


def get_report_meta_data(report_type: str = '') -> dict:
    """Get gotenberg report configuration data."""
    if not report_type or report_type not in (ReportTypes.MHR_REGISTRATION,
                                              ReportTypes.MHR_COVER,
                                              ReportTypes.MHR_TRANSFER,
                                              ReportTypes.MHR_TRANSPORT_PERMIT,
                                              ReportTypes.MHR_EXEMPTION):
        return copy.deepcopy(REPORT_META_DATA)
    data = copy.deepcopy(REPORT_META_DATA)
    data['marginTop'] = MARGIN_TOP_REG_REPORT
    return data


def get_report_files(request_data: dict, report_type: str, mail: bool = False) -> dict:
    """Get gotenberg report generation source file data."""
    files = copy.deepcopy(REPORT_FILES)
    files['index.html'] = get_html_from_data(request_data)
    footer_text = ''
    if report_type in (ReportTypes.SEARCH_BODY_REPORT,
                       ReportTypes.SEARCH_DETAIL_REPORT,
                       ReportTypes.SEARCH_TOC_REPORT,
                       ReportTypes.MHR_COVER,
                       ReportTypes.MHR_REGISTRATION,
                       ReportTypes.MHR_TRANSFER,
                       ReportTypes.MHR_TRANSPORT_PERMIT,
                       ReportTypes.MHR_EXEMPTION):
        title_text = request_data['templateVars'].get('meta_title', '')
        subtitle_text = request_data['templateVars'].get('meta_subtitle', '')
        footer_text = request_data['templateVars'].get('footer_content', '')
    if report_type in (ReportTypes.MHR_REGISTRATION, ReportTypes.MHR_COVER,
                       ReportTypes.MHR_TRANSFER, ReportTypes.MHR_EXEMPTION, ReportTypes.MHR_TRANSPORT_PERMIT):
        subject_text = request_data['templateVars'].get('meta_subject', '')
        if report_type == ReportTypes.MHR_COVER:
            files['header.html'] = get_cover_header_data(title_text, subtitle_text, subject_text)
        else:
            files['header.html'] = get_reg_header_data(title_text, subtitle_text, subject_text, mail)
    else:
        files['header.html'] = get_header_data(title_text, subtitle_text)
    if report_type == ReportTypes.MHR_COVER:
        files['footer.html'] = get_cover_footer_data(footer_text)
    else:
        files['footer.html'] = get_footer_data(footer_text, mail)
    return files


def get_html_from_data(request_data) -> str:
    """Get html by merging the template with the report data."""
    template_ = Template(request_data['template'], autoescape=True)
    html_output = template_.render(request_data['templateVars'])
    return html_output


def update_toc_page_numbers(json_data, reg_pdf_data):
    """Try and update toc page numbers from the registration pdf."""
    if json_data['totalResultsSize'] > 0:
        bodypdf = PyPDF2.PdfReader(io.BytesIO(reg_pdf_data))
        pagecount = len(bodypdf.pages)
        json_data['totalPageCount'] = pagecount
        page_index = 0
        current_app.logger.info(f' TOC totalPageCount={pagecount}')
        for select in json_data['selected']:
            if not select.get('duplicate', False):
                reg_text = REG_PAGE_PREFIX + select['mhrNumber']
                # current_app.logger.info(f'start page index={page_index} reg_text={reg_text}')
                for i in range(page_index, pagecount):
                    page = bodypdf.pages[i]
                    text = page.extract_text()
                    # current_app.logger.info(text[0:200])
                    if text[0:350].find(reg_text) > 0:
                        page_index = i + 1
                        select['pageNumber'] = (i + 1)
                        break
    return json_data


def set_cover(report_data):  # pylint: disable=too-many-branches, too-many-statements
    """Add cover page report data. Cover page envelope window lines up to a maximum of 4."""
    cover_info = {}
    if report_data.get('submittingParty'):
        party = report_data.get('submittingParty')
        name = ''
        line1: str = ''
        line2: str = ''
        line3: str = ''
        line4: str = ''
        address = party['address']
        country = address.get('country', '')
        region = address.get('region', '')
        if 'businessName' in party:
            name = party['businessName']
        elif 'personName' in party:
            name = party['personName']['first'] + ' ' + party['personName']['last']
        if name:
            line1 = name
            if len(line1) > 40:
                line1 = line1[0:40]
        if country == 'CA':
            postal_code: str = address.get('postalCode', '')
            postal_code = postal_code.replace('-', ' ')
            if len(postal_code) == 6:
                line4 = region + '\n' + postal_code[0:3] + ' ' + postal_code[3:]
            else:
                line4 = region + '\n' + postal_code
        else:
            line4 = region + ' ' + address.get('postalCode', '')

        if (len(address['city']) + len(line4)) < 40:
            line4 = address['city'] + ' ' + line4
        else:
            line3 = address['city']
        if 'street' in address:
            street = address['street']
            if not line2:
                line2 = street
                if len(street) > 40 and line3 == '':
                    line3 = street[40:80]
                    line2 = street[0:40]
            else:
                line3 = street
        if not line3 and 'streetAdditional' in address:
            line3 = address['streetAdditional']
        if line2 and len(line2) > 40:
            line2 = line2[0:40]
        if line3 and len(line3) > 40:
            line3 = line3[0:40]
        if country != 'CA':
            if not line3:
                line3 = line4
                line4 = country
            else:
                line4 = line4 + ' ' + country
        cover_info['line1'] = line1.strip()
        if line2:
            cover_info['line2'] = line2.strip()
        if line3:
            cover_info['line3'] = line3.strip()
        cover_info['line4'] = line4.strip()
    return cover_info
