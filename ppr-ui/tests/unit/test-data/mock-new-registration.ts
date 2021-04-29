import { APIRegistrationTypes, UIRegistrationTypes } from '@/enums'
import { RegistrationTypeIF, ErrorIF } from '@/interfaces'

export const mockedSelectSecurityAgreement: RegistrationTypeIF = {
  divider: false,
  selectDisabled: false,
  registrationTypeUI: UIRegistrationTypes.SECURITY_AGREEMENT,
  registrationTypeAPI: APIRegistrationTypes.SECURITY_AGREEMENT,
  textLabel: ''
}

export const mockedError: ErrorIF = {
  statusCode: 500,
  message: 'mock error'
}
