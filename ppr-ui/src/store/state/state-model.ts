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
  debtorName: null,
  searchHistory: null,
  searchResults: null,
  searchedType: null,
  searchedValue: '',
  userInfo: {
    firstname: '',
    lastname: '',
    username: '',
    settings: {
      paymentConfirmationDialog: true,
      selectConfirmationDialog: true
    }
  }
}
