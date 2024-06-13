import { RegistrationFlowType, UnitNoteStatusTypes } from '@/enums'
import { MhrTransportPermitIF, PartyIF, RegistrationTypeIF, StateModelIF } from '@/interfaces'

export const stateModel: StateModelIF = {
  accountInformation: {
    accountType: '',
    id: null,
    label: '',
    type: ''
  },
  accountProductSubscriptions: null,
  userProductSubscriptions: [],
  userProductSubscriptionsCodes: [],
  authorization: {
    authRoles: [],
    isSbc: false
  },
  certifyInformation: {
    valid: false,
    certified: false,
    legalName: ''
  },
  folioOrReferenceNumber: '',
  // orig reg party used for discharge/renew/amend, other for amend only
  originalRegistration: {
    collateral: {
      valid: true,
      vehicleCollateral: [],
      generalCollateral: []
    },
    lengthTrust: {
      valid: true,
      lifeYears: 0,
      lifeInfinite: false,
      trustIndenture: false,
      lienAmount: '',
      surrenderDate: ''
    },
    parties: {
      valid: true,
      registeringParty: null,
      securedParties: [],
      debtors: []
    }
  },
  // PPR Registration Submission State
  registration: {
    amendmentDescription: '',
    collateral: {
      valid: false,
      vehicleCollateral: [],
      generalCollateral: []
    },
    confirmDebtorName: null,
    courtOrderInformation: {
      orderDate: '',
      effectOfOrder: '',
      courtName: '',
      courtRegistry: '',
      fileNumber: ''
    },
    creationDate: '',
    draft: {
      type: null,
      financingStatement: null,
      amendmentStatement: null,
      createDateTime: null,
      lastUpdateDateTime: null
    },
    expiryDate: '',
    lengthTrust: {
      valid: false,
      showInvalid: false,
      lifeYears: 0,
      lifeInfinite: false,
      trustIndenture: false,
      lienAmount: '',
      surrenderDate: ''
    },
    registrationNumber: '',
    registrationType: {} as RegistrationTypeIF,
    registrationFlowType: RegistrationFlowType.NEW,
    registrationTypeOtherDesc: null,
    showStepErrors: false,
    parties: {
      valid: false,
      registeringParty: null,
      securedParties: [],
      debtors: []
    },
    securitiesActNotices: []
  },
  // PPR and MHR Registration Table State
  registrationTable: {
    baseRegs: [],
    baseMhRegs: [],
    draftsBaseReg: [],
    draftsChildReg: [],
    newItem: {
      addedReg: '',
      addedRegParent: '',
      addedRegSummary: null,
      prevDraft: ''
    },
    sortHasMorePages: true,
    sortOptions: {
      endDate: null,
      folNum: '',
      orderBy: 'createDateTime',
      orderVal: 'desc',
      regBy: '',
      regNum: '',
      regParty: '',
      regType: '',
      secParty: '',
      startDate: null,
      status: ''
    },
    sortPage: 1,
    totalRowCount: 0
  },
  // PPR and MHR Search Request State
  search: {
    searchDebtorName: null,
    searchHistory: null,
    searchHistoryLength: null,
    searchResults: null,
    manufacturedHomeSearchResults: null,
    searchedType: null,
    searchedValue: '',
    searching: false,
    searchCertified: false
  },
  selectedManufacturedHomes: [],
  isStaffClientPayment: false,
  staffPayment: null,
  unsavedChanges: false,
  currentRegistrationsTab: 0,
  userInfo: {
    contacts: [],
    feeSettings: null,
    firstname: '',
    lastname: '',
    username: '',
    settings: {
      defaultDropDowns: true,
      defaultTableFilters: true,
      paymentConfirmationDialog: true,
      selectConfirmationDialog: true
    }
  },
  // Base MHR Information State
  mhrInformation: {
    clientReferenceId: '',
    createDateTime: '',
    mhrNumber: '',
    ownerNames: '',
    path: '',
    registrationDescription: '',
    statusType: '',
    submittingParty: '',
    username: '',
    documentId: '',
    lienRegistrationType: '',
    frozenDocumentType: '',
    permitDateTime: '',
    permitExpiryDateTime: '',
    permitRegistrationNumber: '',
    permitStatus: null,
    permitLandStatusConfirmation: null
  },
  // Manufactured Home Registration State
  mhrRegistration: {
    draftNumber: '',
    documentId: '',
    clientReferenceId: '',
    declaredValue: '',
    statusType: null,
    submittingParty: {
      personName: {
        first: '',
        last: '',
        middle: ''
      },
      businessName: '',
      address: {
        street: '',
        city: '',
        region: null,
        country: null,
        postalCode: ''
      },
      emailAddress: '',
      phoneNumber: '',
      phoneExtension: ''
    },
    ownerGroups: [],
    isManualLocationInfo: false,
    ownLand: null,
    attentionReference: '',
    location: {
      parkName: '',
      pad: '',
      address: {
        street: '',
        streetAdditional: '',
        city: '',
        region: null,
        country: null,
        postalCode: ''
      },
      leaveProvince: false,
      pidNumber: '',
      taxCertificate: false,
      taxExpiryDate: '',
      dealerName: '',
      additionalDescription: '',
      locationType: null,
      otherType: null,
      legalDescription: '',
      lot: '',
      parcel: '',
      block: '',
      districtLot: '',
      partOf: '',
      section: '',
      township: '',
      range: '',
      meridian: '',
      landDistrict: '',
      plan: '',
      bandName: '',
      reserveNumber: '',
      exceptionPlan: ''
    },
    description: {
      manufacturer: '',
      baseInformation: {
        year: null,
        circa: false,
        make: '',
        model: ''
      },
      sectionCount: null,
      sections: [],
      csaNumber: '',
      csaStandard: '',
      engineerName: '',
      engineerDate: '',
      certificationOption: null,
      hasNoCertification: null,
      rebuiltRemarks: '',
      otherRemarks: ''
    }
  },

  // mhrReRegistrationPreviousOwnerGroups?: null,
  // mhrReRegistrationPreviousOwnerGroups?: null,
  // Manufactured Home Registration baseline (Corrections/Amendments)
  mhrBaseline: null,
  // Mhr Transport Permit
  mhrTransportPermit: {
    documentId: '',
    clientReferenceId: '',
    submittingParty: {
      personName: {
        first: '',
        last: '',
        middle: ''
      },
      businessName: '',
      address: {
        street: '',
        city: '',
        region: null,
        country: null,
        postalCode: ''
      },
      emailAddress: '',
      phoneNumber: '',
      phoneExtension: ''
    },
    locationChangeType: null,
    newLocation: {
      parkName: '',
      pad: '',
      address: {
        street: '',
        streetAdditional: '',
        city: '',
        region: null,
        country: null,
        postalCode: ''
      },
      leaveProvince: false,
      pidNumber: '',
      taxCertificate: false,
      taxExpiryDate: '',
      dealerName: '',
      additionalDescription: '',
      locationType: null,
      otherType: null,
      legalDescription: '',
      lot: '',
      parcel: '',
      block: '',
      districtLot: '',
      partOf: '',
      section: '',
      township: '',
      range: '',
      meridian: '',
      landDistrict: '',
      plan: '',
      bandName: '',
      reserveNumber: '',
      exceptionPlan: ''
    },
    ownLand: null,
    landStatusConfirmation: false,
    amendment: false,
    registrationStatus: ''
  },
  mhrOriginalTransportPermit: {} as MhrTransportPermitIF,
  // Mhr Unit Notes
  mhrUnitNotes: [],
  mhrSearchResultSelectAllLien: false,
  // Manufactured Home Registration Validation Flags
  mhrValidationState: {
    submittingPartyValid: {
      documentIdValid: false,
      submitterValid: false,
      refNumValid: false
    },
    yourHomeValid: {
      makeModelValid: false,
      homeCertificationValid: false,
      homeSectionsValid: false,
      rebuiltStatusValid: false,
      otherValid: false
    },
    homeOwnersValid: {
      ownersValid: false
    },
    addEditOwnersValid: {
      ownersValid: true
    },
    locationValid: {
      locationTypeValid: false,
      civicAddressValid: false,
      landDetailsValid: false
    },
    reviewConfirmValid: {
      authorizationValid: false,
      staffPaymentValid: false,
      validateSteps: false,
      validateApp: false
    }
  },

  mhrValidationManufacturerState: {
    yourHomeValid: {
      makeModelValid: false,
      homeSectionsValid: false,
      homeCertificationValid: false
    },
    reviewConfirmValid: {
      attentionValid: false,
      refNumValid: false,
      authorizationValid: false,
      validateSteps: false,
      validateApp: false
    }
  },
  // Transfer of Ownership State
  mhrTransfer: {
    mhrNumber: '',
    ownerGroups: [],
    currentOwnerGroups: [],
    submittingParty: {
      emailAddress: '',
      phoneNumber: ''
    },
    documentId: '',
    transferType: null,
    declaredValue: null,
    consideration: '',
    transferDate: '',
    attentionReference: '',
    ownLand: null,
    isAffidavitTransferCompleted: false
  },
  mhrUnitNote: {
    // standalone singe note used for Unit Note filing/registration
    clientReferenceId: '',
    attentionReference: '',
    submittingParty: {
      personName: {
        first: '',
        last: '',
        middle: ''
      },
      businessName: '',
      address: {
        street: '',
        streetAdditional: '',
        city: '',
        region: null,
        country: null,
        postalCode: ''
      },
      emailAddress: '',
      phoneNumber: '',
      phoneExtension: ''
    },
    note: {
      documentType: null,
      documentId: '',
      documentRegistrationNumber: '',
      documentDescription: '',
      createDateTime: '',
      effectiveDateTime: '',
      expiryDateTime: '',
      status: UnitNoteStatusTypes.ACTIVE,
      remarks: '',
      additionalRemarks: '',
      givingNoticeParty: {
        businessName: '',
        personName: {
          first: '',
          last: '',
          middle: ''
        },
        address: {
          street: '',
          streetAdditional: '',
          city: '',
          region: null,
          country: null,
          postalCode: ''
        },
        emailAddress: '',
        phoneNumber: ''
      } as PartyIF,
      hasNoPersonGivingNotice: false,
      destroyed: false
    }
  },
  mhrUserAccess: {
    mrhSubProduct: null,
    qsInformation: {
      businessName: '',
      dbaName: '',
      address: {
        street: '',
        streetAdditional: '',
        city: '',
        region: null,
        postalCode: '',
        country: null,
        deliveryInstructions: ''
      },
      phoneNumber: '',
      phoneExtension: ''
    },
    location: {
      address: {
        street: '',
        streetAdditional: '',
        city: '',
        region: null,
        country: null,
        postalCode: ''
      }
    },
    isRequirementsConfirmed: false,
    authorization: {
      isAuthorizationConfirmed: false,
      authorizationName: '',
      date: ''
    },
    qsSubmittingParty: null
  },
  mhrExemption: {
    documentId: '',
    clientReferenceId: '',
    attentionReference: '',
    submittingParty: {
      personName: {
        first: '',
        last: '',
        middle: ''
      },
      businessName: '',
      address: {
        street: '',
        streetAdditional: '',
        city: '',
        region: null,
        country: null,
        postalCode: ''
      },
      emailAddress: '',
      phoneNumber: '',
      phoneExtension: ''
    },
    nonResidential: null,
    note: {
      documentType: null,
      remarks: '',
      destroyed: null,
      nonResidentialOption: null,
      nonResidentialReason: null,
      nonResidentialOther: null,
      expiryDateTime: null
    }
  },
  mhrExemptionValidation: {
    documentId: false,
    declarationDetails: false,
    remarks: true,
    submittingParty: false,
    attention: true,
    folio: true,
    confirmCompletion: false,
    authorization: false,
    staffPayment: false
  },
  mhrUserAccessValidation: {
    qsInformationValid: false,
    qsLocationValid: true,
    qsSaConfirmValid: false,
    qsReviewConfirmValid: false
  },
  mhrUnitNoteValidationState: {
    unitNoteAddValid: {
      documentIdValid: false,
      remarksValid: false,
      personGivingNoticeValid: false,
      submittingPartyValid: false,
      effectiveDateTimeValid: true, // pre-selected value is valid by default
      expiryDateTimeValid: true, // if pre-selected or absent, value is valid by default
      attentionValid: true, // optional so valid by default
      authorizationValid: false,
      staffPaymentValid: false
    }
  },
  // Manufactured Home Registration Information Validation Flags
  mhrInfoValidationState: {
    isDocumentIdValid: false,
    isValidTransferType: false,
    isValidTransferOwners: false,
    isTransferDetailsValid: false,
    isSubmittingPartyValid: false,
    isRefNumValid: false,
    isCompletionConfirmed: false,
    isAuthorizationValid: false,
    isStaffPaymentValid: false,
    // transport permit props
    isLocationChangeTypeValid: false,
    isHomeLocationTypeValid: false,
    isHomeCivicAddressValid: false,
    isHomeLandOwnershipValid: false,
    isTaxCertificateValid: false,
    isNewPadNumberValid: false
  }
}
