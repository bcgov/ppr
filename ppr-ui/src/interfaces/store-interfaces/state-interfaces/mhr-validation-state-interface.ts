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

export interface mhrInfoValidationStateIF {
  isValidTransferType: false,
  isValidTransferOwners: false,
  isTransferDetailsValid: false,
  isSubmittingPartyValid: false,
  isRefNumValid: false,
  isCompletionConfirmed: false,
  isAuthorizationValid: false,
  isStaffPaymentValid: false
}

export interface MhrValidationManufacturerStateIF {
  yourHomeValid: {
    makeModelValid: boolean,
    homeSectionsValid: boolean,
    homeCertificationValid: boolean,
  },
  reviewConfirmValid: {
    attentionValid: boolean,
    authorizationValid: boolean,
    refNumValid: boolean,
    validateSteps: boolean,
    validateApp: boolean
  }
}

export interface MhrUnitNoteValidationStateIF {
  unitNoteAddValid: {
    documentIdValid: boolean,
    remarksValid: boolean,
    personGivingNoticeValid: boolean,
    submittingPartyValid: boolean,
    attentionValid: boolean,
    authorizationValid: boolean,
    staffPaymentValid: boolean
  }
}
