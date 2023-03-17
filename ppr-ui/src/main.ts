// Core Libraries
import 'core-js/stable' // to polyfill ECMAScript features
import 'regenerator-runtime/runtime' // to use transpiled generator functions
import 'moment'

// Vue Libraries
import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import Vuelidate from 'vuelidate'
import VueCompositionApi from '@vue/composition-api'
import { getVueRouter } from '@/router'
import { getVuexStore } from '@/store'
import Affix from 'vue-affix'
import * as Sentry from '@sentry/browser'
import * as Integrations from '@sentry/integrations'
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
import { fetchConfig, initLdClient, isSigningIn, isSigningOut } from '@/utils'
import KeycloakService from 'sbc-common-components/src/services/keycloak.services'
import { HomeLocationIcon, HomeOwnersIcon } from './assets/svgs/Index'

// get rid of "element implicitly has an 'any' type..."
declare const window: any

Vue.config.productionTip = false

Vue.use(VueCompositionApi)
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

  if (window.sentryEnable === 'true') {
    // initialize Sentry
    console.info('Initializing Sentry...') // eslint-disable-line no-console
    Sentry.init({
      dsn: window['sentryDsn'], // eslint-disable-line dot-notation
      integrations: [new Integrations.Vue({ Vue, attachProps: true })]
    })
  }

  // initialize Launch Darkly
  if (window.ldClientId) {
    await initLdClient()
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
            darkGray: '#495057' // same as theme $gray7
          }
        }
      },
      icons: {
        values: {
          HomeLocationIcon: { // name of our custom icon
            component: HomeLocationIcon // our custom component
          },
          HomeOwnersIcon: {
            component: HomeOwnersIcon
          }
        }
      }
    }),
    router: getVueRouter(),
    store: getVuexStore(),
    render: h => h(App)
  }).$mount('#app')
}

async function syncSession () {
  console.info('Starting Keycloak service...') // eslint-disable-line no-console
  await KeycloakService.setKeycloakConfigUrl(sessionStorage.getItem('KEYCLOAK_CONFIG_PATH'))

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
