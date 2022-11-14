import { RegistrationFlowType } from '@/enums'
import { StateModelIF } from '@/interfaces'

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
    registrationType: null,
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
  // MHR State
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
    documentId: ''
  },
  mhrRegistration: {
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
    attentionReferenceNum: '',
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
      otherType: null
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
    },
    notes: [
      {
        documentType: '',
        documentId: '',
        createDateTime: '',
        remarks: '',
        contactName: '',
        contactAddress: {
          street: '',
          city: '',
          region: '',
          postalCode: '',
          country: ''
        }
      }
    ]
  },
  mhrSearchResultSelectAllLien: false,
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
  mhrTransferValidationState: {
    homeOwnersValid: {
      ownersValid: false
    },
    reviewConfirmValid: {
      validateApp: false
    }
  },
  mhrTransfer: {
    mhrNumber: '',
    ownerGroups: [],
    currentOwnerGroups: [],
    submittingParty: {},
    declaredValue: null,
    consideration: '',
    transferDate: '',
    attentionReference: '',
    ownLand: false
  }
}
