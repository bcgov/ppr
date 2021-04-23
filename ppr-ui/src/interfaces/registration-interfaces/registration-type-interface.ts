import { APIRegistrationTypes, UIRegistrationTypes } from '@/enums'

// Search type interface
export interface RegistrationTypeIF {
  divider: boolean
  selectDisabled: boolean
  registrationTypeUI: UIRegistrationTypes
  registrationTypeAPI: APIRegistrationTypes
  textLabel: string
}
