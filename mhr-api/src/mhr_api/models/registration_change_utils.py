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

# pylint: disable=too-few-public-methods

"""This module holds additional methods to support registration model updates."""
from mhr_api.models import MhrLocation
from mhr_api.models import utils as model_utils
from mhr_api.models.db import db
from mhr_api.models.type_tables import MhrDocumentTypes, MhrNoteStatusTypes, MhrRegistrationStatusTypes, MhrStatusTypes
from mhr_api.utils.logging import logger


def save_exemption(registration, new_reg_id: int):
    """Set the state of the original MH registration to exempt."""
    registration.status_type = MhrRegistrationStatusTypes.EXEMPT
    if registration.change_registrations:  # Close out active transport permit without reverting location.
        for reg in registration.change_registrations:
            if (
                reg.notes
                and reg.notes[0].document_type
                in (MhrDocumentTypes.REG_103, MhrDocumentTypes.REG_103E, MhrDocumentTypes.AMEND_PERMIT)
                and reg.notes[0].status_type == MhrNoteStatusTypes.ACTIVE
            ):
                note = reg.notes[0]
                note.status_type = MhrNoteStatusTypes.CANCELLED
                note.change_registration_id = new_reg_id
    db.session.commit()


def save_transfer(registration, json_data, new_reg_id):
    """Update the original MH removed owner groups."""
    registration.remove_groups(json_data, new_reg_id)
    db.session.commit()


def save_permit(registration, json_data, new_reg_id):
    """Update the existing location state to historical."""
    if registration.locations and registration.locations[0].status_type == MhrStatusTypes.ACTIVE:
        registration.locations[0].status_type = MhrStatusTypes.HISTORICAL
        registration.locations[0].change_registration_id = new_reg_id
    elif registration.change_registrations:
        for reg in registration.change_registrations:  # Updating a change registration location.
            for existing in reg.locations:
                if existing.status_type == MhrStatusTypes.ACTIVE and existing.registration_id != new_reg_id:
                    existing.status_type = MhrStatusTypes.HISTORICAL
                    existing.change_registration_id = new_reg_id
            if reg.notes:
                note = reg.notes[0]
                if (
                    json_data.get("moveCompleted")
                    and note.document_type == MhrDocumentTypes.REG_103
                    and note.status_type == MhrNoteStatusTypes.ACTIVE
                    and not note.is_expired()
                ):
                    note.status_type = MhrNoteStatusTypes.COMPLETED
                    note.change_registration_id = new_reg_id
                    logger.debug(f"save_permit setting note status to completed reg id={new_reg_id}")
                elif (
                    note.document_type
                    in (MhrDocumentTypes.REG_103, MhrDocumentTypes.REG_103E, MhrDocumentTypes.AMEND_PERMIT)
                    and note.status_type == MhrNoteStatusTypes.ACTIVE
                    and not note.is_expired()
                ):
                    note.status_type = MhrNoteStatusTypes.CANCELLED
                    note.change_registration_id = new_reg_id
    if json_data and json_data.get("documentType") == MhrDocumentTypes.CANCEL_PERMIT:
        if (
            registration.status_type
            and registration.status_type == MhrRegistrationStatusTypes.EXEMPT
            and json_data.get("location")
            and json_data["location"]["address"]["region"] == model_utils.PROVINCE_BC
        ):
            registration.status_type = MhrRegistrationStatusTypes.ACTIVE
            logger.info("Cancel Transport Permit new location in BC, updating EXEMPT status to ACTIVE.")
    elif (
        json_data
        and json_data.get("amendment")
        and registration.status_type == MhrRegistrationStatusTypes.EXEMPT
        and json_data["newLocation"]["address"]["region"] == model_utils.PROVINCE_BC
    ):
        registration.status_type = MhrRegistrationStatusTypes.ACTIVE
        logger.info("Amend Transport Permit new location in BC, updating EXEMPT status to ACTIVE.")
    elif (
        json_data
        and json_data["newLocation"]["address"]["region"] != model_utils.PROVINCE_BC
        and json_data.get("documentType", "") != MhrDocumentTypes.CANCEL_PERMIT
    ):
        registration.status_type = MhrRegistrationStatusTypes.EXEMPT
        logger.info("Transport Permit new location out of province, updating status to EXEMPT.")
    db.session.commit()


def setup_permit_extension_location(base_reg, registration, new_loc_json: dict):
    """REG_103E location does not change so clone the active location."""
    if not base_reg.change_registrations:
        return
    logger.info("Permit extension looking up existing location.")
    for reg in base_reg.change_registrations:
        if reg.locations and reg.locations[0].status_type == MhrStatusTypes.ACTIVE:
            current_loc = reg.locations[0]
            location: MhrLocation = MhrLocation.create_from_json(current_loc.json, registration.id)
            location.registration_id = registration.id
            location.change_registration_id = registration.id
            logger.info("Permit extension cloned existing location.")
            if new_loc_json:
                if "taxCertificate" in new_loc_json:
                    location.tax_certification = "Y" if new_loc_json.get("taxCertificate") else "N"
                if new_loc_json.get("taxExpiryDate", None):
                    location.tax_certification_date = model_utils.ts_from_iso_format(new_loc_json.get("taxExpiryDate"))
            registration.locations.append(location)
            break
