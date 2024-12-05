import KeycloakService from 'sbc-common-components/src/services/keycloak.services'
import { isSigningIn, isSigningOut, fetchConfig } from '@/utils'

async function syncSession () {
  console.info('Starting Keycloak service...')
  const keycloakConfig: any = {
    url: `${window.keycloakAuthUrl}`,
    realm: `${window.keycloakRealm}`,
    clientId: `${window.keycloakClientId}`
  }

  await KeycloakService.setKeycloakConfigUrl(keycloakConfig)

  // Auto authenticate user only if they are not trying a login or logout
  if (!isSigningIn() && !isSigningOut()) {
    // Initialize token service which will do a check-sso to initiate session
    await KeycloakService.initializeToken(null).then(() => { console.log('has been initialized') }).catch(err => {
      if (err?.message !== 'NOT_AUTHENTICATED') {
        throw err
      }
    })
  }
}

export default defineNuxtPlugin(async nuxtApp => {
  await fetchConfig()
  await syncSession()
  console.log('Keycloak initialized')
})
