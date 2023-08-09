import { MhrSubTypes } from '@/enums'
import { AccountInfoIF, PartyIF } from '@/interfaces'

export interface UserAccessIF {
  mrhSubProduct: MhrSubTypes
  qsInformation: PartyIF
  qsSubmittingParty: AccountInfoIF
}

export interface UserAccessValidationIF {
  qsInformationValid: false,
  qsReviewConfirmValid: false
}
