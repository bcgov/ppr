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
  authorization: {
    keycloakRoles: [],
    authRoles: []
  },
  registration: {
    amendmentDescription: '',
    collateral: {
      valid: false,
      vehicleCollateral: [],
      generalCollateral: []
    },
    confirmDebtorName: null,
    courtOrderInformation: null,
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
  // used for amendments only
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
  search: {
    searchDebtorName: null,
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
