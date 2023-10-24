// Core Libraries
import 'regenerator-runtime/runtime' // to use transpiled generator functions

// Vue Libraries
import { createApp } from 'vue'
import Vuelidate from 'vuelidate'
import { getVueRouter } from '@/router'
import { getPiniaStore } from '@/store'
import * as Sentry from '@sentry/vue'
import vuetify from './plugins/vuetify'

// Base App
// NB: must come before style imports
import App from '@/App.vue'

// Helpers
import { getFeatureFlag, fetchConfig, initLdClient, isSigningIn, isSigningOut } from '@/utils'
import KeycloakService from 'sbc-common-components/src/services/keycloak.services'
declare const window: any

// main code
async function start () {
  // fetch config from environment and API
  // must come first as inits below depend on config
  await fetchConfig()

  const router = getVueRouter()
  const app = createApp(App)
  const pinia = getPiniaStore()

  // initialize Launch Darkly
  if ((window as any).ldClientId) {
    console.info('Initializing Launch Darkly...') // eslint-disable-line no-console
    await initLdClient()
  }

  if (getFeatureFlag('sentry-enable')) {
    // initialize Sentry
    console.info('Initializing Sentry...') // eslint-disable-line no-console
    Sentry.init({
      app,
      dsn: (window as any).sentryDsn
    })
  }

  // configure KeyCloak Service
  console.info('Starting Keycloak service...') // eslint-disable-line no-console
  const keycloakConfig: any = {
    url: `${window.keycloakAuthUrl}`,
    realm: `${window.keycloakRealm}`,
    clientId: `${window.keycloakClientId}`
  }
  await KeycloakService.setKeycloakConfigUrl(keycloakConfig)

  // Auto authenticate user only if they are not trying a login or logout
  if (!isSigningIn() && !isSigningOut()) {
    console.log('inside initalize token')
    // Initialize token service which will do a check-sso to initiate session
    await KeycloakService.initializeToken(null).then(() => { }).catch(err => {
      console.log(err)
      if (err?.message !== 'NOT_AUTHENTICATED') {
        throw err
      }
    })
  }

  // start Vue application
  console.info('Starting app...')
  app.use(Vuelidate)
  app.use(router)
  app.use(pinia)
  app.use(vuetify)
  app.mount('#app')
}

// execution and error handling
start().catch(error => {
  // log any error after configuring sentry.
  // it helps to identify configuration issues specific to the environment.
  // note that it won't log anything related to `FetchConfig()` since sentry is depending on a config value.
  Sentry.captureException(error)
  console.error(error) // eslint-disable-line no-console
  alert('There was an error starting this page. (See console for details.)\n' +
    'Please try again later.')
})
