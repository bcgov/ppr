import { StateModelIF } from '@/interfaces'

export const stateModel: StateModelIF = {
  tombstone: {
    keycloakRoles: [],
    authRoles: [],
    userInfo: null,
    haveChanges: false
  },
  accountInformation: {
    accountType: '',
    id: null,
    label: '',
    type: ''
  }
}
