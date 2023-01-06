export enum MhrSectVal {
  YOUR_HOME_VALID = 'yourHomeValid',
  SUBMITTING_PARTY_VALID = 'submittingPartyValid',
  HOME_OWNERS_VALID = 'homeOwnersValid',
  ADD_EDIT_OWNERS_VALID = 'addEditOwnersValid',
  LOCATION_VALID = 'locationValid',
  REVIEW_CONFIRM_VALID = 'reviewConfirmValid'
}

export enum MhrCompVal {
  // Your Home Section
  MAKE_MODEL_VALID = 'makeModelValid',
  HOME_SECTION_VALID = 'homeSectionsValid',
  HOME_CERTIFICATION_VALID = 'homeCertificationValid',
  REBUILT_STATUS_VALID = 'rebuiltStatusValid',
  OTHER_VALID = 'otherValid',

  // Submitting Party Section
  SUBMITTER_VALID = 'submitterValid',
  DOC_ID_VALID = 'documentIdValid',
  REF_NUM_VALID = 'refNumValid',

  // HomeOwners Section
  OWNERS_VALID = 'ownersValid',

  // Location Section
  LOCATION_TYPE_VALID = 'locationTypeValid',
  CIVIC_ADDRESS_VALID = 'civicAddressValid',

  // Review Confirm Section
  AUTHORIZATION_VALID = 'authorizationValid',
  STAFF_PAYMENT_VALID = 'staffPaymentValid',
  VALIDATE_STEPS = 'validateSteps', // prompt all Step validations
  VALIDATE_APP = 'validateApp' // prompt all APP validations

}
