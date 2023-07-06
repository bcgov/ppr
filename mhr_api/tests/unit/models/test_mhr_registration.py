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

"""Tests to assure the Registration Model.

Test-Suite to ensure that the Registration Model is working as expected.
"""
import copy
from http import HTTPStatus

from flask import current_app

import pytest
from registry_schemas.example_data.mhr import REGISTRATION, TRANSFER, EXEMPTION, PERMIT

from mhr_api.exceptions import BusinessException
from mhr_api.models import MhrRegistration, MhrDraft, MhrDocument, MhrNote, utils as model_utils
from mhr_api.models.registration_utils import AccountRegistrationParams
from mhr_api.models.type_tables import MhrLocationTypes, MhrPartyTypes, MhrOwnerStatusTypes, MhrStatusTypes
from mhr_api.models.type_tables import MhrRegistrationTypes, MhrRegistrationStatusTypes, MhrDocumentTypes
from mhr_api.models.type_tables import MhrTenancyTypes
from mhr_api.services.authz import MANUFACTURER_GROUP, QUALIFIED_USER_GROUP, GOV_ACCOUNT_ROLE, STAFF_ROLE


REG_DESCRIPTION = 'MANUFACTURED HOME REGISTRATION'
CONV_DESCRIPTION = 'RECORD CONVERSION'
TRAND_DELETE_GROUPS = [
    {
        'groupId': 3,
        'owners': [
            {
                'individualName': {
                    'first': 'ROBERT',
                    'middle': 'JOHN',
                    'last': 'MOWAT'
                },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567'
            }, {
                'individualName': {
                    'first': 'KAREN',
                    'middle': 'PATRICIA',
                    'last': 'MOWAT'
                },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567',
                'deathCertificateNumber': '232432432',
                'deathDateTime': '2021-02-21T18:56:00+00:00'
            }
        ],
        'type': 'JOINT'
    }
]
TRAND_ADD_GROUPS = [
    {
        'groupId': 4,
        'owners': [
            {
            'individualName': {
                'first': 'ROBERT',
                'middle': 'JOHN',
                'last': 'MOWAT'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': 'V8S 4I6',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'SOLE'
    }
]
EXEC_DELETE_GROUPS = [
    {
        'groupId': 1,
        'owners': [
            {
                'individualName': {
                    'first': 'SHARON',
                    'last': 'HALL'
                 },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567'
            }, {
                'individualName': {
                    'first': 'DENNIS',
                    'last': 'HALL'
                },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567',
                'deathCertificateNumber': '232432432',
                'deathDateTime': '2021-02-21T18:56:00+00:00'
            }
        ],
        'type': 'JOINT'
    }
]
EXEC_ADD_GROUPS = [
    {
        'groupId': 2,
        'owners': [
            {
                'individualName': {
                    'first': 'SHARON',
                    'last': 'HALL'
                },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567',
                'partyType': 'OWNER_IND'
            }, {
                'individualName': {
                    'first': 'APPOINTED',
                    'last': 'EXECUTOR'
                },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567',
                'partyType': 'EXECUTOR',
                'description': 'EXECUTOR of the deceased.'
            }
        ],
        'type': 'NA'
    }
]
ADMIN_DELETE_GROUPS = [
    {
        'groupId': 4,
        'owners': [
            {
                'individualName': {
                    'first': 'RICHARD',
                    'middle': 'GORDON',
                    'last': 'LANGER'
                },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567',
                'partyType': 'OWNER_IND',
                'deathCertificateNumber': '232432432',
                'deathDateTime': '2021-02-21T18:56:00+00:00'
            }
        ],
        'type': 'SOLE'
    }
]
ADMIN_ADD_GROUPS = [
    {
        'groupId': 5,
        'owners': [
            {
                'individualName': {
                    'first': 'APPOINTED',
                    'last': 'ADMINISTRATOR'
                },
                'address': {
                    'street': '3122B LYNNLARK PLACE',
                    'city': 'VICTORIA',
                    'region': 'BC',
                    'postalCode': 'V8S 4I6',
                    'country': 'CA'
                },
                'phoneNumber': '6041234567',
                'partyType': 'ADMINISTRATOR',
                'description': 'ADMINISTRATOR of the deceased.'
            }
        ],
        'type': 'SOLE'
    }
]
SOLE_OWNER_GROUP = [
    {
        'groupId': 1,
        'owners': [
            {
            'organizationName': 'TEST BUS.',
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': 'V8S 4I6',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'SOLE'
    }
]
JOINT_OWNER_GROUP = [
    {
        'groupId': 1,
        'owners': [
            {
            'individualName': {
                'first': 'James',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': 'V8S 4I6',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }, {
            'individualName': {
                'first': 'Jane',
                'last': 'Smith'
            },
            'address': {
                'street': '3122B LYNNLARK PLACE',
                'city': 'VICTORIA',
                'region': 'BC',
                'postalCode': 'V8S 4I6',
                'country': 'CA'
            },
            'phoneNumber': '6041234567'
            }
        ],
        'type': 'JOINT'
    }
]
COMMON_OWNER_GROUP = [
    {
    'groupId': 1,
    'owners': [
        {
        'individualName': {
            'first': 'MARY-ANNE',
            'last': 'BICKNELL'
        },
        'address': {
            'street': '3122B LYNNLARK PLACE',
            'city': 'VICTORIA',
            'region': 'BC',
            'postalCode': 'V8S 4I6',
            'country': 'CA'
        },
        'phoneNumber': '6041234567'
        }
    ],
    'type': 'COMMON',
    'interest': 'UNDIVIDED',
    'interestNumerator': 1,
    'interestDenominator': 2,
    'tenancySpecified': True
    }, {
    'groupId': 2,
    'owners': [
        {
        'individualName': {
            'first': 'JOHN',
            'last': 'CONNOLLY'
        },
        'address': {
            'street': '665 238TH STREET',
            'city': 'LANGLEY',
            'region': 'BC',
            'postalCode': 'V3A 6H4',
            'country': 'CA'
        },
        'phoneNumber': '6044620279'
        }
    ],
    'type': 'COMMON',
    'interest': 'UNDIVIDED',
    'interestNumerator': 5,
    'interestDenominator': 10,
    'tenancySpecified': True
    }
]
NOTE_REGISTRATION = {
  'clientReferenceId': 'EX-TP001234',
  'attentionReference': 'JOHN SMITH',
  'submittingParty': {
    'businessName': 'BOB PATERSON HOMES INC.',
    'address': {
      'street': '1200 S. MACKENZIE AVE.',
      'city': 'WILLIAMS LAKE',
      'region': 'BC',
      'country': 'CA',
      'postalCode': 'V2G 3Y1'
    },
    'phoneNumber': '6044620279'
  },
  'note': {
    'documentType': 'CAU',
    'documentId': '62133670',
    'effectiveDateTime': '2023-02-21T18:56:00+00:00',
    'remarks': 'NOTICE OF ACTION COMMENCED MARCH 1 2022 WITH CRANBROOK COURT REGISTRY COURT FILE NO. 3011.',
    'givingNoticeParty': {
      'personName': {
        'first': 'JOHNNY',
        'middle': 'B',
        'last': 'SMITH'
      },
      'address': {
        'street': '222 SUMMER STREET',
        'city': 'VICTORIA',
        'region': 'BC',
        'country': 'CA',
        'postalCode': 'V8W 2V8'
      },
      'phoneNumber': '2504930122'
    }
  }
}
# testdata pattern is ({account_id}, {mhr_num}, {exists}, {reg_description}, {in_list})
TEST_SUMMARY_REG_DATA = [
    ('PS12345', '077741', True, CONV_DESCRIPTION, False),
    ('PS12345', 'TESTXX', False, None, False),
    ('PS12345', '045349', True, CONV_DESCRIPTION, True),
    ('2523', '150062', True, REG_DESCRIPTION, True)
]
# testdata pattern is ({account_id}, {doc_reg_num}, {mhr_number}, {result_count}, {reg_desc}, {in_list})
TEST_SUMMARY_DOC_REG_DATA = [
    ('PS12345', '077741', '077741', 3, CONV_DESCRIPTION, False),
    ('PS12345', 'TESTXX', None, 0, None, False),
    ('PS12345', '00045349', '045349', 3, CONV_DESCRIPTION, True),
    ('PS12345', '009301', '009301', 1, CONV_DESCRIPTION, False),
    ('ppr_staff', '196123', '087219', 5, REG_DESCRIPTION, False),
    ('ppr_staff', '221961', '087219', 5, REG_DESCRIPTION, False)
]
# testdata pattern is ({account_id}, {has_results})
TEST_ACCOUNT_REG_DATA = [
    ('PS12345', True),
    ('2523', True),
    ('999999', False)
]
# testdata pattern is ({reg_id}, {has_results}, {legacy})
TEST_ID_DATA = [
    (200000000, True, False),
    (300000000, False, False),
    (1, True, True)
]
# testdata pattern is ({mhr_number}, {has_results}, {account_id})
TEST_MHR_NUM_DATA = [
    ('UX-XXX', False, 'PS12345'),
    ('150062', True, '2523')
]
# testdata pattern is ({doc_id}, {exist_count})
TEST_DOC_ID_DATA = [
    ('80048709', 1),
    ('80048756', 0)
]
# testdata pattern is ({mhr_num}, {group_id}, {doc_id_prefix}, {account_id})
TEST_DATA_TRANSFER = [
    ('150062', STAFF_ROLE, '9', '2523'),
    ('150062', GOV_ACCOUNT_ROLE, '9', '2523'),
    ('150062', MANUFACTURER_GROUP, '8', '2523'),
    ('150062', QUALIFIED_USER_GROUP, '1', '2523')
]
# testdata pattern is ({mhr_num}, {group_id}, {account_id}, {delete_groups}, {add_groups}, {reg_type})
TEST_DATA_TRANSFER_DEATH = [
    ('001004', QUALIFIED_USER_GROUP, '2523', TRAND_DELETE_GROUPS, TRAND_ADD_GROUPS, MhrRegistrationTypes.TRAND),
    ('001019', STAFF_ROLE, '2523', ADMIN_DELETE_GROUPS, ADMIN_ADD_GROUPS, MhrRegistrationTypes.TRANS_ADMIN),
    ('001020', STAFF_ROLE, '2523', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS, MhrRegistrationTypes.TRANS_AFFIDAVIT),
    ('001020', STAFF_ROLE, '2523', EXEC_DELETE_GROUPS, EXEC_ADD_GROUPS, MhrRegistrationTypes.TRANS_WILL)
]
# testdata pattern is ({mhr_num}, {group_id}, {account_id})
TEST_DATA_TRANSFER_SAVE = [
    ('150062', QUALIFIED_USER_GROUP, '2523')
]
# testdata pattern is ({mhr_num}, {group_id}, {doc_id_prefix}, {account_id})
TEST_DATA_EXEMPTION = [
    ('150062', STAFF_ROLE, '9', '2523'),
    ('150062', GOV_ACCOUNT_ROLE, '9', '2523'),
    ('150062', MANUFACTURER_GROUP, '8', '2523'),
    ('150062', QUALIFIED_USER_GROUP, '1', '2523')
]
# testdata pattern is ({mhr_num}, {group_id}, {account_id})
TEST_DATA_EXEMPTION_SAVE = [
    ('150062', QUALIFIED_USER_GROUP, '2523')
]
# testdata pattern is ({mhr_num}, {group_id}, {doc_id_prefix}, {account_id})
TEST_DATA_PERMIT = [
    ('150062', STAFF_ROLE, '9', '2523'),
    ('150062', GOV_ACCOUNT_ROLE, '9', '2523'),
    ('150062', MANUFACTURER_GROUP, '8', '2523'),
    ('150062', QUALIFIED_USER_GROUP, '1', '2523')
]
# testdata pattern is ({mhr_num}, {group_id}, {account_id})
TEST_DATA_PERMIT_SAVE = [
    ('150062', QUALIFIED_USER_GROUP, '2523')
]
# testdata pattern is ({mhr_num}, {group_id}, {doc_id_prefix}, {account_id})
TEST_DATA_NOTE = [
    ('003936', STAFF_ROLE, '6', 'ppr_staff')
]
# testdata pattern is ({http_status}, {document_id}, {mhr_num}, {doc_type}, {legacy}, {owner_count})
TEST_DATA_DOC_ID = [
    (HTTPStatus.OK, '10104535', '102265', 'TRAN', True, 2),
    (HTTPStatus.NOT_FOUND, 'XXX04535', None, None, False, 0)
]
# testdata pattern is ({type}, {group_count}, {owner_count}, {denominator}, {data})
TEST_DATA_NEW_GROUP = [
    ('SOLE', 1, 1, None, SOLE_OWNER_GROUP),
    ('JOINT', 1, 2, None, JOINT_OWNER_GROUP),
    ('COMMON', 2, 2, 10, COMMON_OWNER_GROUP)
]
# testdata pattern is ({tenancy_type}, {group_id}, {mhr_num}, {party_type}, {account_id})
TEST_DATA_GROUP_TYPE = [
    (MhrTenancyTypes.SOLE, 3, '017270', MhrPartyTypes.OWNER_IND, '2523'),
    (MhrTenancyTypes.JOINT, 3, '016148', MhrPartyTypes.OWNER_BUS, '2523'),
    (MhrTenancyTypes.COMMON, 2, '080282', MhrPartyTypes.OWNER_BUS, '2523'),
    (MhrTenancyTypes.NA, 8, '004764', MhrPartyTypes.EXECUTOR, '2523'),
    (MhrTenancyTypes.NA, 6, '051414', MhrPartyTypes.ADMINISTRATOR, '2523'),
    (MhrTenancyTypes.NA, 4, '098504', MhrPartyTypes.TRUSTEE, '2523')
]
# testdata pattern is ({mhr_num}, {account_id}, {has_pid})
TEST_DATA_LTSA_PID = [
    ('001020', '2523', False),
    ('001019', '2523', True)
]
# testdata pattern is ({mhr_num}, {account_id}, {status})
TEST_DATA_STATUS = [
    ('003936', '2523', 'FROZEN'),
    ('003304', '2523', 'ACTIVE')
]
# testdata pattern is ({mhr_num}, {staff}, {current}, {has_notes}, {account_id}, {has_caution}, {ncan_doc_id})
TEST_MHR_NUM_DATA_NOTE = [
    ('080282', True, True, True, '2523', False, None),
    ('003936', True, True, False, '2523', False, None),
    ('003936', True, False, False, '2523', False, None),
    ('003936', False, True, False, '2523', False, None),
    ('035159', True, True, True, 'ppr_staff', True, None),
    ('080104', True, True, True, 'ppr_staff', True, None),
    ('046315', True, True, True, 'ppr_staff', False, None),
    ('092238', True, True, True, 'ppr_staff', False, '63116143'),
    ('022873', True, True, True, 'ppr_staff', False, '43599221')
]


@pytest.mark.parametrize('account_id,mhr_num,exists,reg_desc,in_list', TEST_SUMMARY_REG_DATA)
def test_find_summary_by_mhr_number(session, account_id, mhr_num, exists, reg_desc, in_list):
    """Assert that finding summary MHR registration information works as expected."""
    registration = MhrRegistration.find_summary_by_mhr_number(account_id, mhr_num)
    if exists:
        current_app.logger.info(registration)
        assert registration['mhrNumber'] == mhr_num
        assert registration['registrationType']
        assert 'hasCaution' in registration
        assert registration['registrationDescription'] == reg_desc
        assert registration['statusType'] is not None
        assert registration['createDateTime'] is not None
        assert registration['username'] is not None
        assert registration['submittingParty'] is not None
        assert registration['clientReferenceId'] is not None
        assert registration['ownerNames'] is not None
        assert registration['path'] is not None
        assert registration['documentId'] is not None
        assert registration['inUserList'] == in_list
    else:
        assert not registration


@pytest.mark.parametrize('account_id,doc_reg_num,mhr_num,result_count,reg_desc,in_list', TEST_SUMMARY_DOC_REG_DATA)
def test_find_summary_by_doc_reg_number(session, account_id, doc_reg_num, mhr_num, result_count, reg_desc, in_list):
    """Assert that finding summary MHR registration information by a document registration number works as expected."""
    registration = MhrRegistration.find_summary_by_doc_reg_number(account_id, doc_reg_num)
    if result_count > 0:
        current_app.logger.info(registration)
        assert registration['mhrNumber'] == mhr_num
        assert registration['registrationType']
        assert 'hasCaution' in registration
        assert registration['registrationDescription'] == reg_desc
        assert registration['statusType'] is not None
        assert registration['createDateTime'] is not None
        assert registration['username'] is not None
        assert registration['submittingParty'] is not None
        assert registration['clientReferenceId'] is not None
        assert registration['ownerNames'] is not None
        assert registration['path'] is not None
        assert registration['documentId'] is not None
        assert registration['inUserList'] == in_list
        if result_count == 1:
            assert not registration.get('changes')
        else:
            assert registration.get('changes')
            assert len(registration['changes']) >= (result_count - 1)
            for reg in registration.get('changes'):
                desc: str = reg['registrationDescription']
                if reg.get('registrationType') == MhrRegistrationTypes.REG_NOTE and desc.find('CAUTION') > 0:
                    assert reg.get('expireDays')
    else:
        assert not registration


@pytest.mark.parametrize('account_id, has_results', TEST_ACCOUNT_REG_DATA)
def test_find_account_registrations(session, account_id, has_results):
    """Assert that finding account summary MHR registration information works as expected."""
    params: AccountRegistrationParams = AccountRegistrationParams(account_id=account_id,
                                                                  collapse=True,
                                                                  sbc_staff=False)

    reg_list = MhrRegistration.find_all_by_account_id(params)
    if has_results:
        for registration in reg_list:
            assert registration['mhrNumber']
            assert registration['registrationType']
            assert 'hasCaution' in registration
            assert registration['registrationDescription']
            assert registration['statusType'] is not None
            assert registration['createDateTime'] is not None
            assert registration['username'] is not None
            assert registration['submittingParty'] is not None
            assert registration['clientReferenceId'] is not None
            assert registration['ownerNames'] is not None
            assert registration['path'] is not None
            assert registration['documentId'] is not None
            assert not registration.get('inUserList')
            if registration['registrationDescription'] == REG_DESCRIPTION:
                assert 'lienRegistrationType' in registration
            if registration.get('changes'):
                for reg in registration.get('changes'):
                    desc: str = reg['registrationDescription']
                    if reg.get('registrationType') == MhrRegistrationTypes.REG_NOTE and desc.find('CAUTION') > 0:
                        assert reg.get('expireDays')
    else:
        assert not reg_list


@pytest.mark.parametrize('reg_id, has_results, legacy', TEST_ID_DATA)
def test_find_by_id(session, reg_id, has_results, legacy):
    """Assert that finding an MHR registration by id works as expected."""
    registration: MhrRegistration = MhrRegistration.find_by_id(reg_id, legacy)
    if has_results:
        assert registration
        if not legacy:
            assert registration.id == reg_id
            assert registration.mhr_number
            assert registration.status_type
            assert registration.registration_type
            assert registration.registration_ts
            assert registration.locations
            assert len(registration.locations) == 1
            assert registration.descriptions
            assert len(registration.descriptions) >= 1
            assert registration.sections
            assert len(registration.sections) >= 1
            assert registration.documents
            assert len(registration.documents) >= 1
        else:
            assert registration.manuhome
            report_json = registration.registration_json
            # current_app.logger.info(report_json)
            assert report_json['mhrNumber']
            assert report_json['status']
            assert report_json.get('createDateTime')
            assert report_json.get('clientReferenceId') is not None
            assert report_json.get('declaredValue') >= 0
            assert report_json.get('ownerGroups')
            assert report_json.get('location')
            assert report_json.get('description')
            assert report_json.get('notes')
            for note in report_json.get('notes'):
                assert note['documentDescription']
            registration.mail_version = True
            report_json = registration.new_registration_json
            # current_app.logger.debug(report_json)
            assert report_json.get('documentDescription')
            assert report_json.get('documentId')
            assert report_json.get('documentRegistrationNumber')
    else:
        assert not registration


@pytest.mark.parametrize('mhr_number, has_results, account_id', TEST_MHR_NUM_DATA)
def test_find_by_mhr_number(session, mhr_number, has_results, account_id):
    """Assert that finding an MHR registration by MHR number works as expected."""
    if has_results:
        registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_number, account_id)
        assert registration
        assert registration.id
        assert registration.mhr_number == mhr_number
        assert registration.status_type in MhrRegistrationStatusTypes
        assert registration.registration_type in MhrRegistrationTypes
        assert registration.registration_ts
        report_json = registration.registration_json
        assert report_json['mhrNumber']
        assert report_json['status']
        assert report_json.get('createDateTime')
        assert report_json.get('clientReferenceId') is not None
        assert report_json.get('declaredValue') >= 0
        assert report_json.get('ownerGroups')
        assert report_json.get('location')
        assert report_json.get('description')
        if report_json.get('notes'):
            for note in report_json.get('notes'):
                assert note['documentDescription']
                assert note['documentRegistrationNumber']
    else:
        with pytest.raises(BusinessException) as not_found_err:
            MhrRegistration.find_by_mhr_number(mhr_number, 'PS12345')
        # check
        assert not_found_err


@pytest.mark.parametrize('mhr_num,staff,current,has_notes,account_id,has_caution,ncan_doc_id', TEST_MHR_NUM_DATA_NOTE)
def test_find_by_mhr_number_note(session, mhr_num, staff, current, has_notes, account_id, has_caution, ncan_doc_id):
    """Assert that find a manufactured home by mhr_number conditionally includes notes."""
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    assert registration
    registration.current_view = current
    registration.staff = staff
    reg_json = registration.new_registration_json
    if has_notes:
        assert reg_json.get('notes')
        has_ncan: bool = False
        for note in reg_json.get('notes'):
            assert note.get('documentRegistrationNumber')
            assert note.get('documentId')
            assert note.get('documentDescription')
            if ncan_doc_id and note.get('documentId') == ncan_doc_id:
                has_ncan = True
                assert note.get('cancelledDocumentType')
                assert note.get('cancelledDocumentDescription')
                assert note.get('cancelledDocumentRegistrationNumber')
            assert note.get('createDateTime')
            assert note.get('status')
            assert 'remarks' in note
            assert note.get('givingNoticeParty')
        if ncan_doc_id:
            assert has_ncan
    elif staff and current:
        assert 'notes' in reg_json
        assert not reg_json.get('notes')
    else:
        assert 'notes' not in reg_json
    assert reg_json.get('hasCaution') == has_caution
    # search version
    reg_json = registration.registration_json
    if has_notes and mhr_num != '080282':
        assert reg_json.get('notes')
        has_ncan: bool = False
        for note in reg_json.get('notes'):
            assert note.get('documentRegistrationNumber')
            assert note.get('documentId')
            if ncan_doc_id and note.get('documentId') == ncan_doc_id:
                has_ncan = True
                assert note.get('cancelledDocumentType')
                assert note.get('cancelledDocumentRegistrationNumber')
            assert note.get('createDateTime')
            assert note.get('status')
            assert 'remarks' in note
            assert note.get('givingNoticeParty')
        if ncan_doc_id:
            assert has_ncan
    else:
        assert not reg_json.get('notes')


@pytest.mark.parametrize('mhr_number, account_id, has_pid', TEST_DATA_LTSA_PID)
def test_find_by_mhr_number_pid(session, mhr_number, account_id, has_pid):
    """Assert that finding an MHR registration with a PID by a legacy MHR number works as expected."""
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_number, account_id)
    assert registration
    assert registration.mhr_number == mhr_number
    reg_json = registration.registration_json
    assert reg_json.get('location')
    if has_pid:
        assert reg_json['location'].get('legalDescription')
    else:
        assert not reg_json['location'].get('legalDescription')


@pytest.mark.parametrize('mhr_number, account_id, status', TEST_DATA_STATUS)
def test_find_by_mhr_number_status(session, mhr_number, account_id, status):
    """Assert that finding an MHR registration MHR number returns the expected status."""
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_number, account_id)
    assert registration
    assert registration.mhr_number == mhr_number
    registration.current_view = True
    reg_json = registration.new_registration_json
    assert reg_json.get('status') == status


@pytest.mark.parametrize('mhr_number, has_results, account_id', TEST_MHR_NUM_DATA)
def test_find_original_by_mhr_number(session, mhr_number, has_results, account_id):
    """Assert that finding the original MH registration information by MHR number works as expected."""
    if has_results:
        registration: MhrRegistration = MhrRegistration.find_original_by_mhr_number(mhr_number, account_id)
        assert registration
        assert registration.id
        assert registration.mhr_number == mhr_number
        assert registration.status_type in MhrRegistrationStatusTypes
        assert registration.registration_type in MhrRegistrationTypes
        assert registration.registration_ts
    else:
        with pytest.raises(BusinessException) as not_found_err:
            MhrRegistration.find_by_mhr_number(mhr_number, 'PS12345')
        # check
        assert not_found_err


@pytest.mark.parametrize('http_status,doc_id,mhr_num,doc_type,legacy,owner_count', TEST_DATA_DOC_ID)
def test_find_by_document_id(session, http_status, doc_id, mhr_num, doc_type, legacy, owner_count):
    """Assert that find manufauctured home information by document id contains all expected elements."""
    if http_status == HTTPStatus.OK:
        registration: MhrRegistration = MhrRegistration.find_by_document_id(doc_id, 'PS12345')

        assert registration
        if not legacy:
            assert registration.id
            assert registration.mhr_number == mhr_num
            assert registration.status_type in MhrRegistrationStatusTypes
            assert registration.registration_type in MhrRegistrationTypes
            assert registration.registration_ts
        else:
            assert registration.manuhome
            assert registration.manuhome.mhr_number == mhr_num
            assert registration.manuhome.reg_documents
            doc = registration.manuhome.reg_documents[0]
            assert doc.id == doc_id
            assert doc.document_type == doc_type
        report_json = registration.json
        assert report_json['mhrNumber'] == mhr_num
        assert report_json.get('status')
        assert report_json.get('createDateTime')
        assert report_json.get('clientReferenceId') is not None
        assert report_json.get('documentId') == doc_id
        assert report_json.get('submittingParty')
        if owner_count > 0 and legacy and doc_type in ('TRAN', 'DEAT'):
            assert len(report_json.get('deleteOwnerGroups')) + len(report_json.get('addOwnerGroups')) == owner_count
        else:
            assert len(report_json.get('ownerGroups')) == owner_count
    else:
        with pytest.raises(BusinessException) as request_err:
             MhrRegistration.find_by_document_id(doc_id, 'PS12345')
        # check
        assert request_err
        assert request_err.value.status_code == http_status


def test_create_new_from_json(session):
    """Assert that the new MHR registration is created from json data correctly."""
    json_data = copy.deepcopy(REGISTRATION)
    json_data['ownLand'] = True
    registration: MhrRegistration = MhrRegistration.create_new_from_json(json_data, 'PS12345')
    assert registration.id > 0
    assert registration.mhr_number
    if model_utils.is_legacy():
        assert not str(registration.mhr_number).startswith('15')
    assert registration.registration_ts
    assert registration.status_type in MhrRegistrationStatusTypes
    assert registration.registration_type in MhrRegistrationTypes
    assert registration.account_id == 'PS12345'
    assert registration.client_reference_id    
    assert registration.draft
    assert registration.draft.id > 0
    assert registration.draft_id == registration.draft.id
    assert registration.draft.draft_number
    assert registration.draft.registration_type == registration.registration_type
    assert registration.draft.create_ts == registration.registration_ts
    assert registration.draft.account_id == registration.account_id
    assert registration.parties
    for party in registration.parties:
        assert party.registration_id > 0
        assert party.change_registration_id > 0
        assert party.party_type in MhrPartyTypes
        assert party.status_type in MhrOwnerStatusTypes
        assert not party.compressed_name
    assert registration.locations
    location = registration.locations[0]
    assert location.registration_id > 0
    assert location.change_registration_id > 0
    assert location.location_type in MhrLocationTypes
    assert location.status_type in MhrStatusTypes
    assert registration.descriptions
    description = registration.descriptions[0]
    assert description.registration_id > 0
    assert description.change_registration_id > 0
    assert description.status_type in MhrStatusTypes
    assert registration.sections
    section = registration.sections[0]
    assert section.registration_id > 0
    assert section.change_registration_id > 0
    assert section.status_type in MhrStatusTypes
    doc: MhrDocument = registration.documents[0]
    assert doc.id > 0
    assert doc.document_id == registration.doc_id
    assert doc.document_type == MhrDocumentTypes.REG_101
    assert doc.document_registration_number == registration.doc_reg_number
    assert doc.own_land == 'Y'
    assert registration.owner_groups
    assert len(registration.owner_groups) == 2
    for group in registration.owner_groups:
        assert group.group_id
        assert group.registration_id == registration.id
        assert group.change_registration_id == registration.id
        assert group.tenancy_type == MhrTenancyTypes.COMMON
        assert group.status_type == MhrOwnerStatusTypes.ACTIVE
        assert group.owners
        assert len(group.owners) == 1
    registration.report_view = True
    mh_json = registration.new_registration_json
    assert mh_json
    assert mh_json['ownLand']


def test_save_new(session):
    """Assert that saving a new MHR registration is working correctly."""
    json_data = copy.deepcopy(REGISTRATION)
    json_data['documentId'] = '88878888'
    registration: MhrRegistration = MhrRegistration.create_new_from_json(json_data, 'PS12345')
    registration.save()
    for party in registration.parties:
        assert party.compressed_name
    for group in registration.owner_groups:
        for party in group.owners:
            assert party.compressed_name
    mh_json = registration.new_registration_json
    assert mh_json
    assert 'ownLand' in mh_json
    reg_new = MhrRegistration.find_by_mhr_number(registration.mhr_number, 'PS12345')
    assert reg_new
    draft_new = MhrDraft.find_by_draft_number(registration.draft.draft_number, True)
    assert draft_new
    registration.report_view = True
    mh_report_json = registration.new_registration_json
    assert mh_report_json.get('mhrNumber') == mh_json.get('mhrNumber')
    assert mh_report_json.get('status') == mh_json.get('status')
    assert mh_report_json.get('registrationType') == mh_json.get('registrationType')
    assert mh_report_json.get('documentDescription') == mh_json.get('documentDescription')
    assert mh_report_json.get('clientReferenceId') == mh_json.get('clientReferenceId')
    assert mh_report_json.get('documentId') == mh_json.get('documentId')
    assert mh_report_json.get('documentRegistrationNumber') == mh_json.get('documentRegistrationNumber')
    assert mh_report_json.get('attentionReference') == mh_json.get('attentionReference')
    assert mh_report_json.get('description') == mh_json.get('description')
    assert mh_report_json.get('location') == mh_json.get('location')
    assert mh_report_json.get('submittingParty') == mh_json.get('submittingParty')
    assert mh_report_json.get('ownLand') == mh_json.get('ownLand')
    assert mh_report_json.get('payment') == mh_json.get('payment')
    groups1 =  mh_json.get('ownerGroups')
    groups2 = mh_report_json.get('ownerGroups')
    assert len(groups1) == len(groups2)
    for group1 in groups1:
        group = None
        for group2 in groups2:
            if group2.get('groupId') == group1.get('groupId'):
                group = group2
        assert group
        assert group1.get('type') == group.get('type')
        assert group1.get('tenancySpecified') == group.get('tenancySpecified')
        assert group1.get('interest', '') == group.get('interest', '')
        assert group1.get('interestDenominator', 0) == group.get('interestDenominator', 0)
        assert group1.get('interestNumerator', 0) == group.get('interestNumerator', 0)
        owners1 = group1.get('owners')
        owners2 = group.get('owners')
        assert len(owners1) == len(owners2)
        for owner1 in owners1:
            owner = None
            for owner2 in owners2:
                if owner2.get('individualName') and owner1.get('individualName') and \
                        owner2.get('individualName') == owner1.get('individualName'):
                    owner = owner2
                elif owner2.get('organizationName') and owner1.get('organizationName') and \
                        owner2.get('organizationName') == owner1.get('organizationName'):
                    owner = owner2
            assert owner
            assert owner1.get('partyType') == owner.get('partyType')
            assert owner1.get('phoneNumber', '') == owner.get('phoneNumber', '')
            assert owner1.get('individualName', None) == owner.get('individualName', None)
            assert owner1.get('organizationName', '') == owner.get('organizationName', '')
            address1 = owner1.get('address')
            address2 = owner.get('address')
            assert address1.get('city', '') ==  address2.get('city', '')
            assert address1.get('street', '') ==  address2.get('street', '')
            assert address1.get('streetAdditional', '') ==  address2.get('streetAdditional', '')
            assert address1.get('postalCode', '') ==  address2.get('postalCode', '')
            assert address1.get('region', '') ==  address2.get('region', '')
            assert address1.get('country', '') ==  address2.get('country', '')


@pytest.mark.parametrize('doc_id, exists_count', TEST_DOC_ID_DATA)
def test_get_doc_id_count(session, doc_id, exists_count):
    """Assert that counting existing document id's works as expected."""
    count: int = MhrRegistration.get_doc_id_count(doc_id)
    assert count == exists_count


@pytest.mark.parametrize('mhr_num,user_group,doc_id_prefix,account_id', TEST_DATA_TRANSFER)
def test_create_transfer_from_json(session, mhr_num, user_group, doc_id_prefix, account_id):
    """Assert that an MHR tranfer is created from MHR transfer json correctly."""
    json_data = copy.deepcopy(TRANSFER)
    del json_data['documentId']
    del json_data['documentDescription']
    del json_data['createDateTime']
    del json_data['payment']
    json_data['mhrNumber'] = mhr_num
    base_reg: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    assert base_reg
    assert base_reg.manuhome
    # current_app.logger.info(json_data)
    registration: MhrRegistration = MhrRegistration.create_transfer_from_json(base_reg,
                                                                              json_data,
                                                                              account_id,
                                                                              'userid',
                                                                              user_group)
    assert registration.id > 0
    assert registration.doc_id
    assert json_data.get('documentId')
    assert str(json_data.get('documentId')).startswith(doc_id_prefix)
    assert registration.mhr_number == mhr_num
    assert registration.registration_ts
    assert registration.status_type == MhrRegistrationStatusTypes.ACTIVE
    assert registration.registration_type == MhrRegistrationTypes.TRANS
    assert registration.account_id == account_id
    assert registration.client_reference_id    
    assert registration.draft
    assert registration.draft.id > 0
    assert registration.draft_id == registration.draft.id
    assert registration.draft.draft_number
    assert registration.draft.registration_type == registration.registration_type
    assert registration.draft.create_ts == registration.registration_ts
    assert registration.draft.account_id == registration.account_id
    assert registration.parties
    sub_party = registration.parties[0]
    assert sub_party.registration_id == registration.id
    assert sub_party.party_type == MhrPartyTypes.SUBMITTING
    if model_utils.is_legacy():
        assert registration.manuhome


@pytest.mark.parametrize('mhr_num,user_group,account_id,del_groups,add_groups,reg_type', TEST_DATA_TRANSFER_DEATH)
def test_create_transfer_death_from_json(session, mhr_num, user_group, account_id, del_groups, add_groups, reg_type):
    """Assert that an MHR tranfer due to death is created from MHR transfer json correctly."""
    json_data = copy.deepcopy(TRANSFER)
    del json_data['documentId']
    del json_data['documentDescription']
    del json_data['createDateTime']
    del json_data['payment']
    json_data['registrationType'] = reg_type
    json_data['mhrNumber'] = mhr_num
    json_data['deleteOwnerGroups'] = copy.deepcopy(del_groups)
    json_data['addOwnerGroups'] = copy.deepcopy(add_groups)
    if reg_type == MhrRegistrationTypes.TRANS_AFFIDAVIT:
        json_data['declaredValue'] = 25000
    base_reg: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    assert base_reg
    assert base_reg.manuhome
    # current_app.logger.info(json_data)
    registration: MhrRegistration = MhrRegistration.create_transfer_from_json(base_reg,
                                                                              json_data,
                                                                              account_id,
                                                                              'userid',
                                                                              user_group)
    assert registration.id > 0
    assert registration.doc_id
    assert json_data.get('documentId')
    assert registration.mhr_number == mhr_num
    assert registration.registration_ts
    assert registration.status_type == MhrRegistrationStatusTypes.ACTIVE
    assert registration.registration_type == reg_type
    assert registration.account_id == account_id
    assert registration.client_reference_id    
    assert registration.draft
    assert registration.draft.id > 0
    assert registration.draft_id == registration.draft.id
    assert registration.draft.draft_number
    assert registration.draft.registration_type == registration.registration_type
    assert registration.draft.create_ts == registration.registration_ts
    assert registration.draft.account_id == registration.account_id
    assert registration.parties
    for group in registration.owner_groups:
        if group.modified:
            for owner in group.owners:
                if reg_type == MhrRegistrationTypes.TRAND:
                    assert owner.party_type in (MhrPartyTypes.OWNER_IND, MhrPartyTypes.OWNER_BUS)
                elif reg_type == MhrRegistrationTypes.TRANS_ADMIN:
                    assert owner.party_type == MhrPartyTypes.ADMINISTRATOR
                else:
                    assert owner.party_type in (MhrPartyTypes.OWNER_IND,
                                                MhrPartyTypes.OWNER_BUS,
                                                MhrPartyTypes.EXECUTOR)
            if reg_type in (MhrRegistrationTypes.TRANS_AFFIDAVIT, MhrRegistrationTypes.TRANS_WILL):
                assert group.tenancy_type == MhrTenancyTypes.NA
    if model_utils.is_legacy():
        assert registration.manuhome


@pytest.mark.parametrize('mhr_num,user_group,account_id,del_groups,add_groups,reg_type', TEST_DATA_TRANSFER_DEATH)
def test_save_transfer_death(session, mhr_num, user_group, account_id, del_groups, add_groups, reg_type):
    """Assert that an MHR transfer due to death save deleted owner group works correctly."""
    json_data = copy.deepcopy(TRANSFER)
    del json_data['documentId']
    del json_data['documentDescription']
    del json_data['createDateTime']
    del json_data['payment']
    json_data['registrationType'] = reg_type
    json_data['mhrNumber'] = mhr_num
    json_data['deleteOwnerGroups'] = copy.deepcopy(del_groups)
    json_data['addOwnerGroups'] = copy.deepcopy(add_groups)
    if reg_type == MhrRegistrationTypes.TRANS_AFFIDAVIT:
        json_data['declaredValue'] = 25000
    base_reg: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    assert base_reg
    assert base_reg.manuhome
    # current_app.logger.info(json_data)
    registration: MhrRegistration = MhrRegistration.create_transfer_from_json(base_reg,
                                                                              json_data,
                                                                              account_id,
                                                                              'userid',
                                                                              user_group)
    registration.save()
    registration.save_transfer(json_data, 500000)
    for group in json_data.get('deleteOwnerGroups'):
        for existing in registration.owner_groups:
            if existing.group_id == group.get('groupId'):
                assert existing.status_type == MhrOwnerStatusTypes.PREVIOUS
                for owner in existing.owners:
                    assert owner.status_type == MhrOwnerStatusTypes.PREVIOUS
                    assert owner.death_cert_number
                    assert owner.death_ts


@pytest.mark.parametrize('mhr_num,user_group,account_id', TEST_DATA_TRANSFER_SAVE)
def test_save_transfer(session, mhr_num, user_group, account_id):
    """Assert that an MHR tranfer is created from MHR transfer json correctly."""
    json_data = copy.deepcopy(TRANSFER)
    del json_data['documentId']
    del json_data['documentDescription']
    del json_data['createDateTime']
    del json_data['payment']
    json_data['mhrNumber'] = mhr_num
    base_reg: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    assert base_reg
    assert base_reg.manuhome
    # current_app.logger.info(json_data)
    registration: MhrRegistration = MhrRegistration.create_transfer_from_json(base_reg,
                                                                              json_data,
                                                                              account_id,
                                                                              'userid',
                                                                              user_group)
    registration.save()
    for party in registration.parties:
        if not party.compressed_name:
            current_app.logger.error(party.json)
        assert party.compressed_name
    for group in registration.owner_groups:
        for party in group.owners:
            if not party.compressed_name:
                current_app.logger.error(party.json)
            assert party.compressed_name

    reg_new = MhrRegistration.find_by_mhr_number(registration.mhr_number,
                                                 account_id,
                                                 False,
                                                 MhrRegistrationTypes.TRANS)
    assert reg_new
    draft_new = MhrDraft.find_by_draft_number(registration.draft.draft_number, True)
    assert draft_new


@pytest.mark.parametrize('mhr_num,user_group,account_id', TEST_DATA_EXEMPTION_SAVE)
def test_save_exemption(session, mhr_num, user_group, account_id):
    """Assert that an MHR exemption is created from MHR exemption json correctly."""
    json_data = copy.deepcopy(EXEMPTION)
    del json_data['documentId']
    del json_data['documentRegistrationNumber']
    del json_data['documentDescription']
    del json_data['createDateTime']
    del json_data['payment']
    json_data['mhrNumber'] = mhr_num
    json_data['nonResidential'] = False
    base_reg: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    assert base_reg
    assert base_reg.manuhome
    # current_app.logger.info(json_data)
    registration: MhrRegistration = MhrRegistration.create_exemption_from_json(base_reg,
                                                                               json_data,
                                                                               account_id,
                                                                               'userid',
                                                                               user_group)
    registration.save()
    base_reg.save_exemption()
    reg_new = MhrRegistration.find_by_mhr_number(registration.mhr_number,
                                                 account_id,
                                                 False,
                                                 MhrRegistrationTypes.EXEMPTION_RES)
    assert reg_new
    draft_new = MhrDraft.find_by_draft_number(registration.draft.draft_number, True)
    assert draft_new


@pytest.mark.parametrize('mhr_num,user_group,doc_id_prefix,account_id', TEST_DATA_EXEMPTION)
def test_create_exemption_from_json(session, mhr_num, user_group, doc_id_prefix, account_id):
    """Assert that an MHR exemption is created from json correctly."""
    json_data = copy.deepcopy(EXEMPTION)
    del json_data['documentId']
    del json_data['documentRegistrationNumber']
    del json_data['documentDescription']
    del json_data['createDateTime']
    del json_data['payment']
    json_data['mhrNumber'] = mhr_num
    json_data['nonResidential'] = False
    json_data['note']['remarks'] = 'remarks'
    json_data['note']['expiryDateTime'] = '2022-10-07T18:43:45+00:00'
    base_reg: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    assert base_reg
    assert base_reg.manuhome
    assert base_reg.manuhome.reg_documents
    # current_app.logger.info(json_data)
    registration: MhrRegistration = MhrRegistration.create_exemption_from_json(base_reg,
                                                                               json_data,
                                                                               account_id,
                                                                               'userid',
                                                                               user_group)
    assert registration.id > 0
    assert registration.doc_id
    assert json_data.get('documentId')
    assert str(json_data.get('documentId')).startswith(doc_id_prefix)
    assert registration.mhr_number == mhr_num
    assert registration.registration_ts
    assert registration.status_type == MhrRegistrationStatusTypes.ACTIVE
    assert registration.registration_type == MhrRegistrationTypes.EXEMPTION_RES
    assert registration.account_id == account_id
    assert registration.client_reference_id    
    assert registration.draft
    assert registration.draft.id > 0
    assert registration.draft_id == registration.draft.id
    assert registration.draft.draft_number
    assert registration.draft.registration_type == registration.registration_type
    assert registration.draft.create_ts == registration.registration_ts
    assert registration.draft.account_id == registration.account_id
    assert registration.parties
    sub_party = registration.parties[0]
    assert sub_party.registration_id == registration.id
    assert sub_party.party_type == MhrPartyTypes.SUBMITTING
    if model_utils.is_legacy():
        assert registration.manuhome
    assert registration.documents
    doc: MhrDocument = registration.documents[0]
    assert doc.id > 0
    assert doc.document_id == registration.doc_id
    assert doc.document_type == MhrDocumentTypes.EXRS
    assert doc.document_registration_number == registration.doc_reg_number
    assert registration.notes
    note: MhrNote = registration.notes[0]
    assert note.document_type == doc.document_type
    assert note.document_id == doc.id
    assert note.destroyed == 'Y'
    assert note.remarks == 'remarks'
    assert note.expiry_date
    assert note.expiry_date.year == 2022
    assert note.expiry_date.month == 10


@pytest.mark.parametrize('mhr_num,user_group,doc_id_prefix,account_id', TEST_DATA_EXEMPTION)
def test_create_permit_from_json(session, mhr_num, user_group, doc_id_prefix, account_id):
    """Assert that an MHR tranfer is created from MHR exemption json correctly."""
    json_data = copy.deepcopy(PERMIT)
    del json_data['documentId']
    del json_data['documentRegistrationNumber']
    del json_data['documentDescription']
    del json_data['createDateTime']
    del json_data['payment']
    del json_data['note']
    del json_data['registrationType']
    json_data['mhrNumber'] = mhr_num
    base_reg: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    assert base_reg
    assert base_reg.manuhome
    assert base_reg.manuhome.reg_documents
    # current_app.logger.info(json_data)
    registration: MhrRegistration = MhrRegistration.create_permit_from_json(base_reg,
                                                                            json_data,
                                                                            'PS12345',
                                                                            'userid',
                                                                            user_group)
    assert registration.draft
    assert registration.draft.id > 0
    assert registration.draft_id == registration.draft.id
    assert registration.draft.draft_number
    assert registration.draft.registration_type == registration.registration_type
    assert registration.draft.create_ts == registration.registration_ts
    assert registration.draft.account_id == registration.account_id
    assert registration.parties
    sub_party = registration.parties[0]
    assert sub_party.registration_id == registration.id
    assert sub_party.party_type == MhrPartyTypes.SUBMITTING
    if model_utils.is_legacy():
        assert registration.manuhome
    assert registration.documents
    doc: MhrDocument = registration.documents[0]
    assert doc.id > 0
    assert doc.document_id == registration.doc_id
    assert doc.document_type == MhrDocumentTypes.REG_103
    assert doc.document_registration_number == registration.doc_reg_number
    assert registration.notes
    note: MhrNote = registration.notes[0]
    assert note.document_type == doc.document_type
    assert note.document_id == doc.id
    assert note.destroyed == 'N'
    # assert note.remarks
    assert note.expiry_date
    assert registration.locations
    location = registration.locations[0]
    assert location.registration_id == registration.id
    assert location.change_registration_id == registration.id
    assert location.location_type in MhrLocationTypes
    assert location.status_type == MhrStatusTypes.ACTIVE


@pytest.mark.parametrize('type,group_count,owner_count,denominator,data', TEST_DATA_NEW_GROUP)
def test_create_new_groups(session, type, group_count, owner_count, denominator, data):
    """Assert that an new MH registration groups are created from json correctly."""
    json_data = copy.deepcopy(REGISTRATION)
    json_data['ownerGroups'] = data
    reg: MhrRegistration = MhrRegistration(id=1000)
    reg.create_new_groups(json_data)
    assert reg.owner_groups
    assert len(reg.owner_groups) == group_count
    own_count = 0
    group_id: int = 0
    for group in reg.owner_groups:
        group_id += 1
        assert group.group_id == group_id
        assert group.registration_id == 1000
        assert group.change_registration_id == 1000
        assert group.tenancy_type == type
        assert group.status_type == MhrOwnerStatusTypes.ACTIVE
        assert group.owners
        own_count += len(group.owners)
        if denominator:
            assert group.interest
            if group.group_id == 1:
                assert group.interest_numerator == 1
                assert group.interest_denominator == 2
            else:
                assert group.interest_numerator == 5
                assert group.interest_denominator == 10
        else:
            assert not group.interest
            assert not group.interest_numerator
            assert not group.interest_denominator
    assert own_count == owner_count


@pytest.mark.parametrize('tenancy_type,group_id,mhr_num,party_type,account_id', TEST_DATA_GROUP_TYPE)
def test_group_type(session, tenancy_type, group_id, mhr_num, party_type, account_id):
    """Assert that find manufauctured home by mhr_number contains all expected elements."""
    registration: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    assert registration
    json_data = registration.registration_json
    for group in json_data.get('ownerGroups'):
        if group.get('groupId') == group_id:
            assert group['type'] == tenancy_type
            if party_type and group.get('owners'):
                for owner in group.get('owners'):
                    assert owner.get('partyType') == party_type


@pytest.mark.parametrize('mhr_num,user_group,doc_id_prefix,account_id', TEST_DATA_NOTE)
def test_create_note_from_json(session, mhr_num, user_group, doc_id_prefix, account_id):
    """Assert that an MHR unit note registration is created from json correctly."""
    json_data = copy.deepcopy(NOTE_REGISTRATION)
    base_reg: MhrRegistration = MhrRegistration.find_by_mhr_number(mhr_num, account_id)
    assert base_reg
    # current_app.logger.info(json_data)
    registration: MhrRegistration = MhrRegistration.create_note_from_json(base_reg,
                                                                          json_data,
                                                                          account_id,
                                                                          'userid',
                                                                          user_group)
    assert registration.id > 0
    assert registration.doc_id
    assert json_data.get('documentId')
    assert str(json_data.get('documentId')).startswith(doc_id_prefix)
    assert registration.mhr_number == mhr_num
    assert registration.registration_ts
    assert registration.status_type == MhrRegistrationStatusTypes.ACTIVE
    assert registration.registration_type == MhrRegistrationTypes.REG_NOTE
    assert registration.account_id == account_id
    assert registration.client_reference_id    
    assert registration.draft
    assert registration.draft.id > 0
    assert registration.draft_id == registration.draft.id
    assert registration.draft.draft_number
    assert registration.draft.registration_type == registration.registration_type
    assert registration.draft.create_ts == registration.registration_ts
    assert registration.draft.account_id == registration.account_id
    assert registration.parties
    sub_party = registration.parties[0]
    assert sub_party.registration_id == registration.id
    assert sub_party.party_type == MhrPartyTypes.SUBMITTING
    notice_party = registration.parties[1]
    assert notice_party.registration_id == registration.id
    assert notice_party.party_type == MhrPartyTypes.CONTACT
    assert registration.documents
    doc: MhrDocument = registration.documents[0]
    assert doc.id > 0
    assert doc.document_id == registration.doc_id
    assert doc.document_type == json_data['note'].get('documentType')
    assert registration.notes
    note: MhrNote = registration.notes[0]
    assert note.document_type == doc.document_type
    assert note.document_id == doc.id
    assert note.destroyed == 'N'
    assert note.remarks
    assert note.expiry_date
    assert note.effective_ts
