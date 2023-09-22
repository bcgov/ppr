// Core Libraries
import 'core-js/stable' // to polyfill ECMAScript features
import 'regenerator-runtime/runtime' // to use transpiled generator functions
import 'moment'
import VueAxe from 'vue-axe'

// Vue Libraries
import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import Vuelidate from 'vuelidate'
import { getVueRouter } from '@/router'
import { getPiniaStore, getVuexStore } from '@/store'
import Affix from 'vue-affix'
import * as Sentry from '@sentry/vue'
import { TiptapVuetifyPlugin } from 'tiptap-vuetify'
// Styles
// NB: order matters - do not change
import '@mdi/font/css/materialdesignicons.min.css' // ensure you are using css-loader
import '@/assets/styles/base.scss'
import '@/assets/styles/layout.scss'
import '@/assets/styles/overrides.scss'
// tiptap editor
import 'tiptap-vuetify/dist/main.css'

// Base App
import App from './App.vue'

// Helpers
import { getFeatureFlag, fetchConfig, initLdClient, isSigningIn, isSigningOut } from '@/utils'
import KeycloakService from 'sbc-common-components/src/services/keycloak.services'
import { ExecutorBusinessIcon, ExecutorPersonIcon, HomeLocationIcon, HomeOwnersIcon } from './assets/svgs/index'

// get rid of "element implicitly has an 'any' type..."
declare const window: any

Vue.config.productionTip = false

Vue.use(Vuetify)
Vue.use(Affix)
Vue.use(Vuelidate)

const vuetify = new Vuetify()
// use this package's plugin
Vue.use(TiptapVuetifyPlugin, {
  // the next line is important! You need to provide the Vuetify Object to this place.
  vuetify, // same as "vuetify: vuetify"
  // optional, default to 'md' (default vuetify icons before v2.0.0)
  iconsGroup: 'mdi'
})

// main code
async function start () {
  // fetch config from environment and API
  // must come first as inits below depend on config
  await fetchConfig()

  // initialize Launch Darkly
  if (window.ldClientId) {
    await initLdClient()
  }

  // For now, ONLY run for local development
  // In your local .env add: VUE_APP_LOCAL_DEV="true"
  if (process.env.VUE_APP_LOCAL_DEV === 'true') {
    Vue.use(VueAxe, {
      // You can customize the configuration here if needed
      allowConsoleClears: false
    })
  }

  if (getFeatureFlag('sentry-enable')) {
    // initialize Sentry
    console.info('Initializing Sentry...') // eslint-disable-line no-console
    Sentry.init({
      Vue,
      dsn: window['sentryDsn'] // eslint-disable-line dot-notation
    })
  }

  // Initialize Keycloak / sync SSO
  await syncSession()

  // start Vue application
  console.info('Starting app...') // eslint-disable-line no-console
  new Vue({
    vuetify: new Vuetify({
      iconfont: 'mdi',
      theme: {
        themes: {
          light: {
            primary: '#1669bb', // same as $$primary-blue
            darkBlue: '#38598a',
            lightBlue: '#E2E8EE', // same as $app-lt-blue
            error: '#d3272c',
            success: '#1a9031',
            darkGray: '#495057', // same as theme $gray7
            caution: '#F8661A' // same as them $app-orange
          }
        }
      },
      icons: {
        values: {
          ExecutorBusinessIcon: { // name of our custom icon
            component: ExecutorBusinessIcon // our custom component
          },
          ExecutorPersonIcon: {
            component: ExecutorPersonIcon
          },
          HomeLocationIcon: {
            component: HomeLocationIcon
          },
          HomeOwnersIcon: {
            component: HomeOwnersIcon
          }
        }
      }
    }),
    router: getVueRouter(),
    store: getVuexStore(),
    render: h => h(App),
    pinia: getPiniaStore() // Having pinia last shows pinia in vue devtools plugins
  }).$mount('#app')
}

async function syncSession () {
  console.info('Starting Keycloak service...') // eslint-disable-line no-console
  const keycloakConfig: any = {
    url: `${window.keycloakAuthUrl}`,
    realm: `${window.keycloakRealm}`,
    clientId: `${window.keycloakClientId}`
  }

  await KeycloakService.setKeycloakConfigUrl(keycloakConfig)

  // Auto authenticate user only if they are not trying a login or logout
  if (!isSigningIn() && !isSigningOut()) {
    // Initialize token service which will do a check-sso to initiate session
    await KeycloakService.initializeToken(null).then(() => { }).catch(err => {
      if (err?.message !== 'NOT_AUTHENTICATED') {
        throw err
      }
    })
  }
}

// execution and error handling
start().catch(error => {
  console.error(error) // eslint-disable-line no-console
  alert('There was an error starting this page. (See console for details.)\n' +
    'Please try again later.')
})
