import { SearchResponseIF, StateModelIF } from '@/interfaces'

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
  searching: false,
  searchResults: null
}
