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
  savedResults: null,
  searchResults: null,
  searchedType: null,
  searchedValue: ''
}
