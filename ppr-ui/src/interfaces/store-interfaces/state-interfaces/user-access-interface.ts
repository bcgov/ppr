import { MhrSubTypes } from '@/enums'
import { AccountInfoIF, UserAccessAuthorizationIF, PartyIF } from '@/interfaces'

export interface UserAccessIF {
  mrhSubProduct: MhrSubTypes
  qsInformation: PartyIF
  qsSubmittingParty: AccountInfoIF
  isRequirementsConfirmed: boolean
  authorization: UserAccessAuthorizationIF
}

export interface UserAccessValidationIF {
  qsInformationValid: boolean
  qsSaConfirmValid: boolean
  qsReviewConfirmValid: boolean
}
