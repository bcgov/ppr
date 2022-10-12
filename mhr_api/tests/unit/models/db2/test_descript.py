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

"""Tests to assure the legacy DB2 Description Model.

Test-Suite to ensure that the legacy DB2 Description Model is working as expected.
"""

import pytest

from flask import current_app

from mhr_api.models import Db2Descript


# testdata pattern is ({exists}, {manuhome_id}, {year}, {serial}, {count})
TEST_DATA = [
    (True, 101550, '2015', '03A001419', 1),
    (True, 101560, '2015', '313000Z008393A', 2),
    (False, 0, None, None, 0)
]
# testdata pattern is ({exists}, {manhomid}, {doc_reg_id})
TEST_DATA_DOC_ID = [
    (True, 101550, '80033034'),
    (False, 0, None)
]


@pytest.mark.parametrize('exists,manuhome_id,year,serial,count', TEST_DATA)
def test_find_by_manuhome_id(session, exists, manuhome_id, year, serial, count):
    """Assert that find descriptions by manuhome id contains all expected elements."""
    descriptions: Db2Descript = Db2Descript.find_by_manuhome_id(manuhome_id)
    if exists:
        assert descriptions
        assert len(descriptions) == count
        for descript in descriptions:
            assert descript.manuhome_id == manuhome_id
            assert descript.description_id > 0
            assert descript.status
            assert descript.year_made == year
            if descript.status == 'A':
                assert descript.serial_number_1 == serial
            else:
                assert descript.serial_number_1
            reg_json = descript.registration_json
            current_app.logger.debug(reg_json)
            assert reg_json.get('manufacturer')
            assert reg_json.get('baseInformation')
            assert reg_json.get('sectionCount')
            assert reg_json.get('sections')
            assert reg_json.get('csaNumber') is not None
            assert reg_json.get('csaStandard') is not None
            assert reg_json.get('engineerName') is not None
            # assert reg_json.get('engineerDate')
            assert reg_json['baseInformation']['year']
            assert reg_json['baseInformation']['make']
            assert len(reg_json['sections']) >= 1

    else:
        assert not descriptions


@pytest.mark.parametrize('exists,manuhome_id,year,serial,count', TEST_DATA)
def test_find_by_manuhome_id_active(session, exists, manuhome_id, year, serial, count):
    """Assert that find the active description by manuhome id contains all expected elements."""
    descript: Db2Descript = Db2Descript.find_by_manuhome_id_active(manuhome_id)
    if exists:
        assert descript.manuhome_id == manuhome_id
        assert descript.description_id > 0
        assert descript.status
        assert descript.year_made == year
        assert descript.serial_number_1 == serial
        assert descript.section_count is not None
        assert descript.circa is not None
        assert descript.csa_number is not None
        assert descript.csa_standard is not None
        assert descript.manufacturer_name is not None
        assert descript.make_model is not None
        assert descript.square_feet is not None
        assert descript.engineer_date is not None
        assert descript.engineer_name is not None
        assert descript.serial_number_1 is not None
        assert descript.length_feet_1 is not None
        assert descript.length_inches_1 is not None
        assert descript.width_feet_1 is not None
        assert descript.width_inches_1 is not None
        reg_json = descript.registration_json
        current_app.logger.debug(reg_json)
        assert reg_json.get('manufacturer')
        assert reg_json.get('baseInformation')
        assert reg_json.get('sectionCount')
        assert reg_json.get('sections')
        assert reg_json.get('csaNumber') is not None
        assert reg_json.get('csaStandard') is not None
        assert reg_json.get('engineerName') is not None
        # assert reg_json.get('engineerDate')
        assert reg_json['baseInformation']['year']
        assert reg_json['baseInformation']['make']
        assert len(reg_json['sections']) >= 1
        for section in reg_json['sections']:
            assert section['serialNumber']
            assert section['lengthFeet']
            assert section['lengthInches'] >= 0
            assert section['widthFeet']
            assert section['widthInches'] >= 0
    else:
        assert not descript


@pytest.mark.parametrize('exists,manuhome_id,doc_id', TEST_DATA_DOC_ID)
def test_find_by_doc_id(session, exists, manuhome_id, doc_id):
    """Assert that find descript by document id contains all expected elements."""
    descript: Db2Descript = Db2Descript.find_by_doc_id(doc_id)
    if exists:
        assert descript
        assert descript.reg_document_id == doc_id
        assert descript.manuhome_id == manuhome_id
    else:
        assert not descript


def test_description_json(session):
    """Assert that the description renders to a json format correctly."""
    descript = Db2Descript(description_id=1,
                           status='A',
                           reg_document_id='1234',
                           can_document_id='5678',
                           csa_number='999999',
                           csa_standard='1111',
                           section_count=1,
                           square_feet=0,
                           year_made='2004',
                           circa='',
                           serial_number_1='ABJ1234',
                           length_feet_1=60,
                           length_inches_1=0,
                           width_feet_1=14,
                           width_inches_1=0,
                           manufacturer_name='MODULINE',
                           make_model='MONARCH',
                           engineer_name='ENG NAME',
                           rebuilt_remarks='',
                           other_remarks='')

    test_json = {
        'descriptionId': descript.description_id,
        'status': descript.status,
        'registrationDocumentId': descript.reg_document_id,
        'canDocumentId': descript.can_document_id,
        'csaNumber': descript.csa_number,
        'csaStandard': descript.csa_standard,
        'sectionCount': descript.section_count,
        'squareFeet': descript.square_feet,
        'year': descript.year_made,
        'circa': descript.circa,
        'serialNumber1': descript.serial_number_1,
        'lengthFeet1': descript.length_feet_1,
        'lengthInches1': descript.length_inches_1,
        'widthFeet1': descript.width_feet_1,
        'widthInches1': descript.width_inches_1,
        'manufacturer': descript.manufacturer_name,
        'makeModel': descript.make_model,
        'engineerName': descript.engineer_name,
        'rebuiltRemarks': descript.rebuilt_remarks,
        'otherRemarks': descript.other_remarks
    }
    assert descript.json == test_json
