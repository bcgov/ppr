import { RegistrationFlowType } from '@/enums'
import { PartyIF, RegistrationTypeIF, StateModelIF, SubmittingPartyIF } from '@/interfaces'

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
    }
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
    lienRegistrationType: ''
  },
  // Manufactured Home Registration State
  mhrRegistration: {
    draftNumber: '',
    documentId: '',
    clientReferenceId: '',
    declaredValue: '',
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
        region: '',
        country: '',
        postalCode: ''
      },
      emailAddress: '',
      phoneNumber: '',
      phoneExtension: ''
    },
    ownerGroups: [],
    isManualLocationInfo: false,
    ownLand: false,
    attentionReference: '',
    location: {
      parkName: '',
      pad: '',
      address: {
        street: '',
        streetAdditional: '',
        city: '',
        region: '',
        country: '',
        postalCode: ''
      },
      leaveProvince: false,
      pidNumber: '',
      taxCertificate: false,
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
      rebuiltRemarks: '',
      otherRemarks: ''
    }
  },
  // Mhr Unit Notes
  mhrUnitNotes: [],
  mhrSearchResultSelectAllLien: false,
  // Manufactured Home Registration Validation Flags
  mhrValidationState: {
    yourHomeValid: {
      makeModelValid: false,
      homeSectionsValid: false,
      homeCertificationValid: false,
      rebuiltStatusValid: false,
      otherValid: false
    },
    submittingPartyValid: {
      submitterValid: false,
      documentIdValid: false,
      refNumValid: false
    },
    homeOwnersValid: {
      ownersValid: false
    },
    addEditOwnersValid: {
      ownersValid: true
    },
    locationValid: {
      locationTypeValid: false,
      civicAddressValid: false
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
    transferType: null,
    declaredValue: null,
    consideration: '',
    transferDate: '',
    attentionReference: '',
    ownLand: false,
    isAffidavitTransferCompleted: false
  },
  mhrUnitNote: { // standalone singe note used for Unit Note filing/registration
    clientReferenceId: '',
    attentionReference: '',
    submittingParty: {
      businessName: '',
      address: {
        street: '',
        streetAdditional: '',
        city: '',
        region: '',
        country: '',
        postalCode: ''
      },
      phoneNumber: '',
      emailAddress: ''
    },
    note: {
      documentType: null,
      documentId: '',
      documentRegistrationNumber: '',
      documentDescription: '',
      createDateTime: '',
      effectiveDateTime: '',
      expiryDateTime: '',
      status: null,
      remarks: '',
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
          region: '',
          country: '',
          postalCode: ''
        },
        emailAddress: '',
        phoneNumber: ''
      } as PartyIF,
      destroyed: null
    }
  },
  mhrUnitNoteValidationState: {
    unitNoteAddValid: {
      documentIdValid: false,
      remarksValid: false,
      personGivingNoticeValid: false
    }
  },
  // Manufactured Home Registration Information Validation Flags
  mhrInfoValidationState: {
    isValidTransferType: false,
    isValidTransferOwners: false,
    isTransferDetailsValid: false,
    isSubmittingPartyValid: false,
    isRefNumValid: false,
    isCompletionConfirmed: false,
    isAuthorizationValid: false,
    isStaffPaymentValid: false
  }
}
