import { StateModelIF } from '@/interfaces'

export const stateModel: StateModelIF = {
  accountInformation: {
    accountType: '',
    id: null,
    label: '',
    type: ''
  },
  accountProductSubscriptions: null,
  authorization: {
    keycloakRoles: [],
    authRoles: []
  },
  registration: {
    collateral: {
      valid: false,
      vehicleCollateral: [],
      generalCollateral: ''
    },
    confirmDebtorName: null,
    creationDate: '',
    currentStep: 1,
    debtorName: null,
    draft: {
      type: '',
      financingStatement: null,
      createDateTime: null,
      lastUpdateDateTime: null
    },
    expiryDate: '',
    lengthTrust: {
      valid: false,
      lifeYears: 0,
      lifeInfinite: false,
      trustIndenture: false,
      lienAmount: '',
      surrenderDate: ''
    },
    registrationNumber: '',
    registrationType: null,
    registrationTypeOtherDesc: null,
    showStepErrors: false,
    parties: {
      valid: false,
      registeringParty: null,
      securedParties: [],
      debtors: []
    }
  },
  search: {
    searchHistory: null,
    searchResults: null,
    searchedType: null,
    searchedValue: '',
    searching: false
  },
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
  folioOrReferenceNumber: ''
}
