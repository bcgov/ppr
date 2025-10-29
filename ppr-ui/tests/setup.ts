// Setup file for Vitest tests
import { vi } from 'vitest'
import { config } from '@vue/test-utils'
import * as nuxt from '#app'
import { createPinia, setActivePinia } from 'pinia'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

// Setup Vuetify
const vuetify = createVuetify({ components, directives })

// Setup Pinia
setActivePinia(createPinia())

// Apply global plugins
config.global.plugins = [vuetify, createPinia()]


vi.mock('#app', () => ({
  useRuntimeConfig: () => ({
    public: {
      ABOUT_TEXT: 'Mocked About Text',
      VUE_APP_PATH: 'mocked/path',
      VUE_APP_LOCAL_DEV: 'true',
      BASE_URL: 'http://mocked-base-url',
      VUE_APP_AUTH_API_URL: 'http://mocked-auth-api-url',
      VUE_APP_AUTH_API_VERSION: 'v1',
      VUE_APP_PAY_API_URL: 'http://mocked-pay-api-url',
      VUE_APP_PAY_API_VERSION: 'v1',
      VUE_APP_PPR_API_URL: 'http://mocked-ppr-api-url',
      VUE_APP_PPR_API_VERSION: 'v1',
      VUE_APP_PPR_API_KEY: 'mocked-ppr-api-key',
      VUE_APP_MHR_API_URL: 'http://mocked-mhr-api-url',
      VUE_APP_MHR_API_VERSION: 'v1',
      VUE_APP_DOC_API_URL: 'http://mocked-doc-api-url',
      VUE_APP_DOC_API_VERSION: 'v1',
      VUE_APP_DOC_API_KEY: 'mocked-doc-api-key',
      VUE_APP_LTSA_API_URL: 'http://mocked-ltsa-api-url',
      VUE_APP_LTSA_API_VERSION: 'v1',
      VUE_APP_REGISTRIES_SEARCH_API_URL: 'http://mocked-registries-search-api-url',
      VUE_APP_REGISTRIES_SEARCH_API_VERSION: 'v1',
      VUE_APP_REGISTRIES_SEARCH_API_KEY: 'mocked-registries-search-api-key',
      VUE_APP_REGISTRY_URL: 'http://mocked-registry-url',
      VUE_APP_DOCUMENTS_UI_URL: 'http://mocked-documents-ui-url',
      VUE_APP_VON_API_URL: 'http://mocked-von-api-url',
      VUE_APP_VON_API_VERSION: 'v1',
      VUE_APP_STATUS_API_URL: 'http://mocked-status-api-url',
      VUE_APP_STATUS_API_VERSION: 'v1',
      VUE_APP_AUTH_WEB_URL: 'http://mocked-auth-web-url',
      VUE_APP_PPR_LD_CLIENT_ID: '',
      VUE_APP_PPR_STAFF_PARTY_CODE: 'mocked-ppr-staff-party-code',
      VUE_APP_BCOL_STAFF_PARTY_CODE: 'mocked-bcol-staff-party-code',
      VUE_APP_SENTRY_DSN: 'mocked-sentry-dsn',
      VUE_APP_KEYCLOAK_AUTH_URL: 'http://mocked-keycloak-auth-url',
      VUE_APP_KEYCLOAK_REALM: 'mocked-keycloak-realm',
      VUE_APP_KEYCLOAK_CLIENTID: 'mocked-keycloak-clientid',
      VUE_APP_POD_NAMESPACE: 'mocked-namespace',
      VUE_APP_ADDRESS_COMPLETE_KEY: 'mocked-address-complete-key',
      VUE_APP_SITEMINDER_LOGOUT_URL: 'http://mocked-siteminder-logout-url',
      keycloakAuthUrl: 'http://mocked-keycloak-auth-url',
      keycloakRealm: 'mocked-keycloak-realm',
      keycloakClientId: 'mocked-keycloak-clientid',
      appNameDisplay: 'mocked-app-name'
    }
  }),
  useNuxtApp: () => ({
    $payApi: vi.fn(),
    $authApi: vi.fn(),
    $pprApi: vi.fn()
  })
}))


vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: vi.fn((key: string) => key)
  })
}))


vi.spyOn(nuxt, 'useNuxtApp').mockImplementation(() => ({
  $payApi: { /* mock methods here */ }
}))




