import { StateModelIF } from '@/interfaces'

export const stateModel: StateModelIF = {
  tombstone: {
    keycloakRoles: [],
    authRoles: [],
    userInfo: null
  },
  accountInformation: {
    accountType: '',
    id: null,
    label: '',
    type: ''
  },
  searchHistory: null,
  searchResults: null,
  searchedType: null,
  searchedValue: ''
}
