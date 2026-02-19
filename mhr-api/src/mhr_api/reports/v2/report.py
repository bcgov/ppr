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
# pylint: disable=too-many-lines
import copy
from http import HTTPStatus
from pathlib import Path

import markupsafe
import pycountry
import requests
from flask import current_app, jsonify

from mhr_api.exceptions import ResourceErrorCodes
from mhr_api.models import registration_utils as reg_utils
from mhr_api.models import utils as model_utils
from mhr_api.models.type_tables import MhrDocumentTypes, MhrRegistrationTypes, MhrTenancyTypes
from mhr_api.reports import ppr_report_utils
from mhr_api.reports.v2 import report_utils
from mhr_api.reports.v2.report_utils import ReportTypes
from mhr_api.services.gcp_auth.auth_service import GoogleAuthService
from mhr_api.utils.logging import logger

# Map from API search type to report description
TO_SEARCH_DESCRIPTION = {
    "OWNER_NAME": "Owner Name",
    "ORGANIZATION_NAME": "Organization Name",
    "MHR_NUMBER": "Manufactured Home Registration Number",
    "SERIAL_NUMBER": "Serial Number",
}
SINGLE_URI = "/forms/chromium/convert/html"
MERGE_URI = "/forms/pdfengines/merge"


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

    def get_pdf(self, report_type=None):
        """Render a pdf for the report type and report data."""
        if report_type:
            self._report_key = report_type
        if self._report_key == ReportTypes.SEARCH_DETAIL_REPORT:
            logger.debug("Search report generating TOC page numbers as a second report api call.")
            return self.get_search_pdf()
        if self._report_key == ReportTypes.MHR_REGISTRATION_COVER:
            return self.get_registration_cover_pdf()
        if self._report_key == ReportTypes.MHR_REGISTRATION_STAFF:
            return self.get_registration_staff_pdf()

        add_cover = self._report_key == ReportTypes.MHR_TRANSFER

        # Generate the cover page for specific non-staff reports
        if add_cover:
            logger.debug("Generate cover letter for specific non-staff report")
            cover_content, cover_status, cover_headers = self.get_registration_cover_pdf()
            if cover_status != HTTPStatus.OK:
                return cover_content, cover_status, cover_headers

        logger.debug("Account {0} report type {1} setting up report data.".format(self._account_id, self._report_key))
        data = self._setup_report_data()
        url = current_app.config.get("REPORT_SVC_URL") + SINGLE_URI
        logger.debug(
            "Account {0} report type {1} calling report-api {2}.".format(self._account_id, self._report_key, url)
        )
        meta_data = report_utils.get_report_meta_data(self._report_key)
        files = report_utils.get_report_files(data, self._report_key)
        headers = Report.get_headers()
        response = requests.post(url=url, headers=headers, data=meta_data, files=files, timeout=1800.0)
        logger.debug(
            "Account {0} report type {1} response status: {2}.".format(
                self._account_id, self._report_key, response.status_code
            )
        )
        if response.status_code != HTTPStatus.OK:
            content = ResourceErrorCodes.REPORT_ERR + ": " + response.content.decode("ascii")
            logger.error(
                "Account {0} response status: {1} error: {2}.".format(self._account_id, response.status_code, content)
            )
            return jsonify(message=content), response.status_code, None

        # Merge the cover letter and registration reports if applicable.
        if add_cover:
            files = []
            files.append(cover_content)
            files.append(response.content)
            return Report.batch_merge(files)

        return response.content, response.status_code, {"Content-Type": "application/pdf"}

    def get_search_pdf(self):
        """Render a search report with TOC page numbers set in a second report call."""
        logger.debug("Account {0} report type {1} setting up report data.".format(self._account_id, self._report_key))
        data_copy = copy.deepcopy(self._report_data)
        # 1: Generate the search pdf with no TOC page numbers or total page count.
        data = self._setup_report_data()
        url = current_app.config.get("REPORT_SVC_URL") + SINGLE_URI
        logger.debug(
            "Account {0} report type {1} calling report-api {2}.".format(self._account_id, self._report_key, url)
        )
        meta_data = report_utils.get_report_meta_data(self._report_key)
        files = report_utils.get_report_files(data, self._report_key)
        headers = Report.get_headers()
        response_reg = requests.post(url=url, headers=headers, data=meta_data, files=files, timeout=1800.0)
        logger.debug(
            "Account {0} report type {1} response status: {2}.".format(
                self._account_id, self._report_key, response_reg.status_code
            )
        )
        if response_reg.status_code != HTTPStatus.OK:
            content = ResourceErrorCodes.REPORT_ERR + ": " + response_reg.content.decode("ascii")
            logger.error(
                "Account {0} response status: {1} error: {2}.".format(
                    self._account_id, response_reg.status_code, content
                )
            )
            return jsonify(message=content), response_reg.status_code, None
        # 2: Set TOC page numbers in report data from initial search pdf page numbering.
        self._report_data = report_utils.update_toc_page_numbers(data_copy, response_reg.content)
        # 3: Generate search report again with TOC page numbers and total page count.
        data_final = self._setup_report_data()
        logger.debug(
            "Account {0} report type {1} calling report-api {2}.".format(self._account_id, self._report_key, url)
        )
        files = report_utils.get_report_files(data_final, self._report_key)
        logger.info("Search report regenerating with TOC page numbers set.")
        response = requests.post(url=url, headers=headers, data=meta_data, files=files, timeout=1800.0)
        logger.info("Search report regeneration with TOC page numbers completed.")
        if response.status_code != HTTPStatus.OK:
            content = ResourceErrorCodes.REPORT_ERR + ": " + response.content.decode("ascii")
            logger.error(
                "Account {0} response status: {1} error: {2}.".format(self._account_id, response.status_code, content)
            )
            return jsonify(message=content), response.status_code, None
        return response.content, response.status_code, {"Content-Type": "application/pdf"}

    def get_registration_cover_pdf(self):
        """Render a registration cover letter report."""
        logger.debug(f"Account {self._account_id} setting up reg cover report data.")
        original_report_key = self._report_key
        original_report_data = copy.deepcopy(self._report_data)
        try:
            self._report_key = ReportTypes.MHR_REGISTRATION_COVER
            data = self._setup_report_data()
            url = current_app.config.get("REPORT_SVC_URL") + SINGLE_URI
            meta_data = report_utils.get_report_meta_data(self._report_key)
            files = report_utils.get_report_files(data, self._report_key, False)
            headers = Report.get_headers()
            response_cover = requests.post(url=url, headers=headers, data=meta_data, files=files, timeout=1800.0)
            logger.debug(
                "Account {0} report type {1} response status: {2}.".format(
                    self._account_id, self._report_key, response_cover.status_code
                )
            )
            if response_cover.status_code != HTTPStatus.OK:
                content = ResourceErrorCodes.REPORT_ERR + ": " + response_cover.content.decode("ascii")
                logger.error(
                    "Account {0} response status: {1} error: {2}.".format(
                        self._account_id, response_cover.status_code, content
                    )
                )
                return jsonify(message=content), response_cover.status_code, None
            return response_cover.content, response_cover.status_code, {"Content-Type": "application/pdf"}
        finally:
            self._report_key = original_report_key
            self._report_data = original_report_data

    def get_registration_staff_pdf(self):
        """Render a staff MH registration report with cover letter."""
        logger.debug(f"Account {self._account_id} setting up staff reg report data.")
        create_ts = self._report_data["createDateTime"]
        if self._report_data.get("registrationType", "") == MhrRegistrationTypes.REG_NOTE and self._report_data.get(
            "note"
        ):
            doc_desc = report_utils.format_description(self._report_data["note"].get("documentDescription"))
            self._report_data["note"]["coverDocumentDescription"] = doc_desc
            if self._report_data["note"].get("cancelledDocumentDescription"):
                desc = report_utils.format_description(self._report_data["note"].get("cancelledDocumentDescription"))
                self._report_data["note"]["cancelledDocumentDescription"] = desc
        # 1: Generate the cover page report.
        self._report_key = ReportTypes.MHR_REGISTRATION_COVER
        data = self._setup_report_data()
        url = current_app.config.get("REPORT_SVC_URL") + SINGLE_URI
        meta_data = report_utils.get_report_meta_data(self._report_key)
        files = report_utils.get_report_files(data, self._report_key, False)
        headers = Report.get_headers()
        response_cover = requests.post(url=url, headers=headers, data=meta_data, files=files, timeout=1800.0)
        logger.debug(
            "Account {0} report type {1} response status: {2}.".format(
                self._account_id, self._report_key, response_cover.status_code
            )
        )
        if response_cover.status_code != HTTPStatus.OK:
            content = ResourceErrorCodes.REPORT_ERR + ": " + response_cover.content.decode("ascii")
            logger.error(
                "Account {0} response status: {1} error: {2}.".format(
                    self._account_id, response_cover.status_code, content
                )
            )
            return jsonify(message=content), response_cover.status_code, None

        # 2: Generate the registration pdf.
        self._report_key = ReportTypes.MHR_REGISTRATION
        if self._report_data.get("registrationType", "") in (
            MhrRegistrationTypes.TRANS,
            MhrRegistrationTypes.TRAND,
            MhrRegistrationTypes.TRANS_ADMIN,
            MhrRegistrationTypes.TRANS_AFFIDAVIT,
            MhrRegistrationTypes.TRANS_WILL,
        ):
            self._report_key = ReportTypes.MHR_TRANSFER
        elif self._report_data.get("registrationType", "") in (
            MhrRegistrationTypes.EXEMPTION_RES,
            MhrRegistrationTypes.EXEMPTION_NON_RES,
        ):
            self._report_key = ReportTypes.MHR_EXEMPTION
        elif self._report_data.get("nocLocation"):
            self._report_key = ReportTypes.MHR_ADMIN_REGISTRATION
        elif self._report_data.get("registrationType", "") in (
            MhrRegistrationTypes.PERMIT,
            MhrRegistrationTypes.PERMIT_EXTENSION,
        ):
            self._report_key = ReportTypes.MHR_TRANSPORT_PERMIT
        elif (
            self._report_data.get("registrationType", "") == MhrRegistrationTypes.AMENDMENT
            and self._report_data.get("permitRegistrationNumber")
            and self._report_data.get("amendment")
        ):
            self._report_key = ReportTypes.MHR_TRANSPORT_PERMIT
        elif self._report_data.get("registrationType", "") == MhrRegistrationTypes.REG_NOTE:
            if self._report_data.get("documentType"):
                self._report_key = ReportTypes.MHR_ADMIN_REGISTRATION
            else:
                self._report_key = ReportTypes.MHR_NOTE
        self._report_data["createDateTime"] = create_ts
        data = self._setup_report_data()
        logger.debug(
            "Account {0} report type {1} calling report-api {2}.".format(self._account_id, self._report_key, url)
        )
        meta_data = report_utils.get_report_meta_data(self._report_key)
        files = report_utils.get_report_files(data, self._report_key, False)
        response_reg = requests.post(url=url, headers=headers, data=meta_data, files=files, timeout=1800.0)
        logger.debug(
            "Account {0} report type {1} response status: {2}.".format(
                self._account_id, self._report_key, response_reg.status_code
            )
        )
        if response_reg.status_code != HTTPStatus.OK:
            content = ResourceErrorCodes.REPORT_ERR + ": " + response_reg.content.decode("ascii")
            logger.error(
                "Account {0} response status: {1} error: {2}.".format(
                    self._account_id, response_reg.status_code, content
                )
            )
            return jsonify(message=content), response_reg.status_code, None
        # 3: Merge cover letter and registration reports.
        files = []
        files.append(response_cover.content)
        files.append(response_reg.content)
        return Report.batch_merge(files)

    @staticmethod
    def get_headers() -> dict:
        """Build the report service request headers."""
        headers = {}
        token = GoogleAuthService.get_report_api_token()
        if token:
            headers["Authorization"] = "Bearer {}".format(token)
        return headers

    @staticmethod
    def batch_merge(pdf_list):
        """Merge a list of pdf files into a single pdf."""
        if not pdf_list:
            return None
        logger.debug(f"Setting up batch merge for {len(pdf_list)} files.")
        count: int = 0
        files = {}
        for pdf in pdf_list:
            count += 1
            filename = "file" + str(count) + ".pdf"
            files[filename] = pdf
        headers = Report.get_headers()
        url = current_app.config.get("REPORT_SVC_URL") + MERGE_URI
        response = requests.post(url=url, headers=headers, files=files, timeout=1800.0)
        logger.debug("Batch merge reports response status: {0}.".format(response.status_code))
        if response.status_code != HTTPStatus.OK:
            content = ResourceErrorCodes.REPORT_ERR + ": " + response.content.decode("ascii")
            logger.error("Batch merge response status: {0} error: {1}.".format(response.status_code, content))
            return jsonify(message=content), response.status_code, None
        return response.content, response.status_code, {"Content-Type": "application/pdf"}

    def _setup_report_data(self):
        """Set up the report service request data."""
        # logger.debug('Setup report data template starting.')
        template = self._get_template()
        logger.debug("Setup report data template completed, setup data starting.")
        data = {
            "reportName": self._get_report_filename(),
            "template": template,
            "templateVars": self._get_template_data(),
        }
        logger.debug("Setup report data completed.")
        return data

    def _get_report_filename(self):
        """Generate the pdf filename from the report type and report data."""
        report_date = self._get_report_date()
        report_id = self._get_report_id()
        description = ReportMeta.reports[self._report_key]["reportDescription"]
        return "{}_{}_{}.pdf".format(report_id, report_date, description).replace(" ", "_")

    def _get_report_date(self):
        """Get the report date for the filename from the report data."""
        if self._report_key in (
            ReportTypes.SEARCH_DETAIL_REPORT,
            ReportTypes.SEARCH_TOC_REPORT,
            ReportTypes.SEARCH_BODY_REPORT,
        ):
            return self._report_data["searchDateTime"]
        return self._report_data["createDateTime"]

    def _get_report_id(self):
        """Get the report transaction ID for the filename from the report data."""
        report_id = ""
        if (
            self._report_key in (ReportTypes.SEARCH_DETAIL_REPORT, ReportTypes.SEARCH_BODY_REPORT)
            and "payment" in self._report_data
        ):
            report_id = self._report_data["payment"]["invoiceId"]
        elif self._report_key in (
            ReportTypes.MHR_REGISTRATION,
            ReportTypes.MHR_TOD_REJECTION,
        ) and self._report_data.get("mhrNumber"):
            report_id = self._report_data.get("mhrNumber")
        return report_id

    def _get_template(self):
        """Load from the local file system the template matching the report type."""
        try:
            template_path = current_app.config.get("REPORT_TEMPLATE_PATH")
            template_code = Path(f"{template_path}/{self._get_template_filename()}").read_text(encoding="UTF-8")
            # substitute template parts
            template_code = self._substitute_template_parts(template_code)
        except Exception as err:  # noqa: B902; just logging
            logger.error(err)
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
        template_path = current_app.config.get("REPORT_TEMPLATE_PATH")
        template_parts = [
            "v2/style",
            "v2/styleMail",
            "v2/stylePage",
            "v2/stylePageCover",
            "v2/stylePageDraft",
            "v2/stylePageMail",
            "v2/stylePageRegistration",
            "v2/stylePageRegistrationDraft",
            "stylePageMail",
            "logo",
            "macros",
            "registrarSignature",
            "registrarSignatureBlack",
            "registration/details",
            "registration/givingNoticeParty",
            "registration/location",
            "registration/notes",
            "registration/owners",
            "registration/sections",
            "registration/submittingParty",
            "search-result/details",
            "search-result/location",
            "search-result/notes",
            "search-result/owners",
            "search-result/pprRegistrations",
            "v2/search-result/selected",
            "search-result/sections",
            "v2/search-result/registration",
            "search-result-ppr/financingStatement",
            "search-result-ppr/amendmentStatement",
            "search-result-ppr/changeStatement",
            "search-result-ppr/renewalStatement",
            "search-result-ppr/dischargeStatement",
            "search-result-ppr/securedParties",
            "search-result-ppr/courtOrderInformation",
            "search-result-ppr/debtors",
            "search-result-ppr/registeringParty",
            "search-result-ppr/vehicleCollateral",
            "search-result-ppr/generalCollateral",
        ]

        # substitute template parts - marked up by [[filename]]
        for template_part in template_parts:
            if template_code.find("[[{}.html]]".format(template_part)) >= 0:
                template_part_code = Path(f"{template_path}/template-parts/{template_part}.html").read_text(
                    encoding="UTF-8"
                )
                for template_part_nested in template_parts:
                    template_reference = "[[{}.html]]".format(template_part_nested)
                    if template_part_code.find(template_reference) >= 0:
                        path = Path(f"{template_path}/template-parts/{template_part_nested}.html")
                        template_nested_code = path.read_text(encoding="UTF-8")
                        template_part_code = template_part_code.replace(template_reference, template_nested_code)
                template_code = template_code.replace("[[{}.html]]".format(template_part), template_part_code)

        return template_code

    def _get_template_filename(self):
        """Get the report template filename from the report type."""
        file_name = ReportMeta.reports[self._report_key]["fileName"]
        return "{}.html".format(file_name)

    def _get_template_data(self):  # pylint: disable=too-many-branches
        """Get the data for the report, modifying the original for the template output."""
        self._set_meta_info()
        if self._report_key == ReportTypes.SEARCH_TOC_REPORT:
            self._set_selected()
        elif self._report_key == ReportTypes.MHR_COVER:
            self._report_data["cover"] = report_utils.set_cover(self._report_data)
            self._report_data["createDateTime"] = Report._to_report_datetime(self._report_data["createDateTime"])
        elif self._report_key == ReportTypes.MHR_REGISTRATION_COVER:
            self._report_data["regCover"] = report_utils.set_registration_cover(self._report_data)
            if self._report_data.get("nocLocation"):
                self._report_data["createDate"] = Report._to_report_datetime(self._report_data["createDateTime"], False)
                if self._report_data.get("ppr"):
                    self._report_data["ppr"]["registrationDescription"] = report_utils.format_description(
                        self._report_data["ppr"].get("registrationDescription")
                    )
            self._report_data["createDateTime"] = Report._to_report_datetime(self._report_data["createDateTime"])
            if (
                self._report_data.get("registrationType", "") == MhrRegistrationTypes.REG_NOTE
                and self._report_data.get("note")
                and self._report_data.get("documentType", "") != MhrDocumentTypes.CANCEL_PERMIT
            ):
                desc = report_utils.format_description(self._report_data["note"].get("documentDescription", ""))
                self._report_data["documentDescription"] = desc
            elif self._report_data.get("documentDescription"):
                self._report_data["documentDescription"] = report_utils.format_description(
                    self._report_data["documentDescription"]
                )
        elif self._report_key == ReportTypes.MHR_TOD_REJECTION:
            self._report_data["address"] = report_utils.set_registration_cover(self._report_data)
            self._report_data["registrationDescription"] = reg_utils.get_registration_description(
                self._report_data["registrationType"]
            )
            self._report_data["registrationDescription"] = report_utils.format_description(
                self._report_data["registrationDescription"]
            )
            self._report_data["createDateTime"] = Report._to_report_datetime(self._report_data["createDateTime"], False)
        else:
            if self._report_key == ReportTypes.SEARCH_DETAIL_REPORT:
                self._set_search_additional_message()
            elif (
                self._report_data.get("registrationType", "") == MhrRegistrationTypes.REG_NOTE
                and self._report_data.get("note")
                and self._report_data.get("documentType", "") != MhrDocumentTypes.CANCEL_PERMIT
            ):
                desc = report_utils.format_description(self._report_data["note"].get("documentDescription", ""))
                self._report_data["documentDescription"] = desc
            elif self._report_data.get("documentDescription"):
                self._report_data["documentDescription"] = report_utils.format_description(
                    self._report_data["documentDescription"]
                )
            self._set_date_times()
            self._set_addresses()
            self._set_owner_groups()
            if self._report_key not in (ReportTypes.MHR_REGISTRATION, ReportTypes.MHR_TRANSFER):
                self._set_notes()
            if self._report_key == ReportTypes.SEARCH_DETAIL_REPORT:
                self._set_selected()
                self._set_ppr_search()
            elif self._report_key == ReportTypes.SEARCH_BODY_REPORT:
                # Add PPR search template setup here:
                self._set_ppr_search()
            if self._report_key not in (ReportTypes.MHR_TRANSFER, ReportTypes.MHR_NOTE):
                self._set_location()
                self._set_registration_additional_message()
                if self._report_key != ReportTypes.MHR_TRANSPORT_PERMIT:
                    self._set_description()
        return self._report_data

    def _set_ppr_search(self):  # pylint: disable=too-many-branches, too-many-statements
        """PPR search result setup for combined searches."""
        for detail in self._report_data["details"]:
            if detail.get("pprRegistrations"):
                for registration in detail["pprRegistrations"]:
                    logger.debug(
                        "Setting up ppr registration for "
                        + registration["financingStatement"]["baseRegistrationNumber"]
                    )
                    if "registrationAct" in registration["financingStatement"]:
                        act: str = registration["financingStatement"]["registrationAct"]
                        registration["financingStatement"]["registrationAct"] = act.title()
                    ppr_report_utils.set_ppr_template_data(registration["financingStatement"])

    def _set_notes(self):
        """Add note type descriptions and dates."""
        if self._report_key == ReportTypes.SEARCH_DETAIL_REPORT and self._report_data["totalResultsSize"] > 0:
            self._set_search_notes()
        elif self._report_key != ReportTypes.SEARCH_DETAIL_REPORT:
            self._set_note()

    def _set_description(self):
        """Set up report description information."""
        if self._report_key == ReportTypes.MHR_REGISTRATION:
            description = self._report_data.get("description")
            if description and description.get("rebuiltRemarks"):
                description["rebuiltRemarks"] = markupsafe.Markup(description["rebuiltRemarks"])
            if description and description.get("otherRemarks"):
                description["otherRemarks"] = markupsafe.Markup(description["otherRemarks"])

    def _set_owner_groups(self):
        """Set up report owner group information."""
        group_id: int = 1
        if self._report_key == ReportTypes.MHR_TRANSFER:
            if self._report_data.get("addOwnerGroups"):
                has_na: bool = False
                for group in self._report_data.get("addOwnerGroups"):
                    if (
                        group.get("type", "") == MhrTenancyTypes.NA
                        and not group.get("interestNumerator")
                        and not group.get("interestDenominator")
                    ):
                        has_na = True
                    group["groupId"] = group_id
                    group_id += 1
                self._report_data["hasNA"] = has_na
        elif self._report_key == ReportTypes.MHR_REGISTRATION or (
            self._report_key == ReportTypes.MHR_ADMIN_REGISTRATION and self._report_data.get("ownerGroups")
        ):
            has_na: bool = False
            for group in self._report_data.get("ownerGroups"):
                group["groupId"] = group_id
                group_id += 1
                if (
                    group.get("type", "") == MhrTenancyTypes.NA
                    and not group.get("interestNumerator")
                    and not group.get("interestDenominator")
                ):
                    has_na = True
            self._report_data["hasNA"] = has_na
        elif self._report_key in (ReportTypes.SEARCH_DETAIL_REPORT, ReportTypes.SEARCH_BODY_REPORT):
            for detail in self._report_data["details"]:
                group_id = 1
                has_na: bool = False
                for group in detail.get("ownerGroups"):
                    group["groupId"] = group_id
                    group_id += 1
                    if (
                        group.get("type", "") == MhrTenancyTypes.NA
                        and not group.get("interestNumerator")
                        and not group.get("interestDenominator")
                    ):
                        has_na = True
                self._report_data["hasNA"] = has_na

    def _set_individual_location(self, location):
        """Set up report location information for a single location."""
        if (  # pylint: disable=too-many-boolean-expressions
            location.get("lot")
            or location.get("parcel")
            or location.get("block")
            or location.get("districtLot")
            or location.get("partOf")
            or location.get("section")
            or location.get("township")
            or location.get("range")
            or location.get("meridian")
            or location.get("landDistrict")
            or location.get("plan")
        ):
            location["hasLTSAInfo"] = True
        else:
            location["hasLTSAInfo"] = False
        if location.get("pidNumber"):
            pid = location.get("pidNumber")
            location["pidNumber"] = pid[0:3] + "-" + pid[3:6] + "-" + pid[6:]

    def _set_location(self):
        """Set up report location information."""
        if self._report_key in (
            ReportTypes.MHR_REGISTRATION,
            ReportTypes.MHR_EXEMPTION,
            ReportTypes.MHR_ADMIN_REGISTRATION,
            ReportTypes.MHR_TRANSPORT_PERMIT,
        ) and self._report_data.get("location"):
            self._set_individual_location(self._report_data.get("location"))
            if self._report_data.get("previousLocation"):
                self._set_individual_location(self._report_data.get("previousLocation"))
        elif self._report_key in (ReportTypes.SEARCH_DETAIL_REPORT, ReportTypes.SEARCH_BODY_REPORT):
            for detail in self._report_data["details"]:
                self._set_individual_location(detail.get("location"))

    def _set_search_notes(self):  # pylint: disable=too-many-branches
        """Add search note document type description and dates."""
        if self._report_data and self._report_data["details"]:  # pylint: disable=too-many-nested-blocks
            for detail in self._report_data["details"]:
                if detail.get("notes"):
                    for note in detail["notes"]:
                        if note.get("createDateTime"):
                            note["createDateTime"] = Report._to_report_datetime(note.get("createDateTime"))
                        if note.get("expiryDate") and note["expiryDate"] == "0001-01-01":
                            note["expiryDate"] = ""
                        elif note.get("expiryDate"):
                            note["expiryDate"] = Report._to_report_datetime(note["expiryDate"], False)
                        elif note.get("expiryDateTime") and str(note["expiryDateTime"]).startswith("0001-01-01"):
                            note["expiryDateTime"] = ""
                        elif note.get("expiryDateTime"):
                            note["expiryDateTime"] = Report._to_report_datetime(note["expiryDateTime"], False)
                        if note.get("contactPhoneNumber"):
                            phone = note.get("contactPhoneNumber")
                            note["contactPhoneNumber"] = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:]
                        elif note.get("givingNoticeParty") and note["givingNoticeParty"].get("phoneNumber"):
                            phone = note["givingNoticeParty"].get("phoneNumber")
                            note["givingNoticeParty"]["phoneNumber"] = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:]
                        if note.get("effectiveDateTime"):
                            note["effectiveDateTime"] = Report._to_report_datetime(note.get("effectiveDateTime"), False)
                        if note.get("remarks"):
                            remarks: str = note.get("remarks")
                            if remarks.find("\n") >= 0:
                                note["remarks"] = remarks.replace("\n", "<br>")

    def _set_note(self):
        """Add registration note document type description and dates."""
        if self._report_data and self._report_data.get("note"):
            note = self._report_data["note"]
            if note.get("createDateTime"):
                note["createDateTime"] = Report._to_report_datetime(note.get("createDateTime"))
            if note.get("expiryDateTime") and str(note["expiryDateTime"]).startswith("0001-01-01"):
                note["expiryDateTime"] = ""
            elif note.get("expiryDateTime"):
                note["expiryDateTime"] = Report._to_report_datetime(note.get("expiryDateTime"), False)
            if note.get("effectiveDateTime"):
                note["effectiveDateTime"] = Report._to_report_datetime(note.get("effectiveDateTime"), True)
            if note.get("cancelledDateTime"):
                note["cancelledDateTime"] = Report._to_report_datetime(note.get("cancelledDateTime"), True)
            if note.get("givingNoticeParty") and note["givingNoticeParty"].get("phoneNumber"):
                phone = note["givingNoticeParty"].get("phoneNumber")
                note["givingNoticeParty"]["phoneNumber"] = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:]
            if note.get("remarks"):
                remarks: str = note.get("remarks")
                if remarks.find("\n") >= 0:
                    note["remarks"] = remarks.replace("\n", "<br>")

    def _set_registration_additional_message(self):
        """Conditionally add a message to the registration report data."""
        messages = []
        if (
            self._report_data
            and self._report_data.get("description")
            and self._report_data["description"].get("sections")
        ):
            sections = self._report_data["description"].get("sections")
            for section in sections:
                if section.get("widthFeet", 0) > 14 or (
                    section.get("widthFeet", 0) == 14 and section.get("widthInches", 0) >= 6
                ):
                    messages.append({"messageType": "WIDTH"})
                    break
        if messages:
            self._report_data["messages"] = messages

    def _set_search_additional_message(self):  # pylint: disable=too-many-branches
        """Conditionally add a message to the search report data."""
        if self._report_data and self._report_data["details"]:
            for detail in self._report_data["details"]:
                messages = []
                has_exempt_note: bool = False
                if detail.get("location"):
                    if detail["location"].get("leaveProvince") and detail["status"] == "EXEMPT":
                        messages.append({"messageType": "OUT_PROV"})
                if detail.get("description") and detail["description"].get("sections"):
                    sections = detail["description"].get("sections")
                    for section in sections:
                        if section.get("widthFeet", 0) >= 16:
                            messages.append({"messageType": "WIDTH"})
                            break
                if detail.get("notes"):
                    for note in detail["notes"]:
                        if detail["status"] == "CANCELLED" and note.get("documentType", "") == "REGC":
                            messages.append({"messageType": "REGC"})
                        elif (
                            note.get("documentType", "") in ("EXRS", "EXNR")
                            and note.get("createDateTime")
                            and not has_exempt_note
                        ):
                            has_exempt_note = True
                            message = {
                                "messageType": note.get("documentType"),
                                "messageId": note.get("documentRegistrationNumber", ""),
                                "messageDate": Report._to_report_datetime(note["createDateTime"], True),
                            }
                            messages.append(message)
                if not has_exempt_note and detail.get("status") == "EXEMPT":
                    message = {"messageType": "EXEMPT"}
                    messages.append(message)
                if messages:
                    detail["messages"] = messages

    def _set_addresses(self):
        """Replace address country code with description."""
        if (
            self._report_key in (ReportTypes.SEARCH_DETAIL_REPORT, ReportTypes.SEARCH_BODY_REPORT)
            and self._report_data["totalResultsSize"] > 0
        ):
            self._set_search_addresses()
        elif self._report_key in (
            ReportTypes.MHR_REGISTRATION,
            ReportTypes.MHR_TRANSFER,
            ReportTypes.MHR_ADMIN_REGISTRATION,
            ReportTypes.MHR_EXEMPTION,
            ReportTypes.MHR_TRANSPORT_PERMIT,
            ReportTypes.MHR_NOTE,
        ):
            self._set_registration_addresses()
            if self._report_data.get("submittingParty") and self._report_data["submittingParty"].get("phoneNumber"):
                self._report_data["submittingParty"]["phoneNumber"] = report_utils.format_phone_number(
                    self._report_data["submittingParty"].get("phoneNumber")
                )

    def _set_search_addresses(self):
        """Replace search results addresses country code with description."""
        if self._report_data and self._report_data["details"]:
            for detail in self._report_data["details"]:
                if detail.get("ownerGroups"):
                    for group in detail["ownerGroups"]:
                        for owner in group["owners"]:
                            Report._format_address(owner["address"])
                if detail.get("location") and "address" in detail["location"]:
                    Report._format_address(detail["location"]["address"])
                if detail.get("notes"):
                    for note in detail["notes"]:
                        if note.get("contactAddress"):
                            Report._format_address(note["contactAddress"])
                        elif note.get("givingNoticeParty") and note["givingNoticeParty"].get("address"):
                            Report._format_address(note["givingNoticeParty"]["address"])

    def _set_registration_addresses(self):  # pylint: disable=too-many-branches
        """Replace registration addresses country code with description."""
        if self._report_data:
            reg = self._report_data
            if reg.get("submittingParty"):
                Report._format_address(reg["submittingParty"]["address"])
            if reg.get("ownerGroups"):
                for group in reg["ownerGroups"]:
                    for owner in group["owners"]:
                        Report._format_address(owner["address"])
            if reg.get("deleteOwnerGroups"):
                for group in reg["deleteOwnerGroups"]:
                    for owner in group["owners"]:
                        Report._format_address(owner["address"])
            if reg.get("addOwnerGroups"):
                for group in reg["addOwnerGroups"]:
                    for owner in group["owners"]:
                        Report._format_address(owner["address"])
            if reg.get("location") and "address" in reg["location"]:
                Report._format_address(reg["location"]["address"])
            if reg.get("previousLocation") and "address" in reg["previousLocation"]:
                Report._format_address(reg["previousLocation"]["address"])
            if (
                reg.get("note")
                and reg["note"].get("givingNoticeParty")
                and reg["note"]["givingNoticeParty"].get("address")
            ):
                Report._format_address(reg["note"]["givingNoticeParty"]["address"])

    def _set_date_times(self):  # pylint: disable=too-many-statements, too-many-branches
        """Replace API ISO UTC strings with local report format strings."""
        if self._report_key in (ReportTypes.SEARCH_DETAIL_REPORT, ReportTypes.SEARCH_BODY_REPORT):
            self._report_data["searchDateTime"] = Report._to_report_datetime(self._report_data["searchDateTime"])
            if self._report_data["totalResultsSize"] > 0:
                for detail in self._report_data["details"]:
                    detail["createDateTime"] = Report._to_report_datetime(detail["createDateTime"])
                    if detail.get("declaredDateTime"):
                        detail["declaredDateTime"] = Report._to_report_datetime(detail["declaredDateTime"], False)
                    declared_value = str(detail["declaredValue"])
                    if declared_value.isnumeric() and declared_value != "0":
                        detail["declaredValue"] = "$" + "{:0,.2f}".format(float(declared_value))
                    else:
                        detail["declaredValue"] = ""
                    if detail.get("description") and detail["description"].get("engineerDate"):
                        if detail["description"]["engineerDate"] == "0001-01-01":
                            detail["description"]["engineerDate"] = ""
                        else:
                            detail["description"]["engineerDate"] = Report._to_report_datetime(
                                detail["description"]["engineerDate"], False
                            )
                    else:
                        detail["description"]["engineerDate"] = ""
                    if detail.get("location") and detail["location"].get("taxExpiryDate"):
                        detail["location"]["taxExpiryDate"] = Report._to_report_datetime(
                            detail["location"]["taxExpiryDate"], False
                        )
        elif self._report_key == ReportTypes.MHR_REGISTRATION:
            reg = self._report_data
            reg["createDateTime"] = Report._to_report_datetime(reg["createDateTime"])
            if reg.get("description") and reg["description"].get("engineerDate"):
                if reg["description"]["engineerDate"] == "0001-01-01":
                    reg["description"]["engineerDate"] = ""
                else:
                    reg["description"]["engineerDate"] = Report._to_report_datetime(
                        reg["description"]["engineerDate"], False
                    )
            else:
                reg["description"]["engineerDate"] = ""
            if reg.get("location") and reg["location"].get("taxExpiryDate"):
                reg["location"]["taxExpiryDate"] = Report._to_report_datetime(reg["location"]["taxExpiryDate"], False)
        elif self._report_key in (
            ReportTypes.MHR_TRANSFER,
            ReportTypes.MHR_EXEMPTION,
            ReportTypes.MHR_TRANSPORT_PERMIT,
            ReportTypes.MHR_NOTE,
            ReportTypes.MHR_ADMIN_REGISTRATION,
        ):
            reg = self._report_data
            if self._report_key == ReportTypes.MHR_EXEMPTION:
                reg["createDate"] = Report._to_report_datetime(reg["createDateTime"], False)
            reg["createDateTime"] = Report._to_report_datetime(reg["createDateTime"])
            if reg.get("declaredValue"):
                declared_value = str(reg["declaredValue"])
                if declared_value.isnumeric() and declared_value != "0":
                    reg["declaredValue"] = "$" + "{:0,.2f}".format(float(declared_value))
                else:
                    reg["declaredValue"] = ""
            if reg.get("consideration"):
                consideration = str(reg["consideration"])
                if consideration.isnumeric() and consideration != "0":
                    reg["consideration"] = "$" + "{:0,.2f}".format(float(consideration))
            if reg.get("transferDate"):
                reg["transferDate"] = Report._to_report_datetime(reg["transferDate"], False)
            if self._report_key == ReportTypes.MHR_TRANSPORT_PERMIT and reg.get("newLocation"):
                reg["location"] = reg.get("newLocation")
                if reg.get("location") and reg["location"].get("taxExpiryDate"):
                    reg["location"]["taxExpiryDate"] = Report._to_report_datetime(
                        reg["location"]["taxExpiryDate"], False
                    )
            if self._report_key == ReportTypes.MHR_TRANSPORT_PERMIT and (reg.get("amendment") or reg.get("extension")):
                if reg.get("permitDateTime"):
                    reg["permitDateTime"] = Report._to_report_datetime(reg["permitDateTime"])
                    reg["permitExpiryDateTime"] = Report._to_report_datetime(reg["permitExpiryDateTime"], False)
            if reg.get("description") and reg["description"].get("engineerDate"):
                if reg["description"]["engineerDate"] == "0001-01-01":
                    reg["description"]["engineerDate"] = ""
                else:
                    reg["description"]["engineerDate"] = Report._to_report_datetime(
                        reg["description"]["engineerDate"], False
                    )

    def _set_selected(self):
        """Replace selection serial type code with description. Remove unselected items."""
        if "selected" in self._report_data:
            match_size: int = len(self._report_data["selected"])
            has_historical: bool = False
            for index, result in enumerate(self._report_data["selected"], start=0):
                result["createDateTime"] = Report._to_report_datetime(result["createDateTime"], False)
                result["index"] = index + 1
                if result.get("extraMatches"):
                    match_size += len(result.get("extraMatches"))
                if result.get("historicalCount", 0) > 0:
                    has_historical = True
            self._report_data["totalResultsSize"] = len(self._report_data["selected"])
            self._report_data["matchResultsSize"] = match_size
            self._report_data["hasHistorical"] = has_historical

    @staticmethod
    def _format_address(address):
        """Replace address country code with description."""
        if "country" in address and address["country"]:
            country = address["country"]
            if country == "CA":
                address["country"] = "CANADA"
            elif country == "US":
                address["country"] = "UNITED STATES OF AMERICA"
            else:
                try:
                    country: str = pycountry.countries.search_fuzzy(country)[0].name
                    address["country"] = country.upper()
                except (AttributeError, TypeError):
                    address["country"] = country

        return address

    def _set_meta_info(self):
        """Identify environment in report if non-production."""
        self._report_data["environment"] = f"{self._get_environment()}".lstrip()
        self._report_data["meta_account_id"] = self._account_id
        if self._account_name:
            self._report_data["meta_account_name"] = self._account_name

        # Get source ???
        # Appears in the Description section of the PDF Document Properties as Title.
        self._report_data["meta_title"] = ReportMeta.reports[self._report_key]["metaTitle"].upper()
        self._report_data["meta_subtitle"] = ReportMeta.reports[self._report_key]["metaSubtitle"]

        # Appears in the Description section of the PDF Document Properties as Subject.
        if self._report_key in (
            ReportTypes.SEARCH_DETAIL_REPORT,
            ReportTypes.SEARCH_TOC_REPORT,
            ReportTypes.SEARCH_BODY_REPORT,
        ):
            search_type: str = self._report_data["searchQuery"]["type"]
            search_desc: str = TO_SEARCH_DESCRIPTION[search_type]
            criteria: str = ""
            if search_type == "OWNER_NAME":
                criteria = self._report_data["searchQuery"]["criteria"]["ownerName"]["last"] + ", "
                criteria += self._report_data["searchQuery"]["criteria"]["ownerName"]["first"]
                if "middle" in self._report_data["searchQuery"]["criteria"]["ownerName"]:
                    criteria += " " + self._report_data["searchQuery"]["criteria"]["ownerName"]["middle"]
            else:
                criteria = self._report_data["searchQuery"]["criteria"]["value"].upper()
            self._report_data["meta_subject"] = f'{search_desc} - "{criteria}"'
            if search_type == "MHR_NUMBER":
                self._report_data["footer_content"] = f'MHR Number Search - "{criteria}"'
            else:
                self._report_data["footer_content"] = f'MHR {search_desc} Search - "{criteria}"'
        elif self._report_key in (
            ReportTypes.MHR_REGISTRATION,
            ReportTypes.MHR_COVER,
            ReportTypes.MHR_TRANSFER,
            ReportTypes.MHR_EXEMPTION,
            ReportTypes.MHR_NOTE,
            ReportTypes.MHR_TRANSPORT_PERMIT,
            ReportTypes.MHR_REGISTRATION_COVER,
            ReportTypes.MHR_TOD_REJECTION,
        ):
            reg_num = self._report_data.get("mhrNumber", "")
            self._report_data["footer_content"] = f"Manufactured Home Registration #{reg_num}"
            self._report_data["meta_subject"] = f"Manufactured Home Registration Number: {reg_num}"
        if self._get_environment() != "":
            self._report_data["footer_content"] = "TEST DATA | " + self._report_data["footer_content"]

    @staticmethod
    def _get_environment():
        """Identify environment in report if non-production."""
        deploy_env = current_app.config.get("DEPLOYMENT_ENV").lower()
        if deploy_env.startswith("dev"):
            return "DEV"
        if deploy_env.startswith("test"):
            return "TEST"
        if deploy_env.startswith("sand"):
            return "SANDBOX"
        return ""

    @staticmethod
    def _to_report_datetime(date_time: str, include_time: bool = True):  # Remove: , expiry: bool = False):
        """Convert ISO formatted date time or date string to report format."""
        if len(date_time) < 10:  # Legacy may be empty string.
            return date_time
        if len(date_time) == 10:  # Legacy has some date only data.
            report_date = model_utils.date_from_iso_format(date_time)
            return report_date.strftime("%B %-d, %Y")
        zone = date_time[20:]
        local_datetime = None
        if not zone.endswith("00"):  # Coming from legacy, already local so ignore timezone adjustment.
            local_datetime = model_utils.ts_from_iso_format_local(date_time)
            # logger.info(f'zone={zone} date_time={date_time}')
        else:
            local_datetime = model_utils.to_local_timestamp(model_utils.ts_from_iso_format(date_time))
        if include_time:
            timestamp = local_datetime.strftime("%B %-d, %Y at %-I:%M:%S %p Pacific time")
            if timestamp.find(" AM ") > 0:
                return timestamp.replace(" AM ", " am ")
            return timestamp.replace(" PM ", " pm ")

        return local_datetime.strftime("%B %-d, %Y")


class ReportMeta:  # pylint: disable=too-few-public-methods
    """Helper class to maintain the report meta information."""

    reports = {
        ReportTypes.MHR_COVER: {
            "reportDescription": "MHRCover",
            "fileName": "coverV2",
            "metaTitle": "VERIFICATION OF SERVICE",
            "metaSubtitle": " Manufactured Home Act",
            "metaSubject": "",
        },
        ReportTypes.MHR_REGISTRATION: {
            "reportDescription": "MHRRegistration",
            "fileName": "registrationV2",
            "metaTitle": "VERIFICATION OF SERVICE",
            "metaSubtitle": " Manufactured Home Act",
            "metaSubject": "",
        },
        ReportTypes.MHR_REGISTRATION_COVER: {
            "reportDescription": "MHRRegistrationCover",
            "fileName": "registrationCoverV2",
            "metaTitle": "MANUFACTURED HOME REGISTRY",
            "metaSubtitle": "BC Registries and Online Services",
            "metaSubject": "",
        },
        ReportTypes.SEARCH_DETAIL_REPORT: {
            "reportDescription": "SearchResult",
            "fileName": "searchResultV2",
            "metaTitle": "Manufactured Home Registry Search Result",
            "metaSubtitle": "BC Registries and Online Services",
            "metaSubject": "",
        },
        ReportTypes.SEARCH_TOC_REPORT: {
            "reportDescription": "SearchResult",
            "fileName": "searchResultTOCV2",
            "metaTitle": "Personal Property Registry Search Result",
            "metaSubtitle": "BC Registries and Online Services",
            "metaSubject": "",
        },
        ReportTypes.SEARCH_BODY_REPORT: {
            "reportDescription": "SearchResult",
            "fileName": "searchResultBodyV2",
            "metaTitle": "Manufactured Home Registry Search Result",
            "metaSubtitle": "BC Registries and Online Services",
            "metaSubject": "",
        },
        ReportTypes.MHR_TRANSFER: {
            "reportDescription": "MHRTransfer",
            "fileName": "transferV2",
            "metaTitle": "OWNERSHIP TRANSFER OR CHANGE",
            "metaSubtitle": " Manufactured Home Act",
            "metaSubject": "",
        },
        ReportTypes.MHR_EXEMPTION: {
            "reportDescription": "MHRExemption",
            "fileName": "exemptionV2",
            "metaTitle": "EXEMPTION VERIFICATION",
            "metaSubtitle": " Manufactured Home Act",
            "metaSubject": "",
        },
        ReportTypes.MHR_TRANSPORT_PERMIT: {
            "reportDescription": "MHRTransportPermit",
            "fileName": "transportPermitV2",
            "metaTitle": "TRANSPORT PERMIT VERIFICATION",
            "metaSubtitle": " Manufactured Home Act",
            "metaSubject": "",
        },
        ReportTypes.MHR_NOTE: {
            "reportDescription": "MHRNote",
            "fileName": "unitNoteV2",
            "metaTitle": "UNIT NOTE VERIFICATION",
            "metaSubtitle": " Manufactured Home Act",
            "metaSubject": "",
        },
        ReportTypes.MHR_ADMIN_REGISTRATION: {
            "reportDescription": "MHRAdminRegistration",
            "fileName": "adminRegistrationV2",
            "metaTitle": "REPLACED",
            "metaSubtitle": " Manufactured Home Act",
            "metaSubject": "",
        },
        ReportTypes.MHR_TOD_REJECTION: {
            "reportDescription": "MHRTODRejection",
            "fileName": "rejectionV2",
            "metaTitle": "REJECTION NOTICE",
            "metaSubtitle": " Manufactured Home Act",
            "metaSubject": "",
        },
    }
