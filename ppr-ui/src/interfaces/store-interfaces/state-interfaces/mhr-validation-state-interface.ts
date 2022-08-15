export interface MhrValidationStateIF {
  yourHomeValid: {
    makeModelValid: boolean
    homeSectionsValid: boolean
    homeCertificationValid: boolean
    rebuiltStatusValid: boolean
    otherValid: boolean
  },
  submittingPartyValid: {
    submitterValid: boolean
    refNumValid: boolean
  },
  homeOwnersValid: {
    OwnersValid: boolean
  },
  locationValid: {
    locationTypeValid: boolean
    civicAddressValid: boolean
  },
  reviewConfirmValid: {
    validateApp: boolean
    authorizationValid: boolean
    staffPaymentValid: boolean
  }
}
