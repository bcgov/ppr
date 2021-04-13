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
  searching: false,
  userInfo: {
    contacts: [],
    firstname: '',
    lastname: '',
    username: '',
    settings: {
      paymentConfirmationDialog: true,
      selectConfirmationDialog: true
    }
  }
}
