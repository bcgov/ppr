import { FeeSummaryTypes } from '@/composables/fees/enums'
import { UIRegistrationTypes } from '@/enums'
import { RegistrationLengthI } from '@/composables/fees/interfaces/registration-length'

// Defines the additional search data required for the Fee Summary when there is multiple fees to display
export interface AdditionalSearchFeeIF {
  feeType: FeeSummaryTypes,
  quantity: number,
  registrationType?: UIRegistrationTypes
  registrationLength?: RegistrationLengthI
}
