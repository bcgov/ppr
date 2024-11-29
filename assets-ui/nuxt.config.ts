// https://nuxt.com/docs/api/configuration/nuxt-config
// import { defineNuxtConfig } from 'nuxt'
import path from 'path'
// import dotenv from 'dotenv'

// Load environment variables from .env file
// dotenv.config()

export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
  components: true,
  app: {
    buildAssetsDir: '/src/',
    head: {
      title: 'Assets UI',
      htmlAttrs: { dir: 'ltr' },
      link: [{ rel: 'icon', type: 'image/png', href: '/favicon.png' }]
    }
  },
  colorMode: {
    preference: 'light'
  },
  srcDir: 'src/',
  // envPrefix: 'VUE_APP_', // Need to remove this after fixing vaults. Use import.meta.env with VUE_APP.
  alias: {
    '@': path.resolve(__dirname, './src'),
    '@sbc': path.resolve(__dirname, './node_modules/sbc-common-components/src')
  },
  resolve: {
    extensions: ['.mjs', '.js', '.ts', '.jsx', '.tsx', '.json', '.vue']
  },
  scss: [
    '@mdi/font/css/materialdesignicons.css',
    '@/assets/styles/base.scss',
    '@/assets/styles/layout.scss',
    '@/assets/styles/overrides.scss',
    '@sbc/assets/styles/theme.scss',
  ],
  ui: {
    icons: ['mdi']
  },
  ssr: false,
  modules: ['@pinia/nuxt', "@nuxt/eslint", 'vuetify-nuxt-module', 'nuxt-lodash'],
  plugins: [],
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
  },
  runtimeConfig: {
    public: {
      VUE_APP_PATH: process.env.VUE_APP_PATH || '',
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