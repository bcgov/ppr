import { MhrSubTypes } from '@/enums'
import { AccountInfoIF, UserAccessAuthorizationIF, PartyIF } from '@/interfaces'

export interface QsReviewConfirmIF {
  isRequirementsConfirmed: boolean
  authorization: UserAccessAuthorizationIF
}

export interface UserAccessIF {
  mrhSubProduct: MhrSubTypes
  qsInformation: PartyIF
  qsSubmittingParty: AccountInfoIF
  qsReviewConfirm: QsReviewConfirmIF
}

export interface UserAccessValidationIF {
  qsInformationValid: false,
  qsReviewConfirmValid: false
}
