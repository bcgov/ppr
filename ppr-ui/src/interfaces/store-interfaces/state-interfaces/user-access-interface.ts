import { MhrSubTypes } from '@/enums'
import { PartyIF } from '@/interfaces'

export interface UserAccessIF {
  mrhSubProduct: MhrSubTypes
  qsInformation: PartyIF
}

export interface UserAccessValidationIF {
  qsInformationValid: false,
  qsReviewConfirmValid: false
}
