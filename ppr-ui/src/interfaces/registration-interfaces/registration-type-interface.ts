import { APIMhrDescriptionTypes, APIRegistrationTypes, UIMhrDescriptionTypes, UIRegistrationTypes } from '@/enums'

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

export interface MhRegistrationTypeIF {
  class: string
  disabled: boolean
  divider: boolean
  group: number
  registrationTypeUI: UIMhrDescriptionTypes,
  registrationTypeAPI: APIMhrDescriptionTypes,
  text: string
}
