import { StateModelIF } from '@/interfaces'

export const stateModel: StateModelIF = {
  accountInformation: {
    accountType: '',
    id: null,
    label: '',
    type: ''
  },
  authorization: {
    keycloakRoles: [],
    authRoles: []
  },
  currentStep: 1,
  debtorName: null,
  draft: {
    type: '',
    financingStatement: null,
    createDateTime: null,
    lastUpdateDateTime: null
  },
  feeSummary: {
    feeAmount: 0,
    serviceFee: 1.50,
    quantity: 0,
    feeCode: ''
  },
  registrationType: null,
  searchHistory: null,
  searchResults: null,
  searchedType: null,
  searchedValue: '',
  searching: false,
  showStepErrors: false,
  userInfo: {
    contacts: [],
    firstname: '',
    lastname: '',
    username: '',
    settings: {
      paymentConfirmationDialog: true,
      selectConfirmationDialog: true
    }
  },
  lengthTrustStep: {
    valid: false,
    lifeYears: 0,
    lifeInfinite: false,
    trustIndenture: false
  },
  addSecuredPartiesAndDebtorsStep: {
    valid: false,
    registeringParty: null,
    securedParties: [],
    debtors: []
  },
  addCollateralStep: {
    valid: false,
    vehicleCollateral: [],
    generalCollateral: ''
  }
}
