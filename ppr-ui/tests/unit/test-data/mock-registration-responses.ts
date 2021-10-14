import { APIAmendmentTypes, APIRegistrationTypes, DraftTypes } from '@/enums'
import { DraftResultIF, RegistrationSummaryIF } from '@/interfaces'

export const mockedRegistration1: RegistrationSummaryIF = {
  baseRegistrationNumber: 'GOV2343',
  clientReferenceId: 'ABC123',
  createDateTime: '2021-07-20T17:21:17+00:00',
  expireDays: '100', // Number of days until expiry
  lastUpdateDateTime: '2021-10-04T18:26:11+00:00',
  path: '/path/to/doc',
  registeringParty: 'John Doe',
  registrationClass: 'PPSALIEN',
  registrationDescription: 'PPSA SECURITY AGREEMENT',
  registrationType: APIRegistrationTypes.SECURITY_AGREEMENT,
  securedParties: 'Bank of Nova Scotia',
  statusType: 'ACT'
}

export const mockedRegistration2: RegistrationSummaryIF = {
  baseRegistrationNumber: 'BC456788',
  clientReferenceId: '',
  createDateTime: '2021-07-20T17:21:17+00:00',
  expireDays: '316',
  path: '/path/to/doc',
  registeringParty: 'ICBC',
  registrationClass: 'PPSALIEN',
  registrationDescription: 'REPAIRERS LIEN',
  registrationType: APIAmendmentTypes.AMENDMENT,
  securedParties: 'Bank of Montreal',
  statusType: 'ACT'
}

export const mockedRegistration2Child: RegistrationSummaryIF = {
  baseRegistrationNumber: 'BC456788',
  clientReferenceId: '',
  createDateTime: '2021-07-20T17:21:17+00:00',
  path: '/path/to/doc',
  registeringParty: 'ICBC',
  registrationClass: 'AMENDMENT',
  registrationDescription: 'AMENDMENT/OTHER CHANGE',
  registrationNumber: 'BC456789',
  registrationType: APIAmendmentTypes.AMENDMENT,
  securedParties: 'Bank of Montreal'
}

export const mockedDraft1: DraftResultIF = {
  type: DraftTypes.FINANCING_STATEMENT,
  documentId: 'D9000018',
  baseRegistrationNumber: '',
  registrationType: APIRegistrationTypes.REPAIRERS_LIEN,
  registrationDescription: '',
  path: '/path/to/doc',
  createDateTime: '2021-08-03T17:21:17+00:00',
  clientReferenceId: 'FFF555'
}

export const mockedDraft2: DraftResultIF = {
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
  type: DraftTypes.AMENDMENT_STATEMENT,
  documentId: 'D9000019',
  baseRegistrationNumber: 'GOV2343',
  registrationType: APIRegistrationTypes.SECURITY_AGREEMENT,
  registrationDescription: '',
  path: '/path/to/doc',
  createDateTime: '2021-08-05T17:21:17+00:00',
  clientReferenceId: 'FFF555'
}
