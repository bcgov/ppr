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

"""This module holds methods to support registration model updates - mostly account registration summary."""
from sqlalchemy.sql import text

from ppr_api.models import utils as model_utils
from ppr_api.services.authz import is_all_staff_account
from ppr_api.utils.logging import logger

from .db import db
from .securities_act_notice import SecuritiesActNotice

PARAM_TO_ORDER_BY = {
    "registrationNumber": "registration_number",
    "registrationType": "registration_type",
    "registeringName": "registering_name",
    "clientReferenceId": "client_reference_id",
    "startDateTime": "registration_ts",
    "endDateTime": "registration_ts",
}
PARAM_TO_ORDER_BY_CHANGE = {
    "registrationNumber": "arv2.registration_number",
    "registrationType": "arv2.registration_type",
    "registeringName": "arv2.registering_name",
    "clientReferenceId": "arv2.client_reference_id",
    "startDateTime": "arv2.registration_ts",
    "endDateTime": "arv2.registration_ts",
}

FINANCING_PATH = "/ppr/api/v1/financing-statements/"
QUERY_ACCOUNT_REG_DEFAULT_ORDER = " ORDER BY registration_ts DESC"
QUERY_ACCOUNT_CHANGE_DEFAULT_ORDER = " ORDER BY arv2.registration_ts DESC"
QUERY_ACCOUNT_REG_LIMIT = " LIMIT :page_size OFFSET :page_offset"
QUERY_ACCOUNT_REG_NUM_CLAUSE = """
 AND (arv.registration_number LIKE :reg_num || '%' OR
      EXISTS (SELECT arv2.financing_id
                FROM account_registration_vw arv2
               WHERE arv2.financing_id = arv.financing_id
                 AND arv2.registration_type_cl NOT IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN')
                 AND arv2.registration_number LIKE :reg_num || '%'))
"""
QUERY_ACCOUNT_CLIENT_REF_CLAUSE = " AND arv.client_reference_id LIKE '%' || :client_reference_id || '%'"
QUERY_ACCOUNT_CLIENT_REF_CLAUSE_NEW = """
 AND (arv.client_reference_id ILIKE '%' || :client_reference_id || '%' OR
    EXISTS (SELECT arv2.financing_id
            FROM account_registration_vw arv2
            WHERE arv2.financing_id = arv.financing_id
                AND arv2.registration_type_cl NOT IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN')
                AND arv2.client_reference_id ILIKE :client_reference_id || '%'))
"""
QUERY_ACCOUNT_REG_NAME_CLAUSE = " AND arv.registering_name LIKE '%' || :registering_name || '%'"
QUERY_ACCOUNT_REG_NAME_CLAUSE_NEW = """
 AND (arv.registering_name ILIKE '%' || :registering_name || '%' OR
    EXISTS (SELECT arv2.financing_id
            FROM account_registration_vw arv2
            WHERE arv2.financing_id = arv.financing_id
                AND arv2.registration_type_cl NOT IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN')
                AND arv2.registering_name ILIKE '%' || :registering_name || '%'))
"""
QUERY_ACCOUNT_STATUS_CLAUSE = " AND arv.state = :status_type"
QUERY_ACCOUNT_REG_TYPE_CLAUSE = " AND arv.registration_type = :registration_type"
QUERY_ACCOUNT_REG_DATE_CLAUSE = """
 AND arv.registration_ts BETWEEN TO_TIMESTAMP(start_ts) AND TO_TIMESTAMP(end_ts)
 """
QUERY_ACCOUNT_CHANGE_REG_CLASS_CLAUSE = " AND arv2.registration_type_cl IN ('CROWNLIEN', 'MISCLIEN', 'PPSALIEN')"
QUERY_ACCOUNT_CHANGE_REG_NUM_CLAUSE = " AND arv2.registration_number LIKE :reg_num || '%'"
QUERY_ACCOUNT_CHANGE_CLIENT_REF_CLAUSE = " AND arv2.client_reference_id LIKE :client_reference_id || '%'"
QUERY_ACCOUNT_CHANGE_REG_NAME_CLAUSE = " AND arv2.registering_name LIKE '%' || :registering_name || '%'"
QUERY_ACCOUNT_CHANGE_STATUS_CLAUSE = " AND arv2.state = :status_type"
QUERY_ACCOUNT_CHANGE_REG_TYPE_CLAUSE = " AND arv2.registration_type = :registration_type"
QUERY_ACCOUNT_CHANGE_REG_DATE_CLAUSE = """
 AND arv2.registration_ts BETWEEN TO_TIMESTAMP(start_ts) AND TO_TIMESTAMP(end_ts)
 """
QUERY_UPDATE_ACCOUNT_ID_REMOVE = """
UPDATE registrations
   SET account_id = account_id || '_R'
 WHERE account_id = :query_account
   AND financing_id = (SELECT fs.id
                         FROM financing_statements fs, registrations r
                        WHERE r.financing_id = fs.id
                          AND r.registration_number = :query_reg_num)
"""
QUERY_UPDATE_ACCOUNT_ID_RESTORE = """
UPDATE registrations
   SET account_id = :query_account
 WHERE account_id = :query_account || '_R'
   AND financing_id = (SELECT fs.id
                         FROM financing_statements fs, registrations r
                        WHERE r.financing_id = fs.id
                          AND r.registration_number = :query_reg_num)
"""
GC_LEGACY_STATUS_ADDED = "A"
GC_LEGACY_STATUS_DELETED = "D"


class AccountRegistrationParams:
    """Contains parameter values to use when querying account summary registration information."""

    account_id: str
    collapse: bool = False
    account_name: str = None
    sbc_staff: bool = False
    from_ui: bool = False
    sort_direction: str = "desc"
    page_number: int = 1
    sort_criteria: str = None
    registration_number: str = None
    registration_type: str = None
    start_date_time: str = None
    end_date_time: str = None
    status_type: str = None
    client_reference_id: str = None
    registering_name: str = None

    def __init__(self, account_id, collapse: bool = False, account_name: str = None, sbc_staff: bool = False):
        """Set common base initialization."""
        self.account_id = account_id
        self.account_name = account_name
        self.collapse = collapse
        self.sbc_staff = sbc_staff


def can_access_report(account_id: str, account_name: str, reg_json, sbc_staff: bool = False) -> bool:
    """Determine if request account can view the registration verification statement."""
    # All staff roles can see any verification statement.
    reg_account_id = reg_json["accountId"]
    if is_all_staff_account(account_id) or sbc_staff:
        return True
    if reg_account_id in (account_id, account_id + "_R"):
        return True
    if account_name:
        if reg_json["registeringParty"] == account_name:
            return True
        sp_names = reg_json["securedParties"]
        if sp_names and account_name in sp_names:
            return True
    return False


def update_summary_optional(reg_json, account_id: str, sbc_staff: bool = False):
    """Single summary result replace optional property 'None' with ''."""
    if not reg_json["registeringName"] or reg_json["registeringName"].lower() == "none":
        reg_json["registeringName"] = ""
    # Only staff role or matching account includes registeringName
    elif (
        not is_all_staff_account(account_id)
        and not sbc_staff
        and "accountId" in reg_json
        and reg_json["accountId"] not in (account_id, account_id + "_R")
    ):
        reg_json["registeringName"] = ""

    if not reg_json["clientReferenceId"] or reg_json["clientReferenceId"].lower() == "none":
        reg_json["clientReferenceId"] = ""
    return reg_json


def build_account_collapsed_json(financing_json, registrations_json):
    """Organize account registrations as parent/child financing statement/change registrations."""
    for statement in financing_json:
        changes = []
        for registration in registrations_json:
            if statement["registrationNumber"] == registration["baseRegistrationNumber"]:
                changes.append(registration)
        if changes:
            statement["changes"] = changes
    return financing_json


def build_account_collapsed_filter_json(
    financing_json, registrations_json, params: AccountRegistrationParams, api_filter: bool = False
):
    """Organize account registrations as parent/child financing statement/change registrations."""
    for statement in financing_json:
        changes = []
        for registration in registrations_json:
            if statement["registrationNumber"] == registration["baseRegistrationNumber"]:
                changes.append(registration)
                if (
                    not api_filter
                    and params.registration_number
                    and registration["registrationNumber"].startswith(params.registration_number)
                ):
                    statement["expand"] = True
                elif (
                    not api_filter
                    and params.client_reference_id
                    and registration["clientReferenceId"].upper().startswith(params.client_reference_id.upper())
                ):
                    statement["expand"] = True
                elif (
                    not api_filter
                    and params.registering_name
                    and params.registering_name.upper() in registration["registeringName"].upper()
                ):
                    statement["expand"] = True
        if changes:
            statement["changes"] = changes
    return financing_json


def set_path(params: AccountRegistrationParams, result, reg_num: str, base_reg_num: str, pending_count: int = 0):
    """Set path to the verification statement."""
    reg_class = result["registrationClass"]
    if model_utils.is_financing(reg_class):
        result["baseRegistrationNumber"] = reg_num
        result["path"] = FINANCING_PATH + reg_num
    elif reg_class == model_utils.REG_CLASS_DISCHARGE:
        result["path"] = FINANCING_PATH + base_reg_num + "/discharges/" + reg_num
    elif reg_class == model_utils.REG_CLASS_RENEWAL:
        result["path"] = FINANCING_PATH + base_reg_num + "/renewals/" + reg_num
    elif reg_class == model_utils.REG_CLASS_CHANGE:
        result["path"] = FINANCING_PATH + base_reg_num + "/changes/" + reg_num
    elif reg_class in (model_utils.REG_CLASS_AMEND, model_utils.REG_CLASS_AMEND_COURT):
        result["path"] = FINANCING_PATH + base_reg_num + "/amendments/" + reg_num

    if not can_access_report(params.account_id, params.account_name, result, params.sbc_staff):
        result["path"] = ""
    elif pending_count > 0:
        # Allow report regeneration if pending and > 15 minutes has elapsed.
        last_ts = model_utils.ts_from_iso_format(result["lastUpdateDateTime"])
        if not model_utils.report_retry_elapsed(last_ts):
            result["path"] = ""
    return result


def get_account_reg_query_order(params: AccountRegistrationParams) -> str:
    """Get the account registration query order by clause from the provided parameters."""
    order_by: str = QUERY_ACCOUNT_REG_DEFAULT_ORDER
    if not params.sort_criteria:
        return order_by
    if param_order_by := PARAM_TO_ORDER_BY.get(params.sort_criteria, None):
        sort_order = "DESC"
        if params.sort_direction and params.sort_direction in ("asc", "ascending", "desc", "descending"):
            sort_order = params.sort_direction
        order_by = " ORDER BY " + param_order_by + " " + sort_order
    return order_by


def get_account_change_query_order(params: AccountRegistrationParams) -> str:
    """Get the account change registration query order by clause from the provided parameters."""
    order_by: str = QUERY_ACCOUNT_CHANGE_DEFAULT_ORDER
    if not params.sort_criteria:
        return order_by
    if param_order_by := PARAM_TO_ORDER_BY_CHANGE.get(params.sort_criteria, None):
        sort_order = "DESC"
        if params.sort_direction and params.sort_direction in ("asc", "ascending", "desc", "descending"):
            sort_order = params.sort_direction
        order_by = " ORDER BY " + param_order_by + " " + sort_order
    return order_by


def build_account_reg_base_query(params: AccountRegistrationParams, new_feature_enabled: bool) -> str:
    """Build the account registration base query from the provided parameters."""
    base_query: str = model_utils.QUERY_ACCOUNT_BASE_REG_BASE
    if params.start_date_time and params.end_date_time:
        base_query = model_utils.QUERY_ACCOUNT_BASE_REG_SUBQUERY
        base_query += build_reg_date_clause(params, True)
    if params.registration_number:
        base_query += QUERY_ACCOUNT_REG_NUM_CLAUSE
    if params.registration_type:
        base_query += QUERY_ACCOUNT_REG_TYPE_CLAUSE
    if params.client_reference_id:
        if new_feature_enabled:
            base_query += QUERY_ACCOUNT_CLIENT_REF_CLAUSE_NEW
        else:
            base_query += QUERY_ACCOUNT_CLIENT_REF_CLAUSE
    if params.registering_name:
        if new_feature_enabled:
            base_query += QUERY_ACCOUNT_REG_NAME_CLAUSE_NEW
        else:
            base_query += QUERY_ACCOUNT_REG_NAME_CLAUSE
    if params.status_type:
        base_query += QUERY_ACCOUNT_STATUS_CLAUSE
    return base_query


def build_reg_date_clause(params: AccountRegistrationParams, base_query: bool) -> str:
    """Build the account registration base query date range clause from the provided parameters."""
    clause: str = QUERY_ACCOUNT_REG_DATE_CLAUSE if base_query else QUERY_ACCOUNT_CHANGE_REG_DATE_CLAUSE
    start_ts: str = str(model_utils.ts_from_iso_format(params.start_date_time).timestamp())
    end_ts: str = str(model_utils.ts_from_iso_format(params.end_date_time).timestamp())
    clause = clause.replace("start_ts", start_ts)
    clause = clause.replace("end_ts", end_ts)
    return clause


def build_account_change_base_query(params: AccountRegistrationParams) -> str:
    """Build the account change registration base query from the provided parameters."""
    base_query: str = model_utils.QUERY_ACCOUNT_CHANGE_REG_BASE
    if not params.registration_number and not params.client_reference_id:
        base_query += QUERY_ACCOUNT_CHANGE_REG_CLASS_CLAUSE
    if params.registration_number:
        base_query += QUERY_ACCOUNT_CHANGE_REG_NUM_CLAUSE
    if params.registration_type:
        base_query += QUERY_ACCOUNT_CHANGE_REG_TYPE_CLAUSE
    if params.client_reference_id:
        base_query += QUERY_ACCOUNT_CHANGE_CLIENT_REF_CLAUSE
    if params.registering_name:
        base_query += QUERY_ACCOUNT_CHANGE_REG_NAME_CLAUSE
    if params.status_type:
        base_query += QUERY_ACCOUNT_CHANGE_STATUS_CLAUSE
    if params.start_date_time and params.end_date_time:
        base_query += build_reg_date_clause(params, False)
    order_by: str = get_account_change_query_order(params)
    base_query += order_by
    base_query += QUERY_ACCOUNT_REG_LIMIT
    return base_query


def build_account_reg_query(params: AccountRegistrationParams, new_feature_enabled: bool) -> str:
    """Build the account registration query from the provided parameters."""
    base_query: str = build_account_reg_base_query(params, new_feature_enabled)
    order_by: str = get_account_reg_query_order(params)
    query: str
    if params.start_date_time and params.end_date_time:
        query = model_utils.QUERY_ACCOUNT_BASE_REG_FILTER.replace("QUERY_ACCOUNT_BASE_REG_SUBQUERY", base_query)
    else:
        query = "SELECT * FROM (" + base_query + ") AS q "
    query += order_by
    query += QUERY_ACCOUNT_REG_LIMIT
    return query


def build_account_change_query(params: AccountRegistrationParams, base_json: dict = None) -> str:
    """Build the account registration change query from the provided parameters."""
    if base_json:  # and params.start_date_time and params.end_date_time:
        reg_nums: str = None
        for reg in base_json:
            if reg_nums is None:
                reg_nums = "'" + reg["registrationNumber"] + "'"
            else:
                reg_nums += ",'" + reg["registrationNumber"] + "'"
        query: str = model_utils.QUERY_ACCOUNT_CHANGE_REG_FILTER.replace("BASE_REG_LIST", reg_nums)
        return query

    base_query: str = build_account_change_base_query(params)
    query: str = model_utils.QUERY_ACCOUNT_CHANGE_REG.replace("QUERY_ACCOUNT_CHANGE_REG_BASE", base_query)
    return query


def build_account_query_params(params: AccountRegistrationParams, api_filter: bool = False) -> dict:
    """Build the account query runtime parameter set from the provided parameters."""
    page_size: int = (
        model_utils.MAX_ACCOUNT_REGISTRATIONS_DEFAULT if api_filter else model_utils.get_max_registrations_size()
    )
    page_offset: int = params.page_number
    if page_offset <= 1:
        page_offset = 0
    else:
        page_offset = (page_offset - 1) * page_size
    query_params = {"query_account": params.account_id, "page_size": page_size, "page_offset": page_offset}
    if params.registration_number:
        query_params["reg_num"] = params.registration_number.upper()
    if params.registration_type:
        query_params["registration_type"] = params.registration_type
    if params.client_reference_id:
        query_params["client_reference_id"] = params.client_reference_id
    if params.registering_name:
        query_params["registering_name"] = params.registering_name
    if params.status_type:
        query_params["status_type"] = params.status_type
    return query_params


def build_account_base_reg_results(params, rows, api_filter: bool = False) -> dict:
    """Build the account query base registration results from the query result set."""
    results_json = []
    if rows is not None:
        for row in rows:
            reg_class = str(row[3])
            if model_utils.is_financing(reg_class):
                results_json.append(__build_account_reg_result(params, row, reg_class, api_filter))

    return results_json


def update_account_reg_results(params, rows, results_json, api_filter: bool = False) -> dict:
    """Build the account query base registration results from the query result set."""
    if results_json and rows is not None:
        changes_json = []
        last_reg_num: str = ""
        for row in rows:
            reg_class = str(row[3])
            if not model_utils.is_financing(reg_class):
                # This is faster than eliminating duplicates in the db query.
                reg_summary = __build_account_reg_result(params, row, reg_class, api_filter)
                if not last_reg_num:
                    last_reg_num = reg_summary["registrationNumber"]
                    changes_json.append(reg_summary)
                elif last_reg_num != reg_summary["registrationNumber"]:
                    last_reg_num = reg_summary["registrationNumber"]
                    changes_json.append(reg_summary)
        if changes_json:
            return build_account_collapsed_filter_json(results_json, changes_json, params, api_filter)
    return results_json


def __build_account_reg_result(params, row, reg_class, api_filter: bool = False) -> dict:
    """Build a registration result from a query result set row."""
    reg_num = str(row[0])
    base_reg_num = str(row[6])
    result = {
        "accountId": str(row[14]),
        "registrationNumber": reg_num,
        "baseRegistrationNumber": base_reg_num,
        "createDateTime": model_utils.format_ts(row[1]),
        "registrationType": str(row[2]),
        "registrationDescription": str(row[5]),
        "registrationClass": reg_class,
        "statusType": str(row[7]),
        "expireDays": int(row[8]),
        "lastUpdateDateTime": model_utils.format_ts(row[9]),
        "registeringParty": str(row[10]),
        "securedParties": str(row[11]),
        "clientReferenceId": str(row[12]),
        "registeringName": str(row[13]) if row[13] else "",
    }
    if not api_filter:
        result["vehicleCount"] = int(row[16])
    result["legacy"] = result.get("accountId") == "0"
    if model_utils.is_financing(reg_class) and not api_filter:
        result["expand"] = False
    result = set_path(params, result, reg_num, base_reg_num, int(row[15]))
    result = update_summary_optional(result, params.account_id, params.sbc_staff)
    if "accountId" in result:
        del result["accountId"]  # Only use this for report access checking.
    return result


def api_account_reg_filter(params: AccountRegistrationParams) -> bool:
    """Check if api account registration summary request includes filter parameters.

    Filter parameters may be a client reference ID, a timestamp range, or a registration number.
    """
    if not params.from_ui and (
        params.client_reference_id or params.registration_number or (params.start_date_time and params.end_date_time)
    ):
        return True
    return False


def create_securities_act_notices(registration, json_data: dict):
    """Conditionally create securities act notices based on registration type."""
    if registration.registration_type == model_utils.REG_TYPE_SECURITIES_NOTICE and json_data.get(
        "securitiesActNotices"
    ):
        notices = []
        for notice_json in json_data.get("securitiesActNotices"):
            notices.append(SecuritiesActNotice.create_from_json(notice_json, registration.id))
        registration.securities_act_notices = notices
    return registration


def get_securities_act_notices_count(statement, json_data: dict) -> int:
    """Count the current securities act notices: with amendments there must be at least one active."""
    count: int = 0
    if json_data.get("addSecuritiesActNotices"):
        count = len(json_data.get("addSecuritiesActNotices"))
        logger.debug(f"add notice count={count}")
    if statement:
        for reg in statement.registration:
            if reg.securities_act_notices:
                for notice in reg.securities_act_notices:
                    if notice.registration_id_end is None:
                        count += 1
    logger.debug(f"total current + added notice count={count}")
    return count


def find_securities_notice_by_id(notice_id: int, statement) -> SecuritiesActNotice:
    """Search existing registration securities act notices for a matching notice id."""
    if notice_id and statement:
        for reg in statement.registration:
            if reg.securities_act_notices:
                for notice in reg.securities_act_notices:
                    if notice.id == notice_id:
                        return notice
    return None


def set_add_general_collateral_json(registration, json_data, registration_id):
    """Build general collateral added as part of the registration."""
    collateral = []
    if registration.general_collateral_legacy:
        for gen_c in registration.general_collateral_legacy:
            if gen_c.registration_id == registration_id and gen_c.status == GC_LEGACY_STATUS_ADDED:
                collateral.append(gen_c.json)
    if registration.general_collateral:
        for gen_c in registration.general_collateral:
            if gen_c.registration_id == registration_id and gen_c.status == GC_LEGACY_STATUS_ADDED:
                collateral.append(gen_c.json)
    if collateral:
        json_data["addGeneralCollateral"] = collateral


def set_delete_general_collateral_json(registration, json_data, registration_id):
    """Build general collateral deleted as part of the registration."""
    collateral = []
    if registration.financing_statement.general_collateral_legacy:
        for gen_c in registration.financing_statement.general_collateral_legacy:
            if registration_id == gen_c.registration_id_end or (
                registration_id == gen_c.registration_id and gen_c.status == GC_LEGACY_STATUS_DELETED
            ):
                collateral.append(gen_c.json)
    if registration.financing_statement.general_collateral:
        for gen_c in registration.financing_statement.general_collateral:
            if registration_id == gen_c.registration_id_end or (
                registration_id == gen_c.registration_id and gen_c.status == GC_LEGACY_STATUS_DELETED
            ):
                collateral.append(gen_c.json)
    if not collateral and registration.general_collateral:
        for gen_c in registration.general_collateral:
            if registration_id == gen_c.registration_id_end or (
                registration_id == gen_c.registration_id and gen_c.status == GC_LEGACY_STATUS_DELETED
            ):
                collateral.append(gen_c.json)
    if collateral:
        json_data["deleteGeneralCollateral"] = collateral


def set_vehicle_collateral_json(registration, json_data, registration_id):
    """Build vehicle collateral added or removed as part of the the amendment/change registration."""
    # add vehicle collateral
    if registration.vehicle_collateral:
        add_collateral = []
        for vehicle_c in registration.vehicle_collateral:
            if vehicle_c.registration_id == registration_id:
                collateral_json = vehicle_c.json
                collateral_json["reg_id"] = registration_id
                add_collateral.append(collateral_json)
        if add_collateral:
            json_data["addVehicleCollateral"] = add_collateral
    # delete vehicle collateral
    if registration.financing_statement.vehicle_collateral:
        del_collateral = []
        for vehicle_c in registration.financing_statement.vehicle_collateral:
            if vehicle_c.registration_id_end == registration_id:
                collateral_json = vehicle_c.json
                collateral_json["reg_id"] = registration_id
                del_collateral.append(collateral_json)
        if del_collateral:
            json_data["deleteVehicleCollateral"] = del_collateral


def set_securities_notices_json(registration, json_data, registration_id):
    """Build securities act notices added or removed as part of the the amendment registration."""
    if registration.financing_statement.registration[0].registration_type != model_utils.REG_TYPE_SECURITIES_NOTICE:
        return
    # add notice
    if registration.securities_act_notices:
        add_notice = []
        for notice in registration.securities_act_notices:
            if notice.registration_id == registration_id:
                notice_json = notice.json
                notice_json["reg_id"] = registration_id
                add_notice.append(notice_json)
        if add_notice:
            json_data["addSecuritiesActNotices"] = add_notice
    # delete notice
    del_notice = []
    for reg in registration.financing_statement.registration:
        if reg.securities_act_notices:
            for notice in reg.securities_act_notices:
                if notice.registration_id_end == registration_id:
                    notice_json = notice.json
                    notice_json["reg_id"] = registration_id
                    del_notice.append(notice_json)
    if del_notice:
        json_data["deleteSecuritiesActNotices"] = del_notice


def update_account_reg_remove(account_id: str, reg_num: str) -> int:
    """Mark registrations created by an account as removed by appending _R to the account id."""
    db.session.execute(text(QUERY_UPDATE_ACCOUNT_ID_REMOVE), {"query_account": account_id, "query_reg_num": reg_num})
    logger.info(f"update_account_reg_remove account={account_id} reg_num={reg_num}")
    db.session.commit()


def update_account_reg_restore(account_id: str, reg_num: str):
    """Mark registrations created by an account as restored by removing _R from the end of the account id."""
    db.session.execute(text(QUERY_UPDATE_ACCOUNT_ID_RESTORE), {"query_account": account_id, "query_reg_num": reg_num})
    logger.info(f"update_account_reg_restore account={account_id} reg_num={reg_num}")
    db.session.commit()
