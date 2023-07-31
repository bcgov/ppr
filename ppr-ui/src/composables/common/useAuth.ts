import { computed, ComputedRef } from 'vue-demi'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'

export const useAuth = () => {
  /** Helper to check if the current user is authenticated */
  const isAuthenticated: ComputedRef<boolean> = computed((): boolean => {
    return Boolean(sessionStorage.getItem(SessionStorageKeys.KeyCloakToken))
  })

  return {
    isAuthenticated
  }
}
