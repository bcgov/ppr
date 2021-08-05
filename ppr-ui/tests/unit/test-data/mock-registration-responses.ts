import { APIRegistrationTypes, DraftTypes } from '@/enums'
import { DraftIF, RegistrationIF } from '@/interfaces'


export const mockedRegistration1: RegistrationIF = {
  registrationNumber: 'GOV12343',
  clientReferenceId: 'ABC123', 
  registrationType: APIRegistrationTypes.SECURITY_AGREEMENT,
  registeringParty: 'John Doe',
  securedParties: 'Bank of Nova Scotia',
  expireDays: '100', // Number of days until expiry
  statusType: 'ACT',
  path: '/path/to/doc',
  createDateTime: '2021-07-20T17:21:17+00:00'
}


export const mockedRegistration2: RegistrationIF = {
  registrationNumber: 'BC456789',
  clientReferenceId: '', 
  registrationType: APIRegistrationTypes.SECURITY_AGREEMENT,
  registeringParty: 'ICBC',
  securedParties: 'Bank of Montreal',
  expireDays: '10', // Number of days until expiry
  statusType: 'ACT',
  path: '/path/to/doc',
  createDateTime: '2021-07-20T17:21:17+00:00'
}

export const mockedDraft1: DraftIF = {
  type: DraftTypes.FINANCING_STATEMENT,
    documentId: 'D9000018',
    baseRegistrationNumber: '',
    registrationType: APIRegistrationTypes.REPAIRERS_LIEN,
    registrationDescription: '',
    path: '/path/to/doc',
    createDateTime: '2021-08-03T17:21:17+00:00',
    clientReferenceId: ''
}

export const mockedDraft2: DraftIF = {
  type: DraftTypes.FINANCING_STATEMENT,
    documentId: 'D9000338',
    baseRegistrationNumber: '',
    registrationType: APIRegistrationTypes.MISCELLANEOUS_OTHER,
    registrationDescription: '',
    path: '/path/to/doc',
    createDateTime: '2021-08-01T17:21:17+00:00',
    clientReferenceId: ''
}
