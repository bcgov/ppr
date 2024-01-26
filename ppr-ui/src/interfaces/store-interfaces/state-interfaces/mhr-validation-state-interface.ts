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
    landDetailsValid: boolean
  },
  reviewConfirmValid: {
    authorizationValid: boolean
    staffPaymentValid: boolean
    validateSteps: boolean
    validateApp: boolean
  }
}

export interface mhrInfoValidationStateIF {
  isDocumentIdValid: false,
  isValidTransferType: false,
  isValidTransferOwners: false,
  isTransferDetailsValid: false,
  isSubmittingPartyValid: false,
  isRefNumValid: false,
  isCompletionConfirmed: false,
  isAuthorizationValid: false,
  isStaffPaymentValid: false,

  // transport permit state
  isLocationChangeTypeValid: boolean,
  isHomeLocationTypeValid: boolean,
  isHomeCivicAddressValid: boolean,
  isHomeLandOwnershipValid: boolean,
  isTaxCertificateValid: boolean,
  isNewPadNumberValid: boolean
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
    effectiveDateTimeValid: boolean,
    expiryDateTimeValid: boolean,
    attentionValid: boolean,
    authorizationValid: boolean,
    staffPaymentValid: boolean
  }
}
