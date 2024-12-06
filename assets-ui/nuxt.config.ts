// https://nuxt.com/docs/api/configuration/nuxt-config
import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'
import path from 'path'

export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
  // components: true,
  components: [
    '~/components', // Auto-import components from the components directory
    '~/components/collateral',
    '~/components/collateral/generalCollateral',
    '~/components/collateral/vehicle',
    '~/components/common',
    '~/components/dashboard',
    '~/components/dialogs',
    '~/components/dialogs/common',
    '~/components/exemptions',
    '~/components/mhrHistory',
    '~/components/mhrRegistration',
    '~/components/mhrRegistration/HomeLocation',
    '~/components/mhrRegistration/HomeOwners',
    '~/components/mhrRegistration/ReviewConfirm',
    '~/components/mhrRegistration/YourHome',
    '~/components/mhrTransfers',
    '~/components/mhrTransportPermits',
    '~/components/mhrTransportPermits/ConfirmCompletionContent',
    '~/components/mhrTransportPermits/HelpContent',
    '~/components/parties',
    '~/components/parties/debtor',
    '~/components/parties/party',
    '~/components/parties/summaries',
    '~/components/registration',
    '~/components/registration/length-trust',
    '~/components/registration/securities-act-notices',
    '~/components/search',
    '~/components/tables',
    '~/components/tables/common',
    '~/components/tables/mhr',
    '~/components/tables/ppr',
    '~/components/tombstones',
    '~/components/unitNotes',
    '~/components/userAccess'
  ],
  app: {
    buildAssetsDir: '/src/',
    head: {
      title: 'Assets UI',
      htmlAttrs: { dir: 'ltr' },
      link: [{ rel: 'icon', type: 'image/png', href: './src/assets/favicon.png' }]
    }
  },
  build: {
    transpile: ['vuetify'],
  },
  colorMode: {
    preference: 'light'
  },
  srcDir: 'src/',
  alias: {
    '@': path.resolve(__dirname, './src'),
    '@sbc': path.resolve(__dirname, './node_modules/sbc-common-components/src')
  },
  resolve: {
    extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.vue', '.scss', '.css']
  },
  ui: {
    icons: ['mdi']
  },
  ssr: false,
  server: {
    hmr: {
      overlay: false, // Disable the error overlay
      clientPort: 443, // Specify the client port if needed
    },
    watch: {
      usePolling: true, // Use polling for file changes
      interval: 1000, // Polling interval in milliseconds
    },
  },
  modules: ['@pinia/nuxt', '@nuxt/eslint', 'nuxt-lodash',
    (_options, nuxt) => {
      nuxt.hooks.hook('vite:extendConfig', (config) => {
        config.plugins.push(vuetify({ autoImport: true }))
      })
    }
  ],
  typescript: {
    tsConfig: {
      compilerOptions: {
        module: "esnext",
        dynamicImport: true,
        noImplicitAny: false,
        strictNullChecks: false,
        strict: true
      }
    },
    // NOTE: https://github.com/vuejs/language-tools/issues/3969
    typeCheck: false
  },
  vite: {
    optimizeDeps: {
      include: [
        'vuelidate',
        'lodash',
        'keycloak-js',
      ]
    },
    vue: {
      template: {
        transformAssetUrls,
      },
    }
  },
  runtimeConfig: {
    public: {
      VUE_APP_PATH: process.env.VUE_APP_PATH || '',
      VUE_APP_LOCAL_DEV: process.env.VUE_APP_LOCAL_DEV || '',
      BASE_URL: process.env.BASE_URL || '',
      VUE_APP_AUTH_API_URL: process.env.VUE_APP_AUTH_API_URL || '',
      VUE_APP_AUTH_API_VERSION: process.env.VUE_APP_AUTH_API_VERSION || '',
      VUE_APP_PAY_API_URL: process.env.VUE_APP_PAY_API_URL || '',
      VUE_APP_PAY_API_VERSION: process.env.VUE_APP_PAY_API_VERSION || '',
      VUE_APP_PPR_API_URL: process.env.VUE_APP_PPR_API_URL || '',
      VUE_APP_PPR_API_VERSION: process.env.VUE_APP_PPR_API_VERSION || '',
      VUE_APP_PPR_API_KEY: process.env.VUE_APP_PPR_API_KEY || '',
      VUE_APP_MHR_API_URL: process.env.VUE_APP_MHR_API_URL || '',
      VUE_APP_MHR_API_VERSION: process.env.VUE_APP_MHR_API_VERSION || '',
      VUE_APP_DOC_API_URL: process.env.VUE_APP_DOC_API_URL || '',
      VUE_APP_DOC_API_VERSION: process.env.VUE_APP_DOC_API_VERSION || '',
      VUE_APP_DOC_API_KEY: process.env.VUE_APP_DOC_API_KEY || '',
      VUE_APP_LTSA_API_URL: process.env.VUE_APP_LTSA_API_URL || '',
      VUE_APP_LTSA_API_VERSION: process.env.VUE_APP_LTSA_API_VERSION || '',
      VUE_APP_REGISTRIES_SEARCH_API_URL: process.env.VUE_APP_REGISTRIES_SEARCH_API_URL || '',
      VUE_APP_REGISTRIES_SEARCH_API_VERSION: process.env.VUE_APP_REGISTRIES_SEARCH_API_VERSION || '',
      VUE_APP_REGISTRIES_SEARCH_API_KEY: process.env.VUE_APP_REGISTRIES_SEARCH_API_KEY || '',
      VUE_APP_REGISTRY_URL: process.env.VUE_APP_REGISTRY_URL || '',
      VUE_APP_DOCUMENTS_UI_URL: process.env.VUE_APP_DOCUMENTS_UI_URL || '',
      VUE_APP_VON_API_URL: process.env.VUE_APP_VON_API_URL || '',
      VUE_APP_VON_API_VERSION: process.env.VUE_APP_VON_API_VERSION || '',
      VUE_APP_STATUS_API_URL: process.env.VUE_APP_STATUS_API_URL || '',
      VUE_APP_STATUS_API_VERSION: process.env.VUE_APP_STATUS_API_VERSION || '',
      VUE_APP_AUTH_WEB_URL: process.env.VUE_APP_AUTH_WEB_URL || '',
      VUE_APP_PPR_LD_CLIENT_ID: process.env.VUE_APP_PPR_LD_CLIENT_ID || '',
      VUE_APP_PPR_STAFF_PARTY_CODE: process.env.VUE_APP_PPR_STAFF_PARTY_CODE || '',
      VUE_APP_BCOL_STAFF_PARTY_CODE: process.env.VUE_APP_BCOL_STAFF_PARTY_CODE || '',
      VUE_APP_SENTRY_DSN: process.env.VUE_APP_SENTRY_DSN || '',
      VUE_APP_KEYCLOAK_AUTH_URL: process.env.VUE_APP_KEYCLOAK_AUTH_URL || '',
      VUE_APP_KEYCLOAK_REALM: process.env.VUE_APP_KEYCLOAK_REALM || '',
      VUE_APP_KEYCLOAK_CLIENTID: process.env.VUE_APP_KEYCLOAK_CLIENTID || '',
      VUE_APP_POD_NAMESPACE: process.env.VUE_APP_POD_NAMESPACE || 'unknown',
      VUE_APP_ADDRESS_COMPLETE_KEY: process.env.VUE_APP_ADDRESS_COMPLETE_KEY || '',
      VUE_APP_SITEMINDER_LOGOUT_URL: process.env.VUE_APP_SITEMINDER_LOGOUT_URL || '',
      keycloakAuthUrl: process.env.VUE_APP_KEYCLOAK_AUTH_URL || '',
      keycloakRealm: process.env.VUE_APP_KEYCLOAK_REALM || '',
      keycloakClientId: process.env.VUE_APP_KEYCLOAK_CLIENTID || '',
      appNameDisplay: 'assets-ui'
    }
  }
})