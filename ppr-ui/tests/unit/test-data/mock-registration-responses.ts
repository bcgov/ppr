import {
  APIAmendmentTypes,
  APIMhrTypes,
  APIRegistrationTypes,
  APIStatusTypes,
  DraftTypes,
  MhApiStatusTypes
} from '@/enums'
import { DraftResultIF, MhrDraftIF, MhRegistrationSummaryIF, RegistrationSummaryIF } from '@/interfaces'

export const mockedRegistration1: RegistrationSummaryIF = {
  baseRegistrationNumber: 'GOV2343',
  clientReferenceId: 'ABC123',
  createDateTime: '2021-07-20T17:21:17+00:00',
  expireDays: 500, // Number of days until expiry
  hasDraft: true,
  lastUpdateDateTime: '2021-10-04T18:26:11+00:00',
  path: '/path/to/doc',
  registeringName: 'Reg Name 1',
  registeringParty: 'John Doe',
  registrationClass: 'PPSALIEN',
  registrationDescription: 'PPSA SECURITY AGREEMENT',
  registrationNumber: 'GOV2343',
  registrationType: APIRegistrationTypes.SECURITY_AGREEMENT,
  securedParties: 'Bank of Nova Scotia',
  statusType: APIStatusTypes.ACTIVE,
  totalRegistrationCount: 1
}

export const mockedRegistration2: RegistrationSummaryIF = {
  baseRegistrationNumber: 'BC456788',
  clientReferenceId: '',
  createDateTime: '2021-08-20T17:21:17+00:00',
  expireDays: 316,
  path: '/path/to/doc',
  registeringName: 'Reg Name 2',
  registeringParty: 'ICBC',
  registrationClass: 'PPSALIEN',
  registrationDescription: 'REPAIRERS LIEN',
  registrationNumber: 'BC456788',
  registrationType: APIAmendmentTypes.AMENDMENT,
  securedParties: 'Bank of Montreal',
  statusType: APIStatusTypes.ACTIVE,
  expand: false
}

export const mockedRegistration2Child: RegistrationSummaryIF = {
  baseRegistrationNumber: 'BC456788',
  clientReferenceId: '',
  createDateTime: '2021-07-20T17:21:17+00:00',
  path: '/path/to/doc',
  registeringName: 'Reg Name 2',
  registeringParty: 'ICBC',
  registrationClass: 'AMENDMENT',
  registrationDescription: 'AMENDMENT/OTHER CHANGE',
  registrationNumber: 'BC456789',
  registrationType: APIAmendmentTypes.AMENDMENT,
  securedParties: 'Bank of Montreal'
}

export const mockedRegistration3: RegistrationSummaryIF = {
  baseRegistrationNumber: '003423B',
  clientReferenceId: '',
  createDateTime: '2019-08-20T17:21:17+00:00',
  expireDays: 0,
  path: '',
  registeringName: 'Reg Name 3',
  registeringParty: 'ICBC',
  registrationClass: 'PPSALIEN',
  registrationDescription: 'REPAIRERS LIEN',
  registrationNumber: '003423B',
  registrationType: APIAmendmentTypes.AMENDMENT,
  securedParties: 'Bank of Montreal',
  statusType: APIStatusTypes.DISCHARGED
}

export const mockedDraft1: DraftResultIF = {
  lastUpdateDateTime: '2021-08-03T17:21:17+00:00',
  type: DraftTypes.FINANCING_STATEMENT,
  documentId: 'D9000018',
  baseRegistrationNumber: '',
  registrationType: APIRegistrationTypes.REPAIRERS_LIEN,
  registrationDescription: '',
  path: '/path/to/doc',
  createDateTime: '2021-08-03T17:21:17+00:00',
  clientReferenceId: 'FFF555',
  expand: false
}

export const mockedDraft2: DraftResultIF = {
  lastUpdateDateTime: '2021-08-01T17:21:17+00:00',
  type: DraftTypes.FINANCING_STATEMENT,
  documentId: 'D9000338',
  baseRegistrationNumber: '',
  registrationType: APIRegistrationTypes.OTHER,
  registrationDescription: '',
  path: '/path/to/doc',
  createDateTime: '2021-08-01T17:21:17+00:00',
  clientReferenceId: ''
}

export const mockedDraftAmend: DraftResultIF = {
  lastUpdateDateTime: '2021-08-05T17:21:17+00:00',
  type: DraftTypes.AMENDMENT_STATEMENT,
  documentId: 'D9000019',
  baseRegistrationNumber: 'GOV2343',
  registrationType: APIRegistrationTypes.SECURITY_AGREEMENT,
  registrationDescription: '',
  path: '/path/to/doc',
  createDateTime: '2021-08-05T17:21:17+00:00',
  clientReferenceId: 'FFF555'
}

export const mockedRegistration1Collapsed: RegistrationSummaryIF = {
  baseRegistrationNumber: 'GOV2343',
  changes: [mockedDraftAmend],
  clientReferenceId: 'ABC123',
  createDateTime: '2021-07-20T17:21:17+00:00',
  expireDays: 500, // Number of days until expiry
  lastUpdateDateTime: '2021-10-04T18:26:11+00:00',
  path: '/path/to/doc',
  registeringName: 'Reg Name 1',
  registeringParty: 'John Doe',
  registrationClass: 'PPSALIEN',
  registrationDescription: 'PPSA SECURITY AGREEMENT',
  registrationNumber: 'GOV2343',
  registrationType: APIRegistrationTypes.SECURITY_AGREEMENT,
  securedParties: 'Bank of Nova Scotia',
  statusType: APIStatusTypes.ACTIVE,
  expand: false
}

export const mockedRegistration2Collapsed: RegistrationSummaryIF = {
  baseRegistrationNumber: 'BC456788',
  changes: [mockedRegistration2Child],
  clientReferenceId: '',
  createDateTime: '2021-08-20T17:21:17+00:00',
  expireDays: 316,
  path: '/path/to/doc',
  registeringName: 'Reg Name 2',
  registeringParty: 'ICBC',
  registrationClass: 'PPSALIEN',
  registrationDescription: 'REPAIRERS LIEN',
  registrationNumber: 'BC456788',
  registrationType: APIAmendmentTypes.AMENDMENT,
  securedParties: 'Bank of Montreal',
  statusType: APIStatusTypes.ACTIVE,
  expand: false
}

export const mockedMhRegistration: MhRegistrationSummaryIF = {
  mhrNumber: '123456',
  ownerNames: 'John Smith',
  clientReferenceId: 'ABC123',
  createDateTime: '2021-07-20T17:21:17+00:00',
  expireDays: 500, // Number of days until expiry
  hasDraft: true,
  path: '/path/to/doc',
  username: 'John Smith',
  submittingParty: 'some Submitting Party',
  registrationDescription: 'PPSA SECURITY AGREEMENT',
  documentRegistrationNumber: 'GOV2343',
  baseRegistrationNumber: '654321',
  registrationType: APIMhrTypes.MANUFACTURED_HOME_REGISTRATION,
  statusType: MhApiStatusTypes.ACTIVE,
  expand: true
}

export const mockedMhDraft: MhrDraftIF = {
  lastUpdateDateTime: '2021-08-03T17:21:17+00:00',
  type: APIMhrTypes.MANUFACTURED_HOME_REGISTRATION,
  mhrNumber: '',
  registrationType: APIMhrTypes.MANUFACTURED_HOME_REGISTRATION,
  registrationDescription: '',
  path: '/path/to/doc',
  createDateTime: '2021-08-03T17:21:17+00:00',
  clientReferenceId: 'FFF555',
  statusType: 'Draft'
}
