import type { MhrSubTypes } from '@/enums'
import type { AccountInfoIF, UserAccessAuthorizationIF, PartyIF, AddressIF } from '@/interfaces'

export interface UserAccessIF {
  mrhSubProduct: MhrSubTypes
  qsInformation: PartyIF
  location: {
    address: AddressIF
  }
  qsSubmittingParty: AccountInfoIF
  isRequirementsConfirmed: boolean
  authorization: UserAccessAuthorizationIF
}

export interface UserAccessValidationIF {
  qsInformationValid: boolean
  qsLocationValid: boolean
  qsSaConfirmValid: boolean
  qsReviewConfirmValid: boolean
}
