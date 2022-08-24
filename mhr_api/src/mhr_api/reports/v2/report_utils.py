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
FOOTER_PAGES_PATH = '/static/v2/footer.html'
HEADER_TITLE_REPLACE = '{{TITLE}}'
FOOTER_TEXT_REPLACE = '{{FOOTER-TEXT}}'
REPORT_META_DATA = {
    'marginTop': 1.5,
    'marginBottom': 0.7,
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

    MHR_REGISTRATION = 'mhrRegistration'
    SEARCH_DETAIL_REPORT = 'searchDetail'
    # Gotenberg
    SEARCH_TOC_REPORT = 'searchTOC'
    SEARCH_BODY_REPORT = 'searchBody'


class Config:  # pylint: disable=too-few-public-methods
    """Configuration that loads report template static data."""

    HEADER_TEMPLATE: str = None
    FOOTER_TEMPLATE: str = None

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
    def get_footer_template(cls) -> str:
        """Fetch footer template data from the file system."""
        if not cls.FOOTER_TEMPLATE:
            file_path = current_app.config.get('REPORT_TEMPLATE_PATH', '') + FOOTER_PAGES_PATH
            try:
                cls.FOOTER_TEMPLATE = Path(file_path).read_text()
                current_app.logger.info(f'Loaded footer file from path {file_path}')
            except Exception as err:  # noqa: B902; just logging
                current_app.logger.error(f'Error loading footer template from path={file_path}: ' + str(err))
        return cls.FOOTER_TEMPLATE


def get_header_data(title: str) -> str:
    """Get report header with the provided title."""
    template = Config().get_header_template()
    if template:
        return template.replace(HEADER_TITLE_REPLACE, title)
    return None


def get_footer_data(footer_text: str) -> str:
    """Get report footer with the provided text."""
    template = Config().get_footer_template()
    if template:
        return template.replace(FOOTER_TEXT_REPLACE, footer_text)
    return None


def get_report_meta_data() -> dict:
    """Get gotenberg report configuration data."""
    return copy.deepcopy(REPORT_META_DATA)


def get_report_files(request_data: dict, report_type: str) -> dict:
    """Get gotenberg report generation source file data."""
    files = copy.deepcopy(REPORT_FILES)
    files['index.html'] = get_html_from_data(request_data)
    header_text = ''
    footer_text = ''
    if report_type in (ReportTypes.SEARCH_BODY_REPORT, ReportTypes.SEARCH_DETAIL_REPORT, ReportTypes.SEARCH_TOC_REPORT):
        header_text = request_data['templateVars'].get('meta_title', '')
        footer_text = request_data['templateVars'].get('footer_content', '')

    files['header.html'] = get_header_data(header_text)
    files['footer.html'] = get_footer_data(footer_text)
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
                    if text[0:200].find(reg_text) > 0:
                        page_index = i + 1
                        select['pageNumber'] = (i + 1)
                        break
    return json_data
