import { APIRegistrationTypes, UIRegistrationTypes } from '@/enums'

// Search type interface
export interface RegistrationTypeIF {
  class: string
  disabled: boolean
  divider: boolean
  group: number
  registrationTypeUI: UIRegistrationTypes
  registrationTypeAPI: APIRegistrationTypes
  text: string
}
