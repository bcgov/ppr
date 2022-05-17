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
from datetime import timedelta

import markupsafe
import pycountry

from mhr_api.models import utils as model_utils


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
    'AC': 'Collateral Addition',
    'AA': 'Collateral Addition',
    'AM': 'Amendment',
    'CO': 'Court Order',
    'DR': 'Debtor Release',
    'AR': 'Debtor Release',
    'DT': 'Debtor Transfer',
    'AD': 'Debtor Transfer',
    'PD': 'Partial Discharge',
    'AP': 'Partial Discharge',
    'ST': 'Secured Party Transfer',
    'AS': 'Secured Party Transfer',
    'SU': 'Collateral Substitution',
    'AU': 'Collateral Substitution',
    'RC': 'Registry Correction'
}


def set_ppr_template_data(report_data):
    """Set up the PPR search data for the report, modifying the original for the template output."""
    set_addresses(report_data)
    set_date_times(report_data)
    set_vehicle_collateral(report_data)
    set_general_collateral(report_data)


def format_address(address):
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


def set_financing_addresses(statement):
    """Replace financing statement addresses country code with description."""
    format_address(statement['registeringParty']['address'])
    for secured_party in statement['securedParties']:
        format_address(secured_party['address'])
    for debtor in statement['debtors']:
        format_address(debtor['address'])


def set_amend_change_addresses(statement):
    """Replace amendment/change statement address country code with description."""
    format_address(statement['registeringParty']['address'])
    if 'deleteSecuredParties' in statement:
        for delete_secured in statement['deleteSecuredParties']:
            format_address(delete_secured['address'])
    if 'addSecuredParties' in statement:
        for add_secured in statement['addSecuredParties']:
            format_address(add_secured['address'])
    if 'deleteDebtors' in statement:
        for delete_debtor in statement['deleteDebtors']:
            format_address(delete_debtor['address'])
    if 'addDebtors' in statement:
        for add_debtor in statement['addDebtors']:
            format_address(add_debtor['address'])


def set_modified_party(add_party, delete_parties):
    """Set the update flags for a single party ."""
    for delete_party in delete_parties:
        if 'reg_id' in add_party and 'reg_id' in delete_party and \
                add_party['reg_id'] == delete_party['reg_id'] and 'edit' not in delete_party:
            if add_party['address'] == delete_party['address']:
                if 'businessName' in add_party and 'businessName' in delete_party and \
                        add_party['businessName'] != delete_party['businessName']:
                    add_party['name_change'] = True
                    delete_party['edit'] = True
                    break
                elif 'personName' in add_party and 'personName' in delete_party and \
                        add_party['personName'] != delete_party['personName']:
                    add_party['name_change'] = True
                    delete_party['edit'] = True
                    break
            elif 'businessName' in add_party and 'businessName' in delete_party and \
                    add_party['businessName'] == delete_party['businessName']:
                add_party['address_change'] = True
                delete_party['edit'] = True
                break
            elif 'personName' in add_party and 'personName' in delete_party and \
                    add_party['personName'] == delete_party['personName']:
                add_party['address_change'] = True
                delete_party['edit'] = True
                break


def set_modified_parties(statement):
    """Replace amendment or change address country code with description. Set if party edited."""
    set_amend_change_addresses(statement)
    if 'deleteSecuredParties' in statement and 'addSecuredParties' in statement:
        for add_secured in statement['addSecuredParties']:
            if statement['deleteSecuredParties']:
                set_modified_party(add_secured, statement['deleteSecuredParties'])
    if 'deleteDebtors' in statement and 'addDebtors' in statement:
        for add_debtor in statement['addDebtors']:
            if statement['deleteDebtors']:
                set_modified_party(add_debtor, statement['deleteDebtors'])


def set_addresses(report_data):
    """Replace search results addresses country code with description."""
    set_financing_addresses(report_data)
    if 'changes' in report_data:
        for change in report_data['changes']:
            if change['statementType'] == 'CHANGE_STATEMENT':
                set_modified_parties(change)
            elif change['statementType'] == 'AMENDMENT_STATEMENT':
                set_modified_parties(change)
            else:
                format_address(change['registeringParty']['address'])


def to_report_datetime(date_time: str, include_time: bool = True, expiry: bool = False):
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


def to_report_datetime_expiry(date_time: str):
    """Convert ISO formatted date time or date string to report expiry date format."""
    # current_app.logger.info(model_utils.ts_from_iso_format(date_time).isoformat())
    local_datetime = model_utils.to_local_expiry_report(date_time)
    # current_app.logger.info(local_datetime.isoformat())
    if local_datetime.hour != 23:  # Expiry dates 15+ years in the future are not ajdusting for DST.
        offset = 23 - local_datetime.hour
        local_datetime = local_datetime + timedelta(hours=offset)
    timestamp = local_datetime.strftime('%B %-d, %Y at %-I:%M:%S %p Pacific time')
    return timestamp.replace(' PM ', ' pm ')


def set_financing_date_time(statement):
    """Replace financing statement API ISO UTC strings with local report format strings."""
    statement['createDateTime'] = to_report_datetime(statement['createDateTime'])
    if 'expiryDate' in statement and len(statement['expiryDate']) > 10:
        statement['expiryDate'] = to_report_datetime_expiry(statement['expiryDate'])
    if 'surrenderDate' in statement:
        statement['surrenderDate'] = to_report_datetime(statement['surrenderDate'], False)
    if 'dischargedDateTime' in statement:
        statement['dischargedDateTime'] = to_report_datetime(statement['dischargedDateTime'])
    if 'courtOrderInformation' in statement and 'orderDate' in statement['courtOrderInformation']:
        order_date = to_report_datetime(statement['courtOrderInformation']['orderDate'], False)
        statement['courtOrderInformation']['orderDate'] = order_date
    for debtor in statement['debtors']:
        if 'birthDate' in debtor:
            debtor['birthDate'] = to_report_datetime(debtor['birthDate'], False)
    if 'generalCollateral' in statement:
        for collateral in statement['generalCollateral']:
            if 'addedDateTime' in collateral:
                collateral['addedDateTime'] = to_report_datetime(collateral['addedDateTime'], True)

    if statement['type'] == 'RL' and 'lienAmount' in statement:
        lien_amount = str(statement['lienAmount'])
        if lien_amount.isnumeric():
            statement['lienAmount'] = '$' + '{:0,.2f}'.format(float(lien_amount))


def set_change_date_time(statement):   # pylint: disable=too-many-branches
    """Replace non-financing statement API ISO UTC strings with local report format strings."""
    statement['createDateTime'] = to_report_datetime(statement['createDateTime'])
    if 'courtOrderInformation' in statement and 'orderDate' in statement['courtOrderInformation']:
        order_date = to_report_datetime(statement['courtOrderInformation']['orderDate'], False)
        statement['courtOrderInformation']['orderDate'] = order_date
    if 'changeType' in statement:
        statement['changeType'] = TO_CHANGE_TYPE_DESCRIPTION[statement['changeType']].upper()
    if 'expiryDate' in statement and len(statement['expiryDate']) > 10:
        statement['expiryDate'] = to_report_datetime_expiry(statement['expiryDate'])
    if 'surrenderDate' in statement:
        statement['surrenderDate'] = to_report_datetime(statement['surrenderDate'], False)
    if 'deleteDebtors' in statement:
        for delete_debtor in statement['deleteDebtors']:
            if 'birthDate' in delete_debtor:
                delete_debtor['birthDate'] = to_report_datetime(delete_debtor['birthDate'], False)
    if 'addDebtors' in statement:
        for add_debtor in statement['addDebtors']:
            if 'birthDate' in add_debtor:
                add_debtor['birthDate'] = to_report_datetime(add_debtor['birthDate'], False)
    if 'deleteGeneralCollateral' in statement:
        for delete_gc in statement['deleteGeneralCollateral']:
            if 'addedDateTime' in delete_gc:
                delete_gc['addedDateTime'] = to_report_datetime(delete_gc['addedDateTime'], True)
    if 'addGeneralCollateral' in statement:
        for add_gc in statement['addGeneralCollateral']:
            if 'addedDateTime' in add_gc:
                add_gc['addedDateTime'] = to_report_datetime(add_gc['addedDateTime'], True)


def set_date_times(report_data):
    """Replace API ISO UTC strings with local report format strings."""
    set_financing_date_time(report_data)
    if 'changes' in report_data:
        for change in report_data['changes']:
            set_change_date_time(change)


def set_financing_vehicle_collateral(statement):
    """Replace financing statement vehicle collateral type code with description."""
    if 'vehicleCollateral' in statement:
        mh_count = 0
        for collateral in statement['vehicleCollateral']:
            if collateral['type'] == 'MH':
                mh_count += 1
            desc = TO_VEHICLE_TYPE_DESCRIPTION[collateral['type']]
            collateral['type'] = desc
        statement['mhCollateralCount'] = mh_count


def set_amend_change_vehicle_collateral(statement):
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


def set_amend_vehicle_collateral(statement):
    """Replace amendment statement vehicle collateral type code with description. Set if change is an edit."""
    set_amend_change_vehicle_collateral(statement)
    if 'deleteVehicleCollateral' in statement and 'addVehicleCollateral' in statement:
        for add in statement['addVehicleCollateral']:
            for delete in statement['deleteVehicleCollateral']:
                if 'serialNumber' in add and 'serialNumber' in delete:
                    if 'reg_id' in add and 'reg_id' in delete and add['reg_id'] == delete['reg_id'] and \
                            add['type'] == delete['type'] and add['serialNumber'] == delete['serialNumber']:
                        add['edit'] = True
                        delete['edit'] = True


def set_vehicle_collateral(report_data):
    """Replace search results vehicle collateral type codes with descriptions."""
    set_financing_vehicle_collateral(report_data)
    if 'changes' in report_data:
        for change in report_data['changes']:
            if change['statementType'] == 'CHANGE_STATEMENT':
                set_amend_change_vehicle_collateral(change)
            elif change['statementType'] == 'AMENDMENT_STATEMENT':
                set_amend_vehicle_collateral(change)


def set_financing_general_collateral(statement):
    """Replace report newline characters in financing statement general collateral descriptions."""
    if 'generalCollateral' in statement:
        for collateral in statement['generalCollateral']:
            if 'description' in collateral:
                collateral['description'] = collateral['description'].replace('/r/n', '<br>')
                collateral['description'] = markupsafe.Markup(collateral['description'])
            if 'descriptionAdd' in collateral:
                collateral['descriptionAdd'] = collateral['descriptionAdd'].replace('/r/n', '<br>')
                collateral['descriptionAdd'] = markupsafe.Markup(collateral['descriptionAdd'])
            if 'descriptionDelete' in collateral:
                collateral['descriptionDelete'] = collateral['descriptionDelete'].replace('/r/n', '<br>')
                collateral['descriptionDelete'] = markupsafe.Markup(collateral['descriptionDelete'])


def set_amend_change_general_collateral(statement):
    """Replace report newline characters in amendment statement general collateral description."""
    if 'deleteGeneralCollateral' in statement:
        for collateral in statement['deleteGeneralCollateral']:
            if 'description' in collateral:
                collateral['description'] = collateral['description'].replace('/r/n', '<br>')
                collateral['description'] = markupsafe.Markup(collateral['description'])
    if 'addGeneralCollateral' in statement:
        for collateral in statement['addGeneralCollateral']:
            if 'description' in collateral:
                collateral['description'] = collateral['description'].replace('/r/n', '<br>')
                collateral['description'] = markupsafe.Markup(collateral['description'])


def set_general_collateral(report_data):
    """Replace report newline characters in search general collateral descriptions."""
    set_financing_general_collateral(report_data)
    if 'changes' in report_data:
        for change in report_data['changes']:
            if change['statementType'] in ('CHANGE_STATEMENT', 'AMENDMENT_STATEMENT'):
                set_amend_change_general_collateral(change)
