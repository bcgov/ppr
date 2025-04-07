import type { FeeSummaryTypes } from '@/composables/fees/enums'
import type { UIRegistrationTypes } from '@/enums'
import type { RegistrationLengthI } from '@/composables/fees/interfaces/registration-length'

// Defines the additional search data required for the Fee Summary when there is multiple fees to display
export interface AdditionalSearchFeeIF {
  feeType: FeeSummaryTypes,
  quantity: number,
  registrationType?: UIRegistrationTypes
  registrationLength?: RegistrationLengthI
}
