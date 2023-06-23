export enum MhrSectVal {
  YOUR_HOME_VALID = 'yourHomeValid',
  SUBMITTING_PARTY_VALID = 'submittingPartyValid',
  HOME_OWNERS_VALID = 'homeOwnersValid',
  ADD_EDIT_OWNERS_VALID = 'addEditOwnersValid',
  LOCATION_VALID = 'locationValid',
  REVIEW_CONFIRM_VALID = 'reviewConfirmValid',
  UNIT_NOTE_VALID = 'unitNoteAddValid'
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
  DOC_ID_VALID = 'documentIdValid', // also used for Unit Note
  REF_NUM_VALID = 'refNumValid', // Under review and confirm section for manufacturer registration

  // HomeOwners Section
  OWNERS_VALID = 'ownersValid',

  // Location Section
  LOCATION_TYPE_VALID = 'locationTypeValid',
  CIVIC_ADDRESS_VALID = 'civicAddressValid',

  // Review Confirm Section
  ATTENTION_VALID = 'attentionValid', // Only used in Manufacturer registrations
  AUTHORIZATION_VALID = 'authorizationValid',
  STAFF_PAYMENT_VALID = 'staffPaymentValid', // Only used for staff registrations
  VALIDATE_STEPS = 'validateSteps', // prompt all Step validations
  VALIDATE_APP = 'validateApp', // prompt all APP validations

  // Unit Note Registration
  REMARKS_VALID = 'remarksValid',
  PERSON_GIVING_NOTICE_VALID = 'personGivingNoticeValid'
}
