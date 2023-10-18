// Libraries
import { createPinia } from 'pinia'
// export { useAuthStore, useNotificationStore, useAccountStore } from 'sbc-common-components/src/store'

/**
 * Configures and returns Pinia Store.
 */
export function getPiniaStore () {
  return createPinia()
}
