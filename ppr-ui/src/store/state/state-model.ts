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
  mhrRegistration: {
    clientReferenceId: '',
    declaredValue: '',
    registeringParty: {
      businessName: '',
      address: {
        street: '',
        city: '',
        region: '',
        country: '',
        postalCode: ''
      },
      emailAddress: '',
      phoneNumber: null,
      phoneExtension: null
    },
    owners: [
      {
        individualName: {
          first: '',
          last: ''
        },
        address: {
          street: '',
          city: '',
          region: '',
          country: '',
          postalCode: ''
        },
        type: ''
      }
    ],
    location: {
      parkName: '',
      pad: null,
      address: {
        street: '',
        city: '',
        region: '',
        country: '',
        postalCode: ''
      }
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
      engineerReportDate: '',
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
  registrationTable: {
    baseRegs: [],
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
  }
}
