export interface MhrValidationStateIF {
  yourHomeValid: {
    makeModelValid: boolean
    homeSectionsValid: boolean
    homeCertificationValid: boolean
    rebuiltStatusValid: boolean
    otherValid: boolean
  },
  submittingPartyValid: {
    documentIdValid: boolean
    submitterValid: boolean
    refNumValid: boolean
  },
  homeOwnersValid: {
    ownersValid: boolean
  },
  addEditOwnersValid: {
    ownersValid: boolean
  },
  locationValid: {
    locationTypeValid: boolean
    civicAddressValid: boolean
  },
  reviewConfirmValid: {
    authorizationValid: boolean
    staffPaymentValid: boolean
    validateSteps: boolean
    validateApp: boolean
  }
}

export interface MhrTransferValidationStateIF {
  homeOwnersValid: {
    ownersValid: boolean
  },
  reviewConfirmValid: {
    validateApp: boolean
  }
}
