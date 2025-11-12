// TypeScript
import { defineNuxtConfig } from 'nuxt/config'
import vuetify, { transformAssetUrls } from 'vite-plugin-vuetify'
import fs from 'fs'
import path from 'path'

const packageJson = fs.readFileSync('./package.json', 'utf-8')
const appName = JSON.parse(packageJson).appName
const appVersion = JSON.parse(packageJson).version

export default defineNuxtConfig({
  compatibilityDate: '2025-03-07',
  devtools: { enabled: true },

  components: {
    dirs: [{ path: '~/components', extensions: ['vue'], pathPrefix: false }]
  },

  extends: [
    '@sbc-connect/nuxt-core-layer-beta',
    'documents-common-base-layer'
  ],

  imports: {
    dirs: ['store', 'composables', 'enums', 'interfaces', 'utils']
  },

  app: {
    buildAssetsDir: '/src/',
    head: {
      title: 'Assets UI',
      htmlAttrs: { dir: 'ltr' },
      link: [
        { rel: 'icon', type: 'image/png', href: './src/assets/favicon.png' },
        {
          rel: 'stylesheet',
          type: 'text/css',
          href: 'https://ws1.postescanada-canadapost.ca/css/addresscomplete-2.30.min.css?key=tr28-mh11-ud79-br91'
        }
      ],
      script: [
        {
          src: 'https://ws1.postescanada-canadapost.ca/js/addresscomplete-2.30.js?key=tr28-mh11-ud79-br91&app=14466&culture=en',
          type: 'text/javascript'
        }
      ]
    }
  },

  build: {
    transpile: ['vuetify']
  },

  srcDir: 'src/',

  alias: {
    '@': path.resolve(__dirname, './src'),
    '@sbc': path.resolve(__dirname, './node_modules/sbc-common-components/src')
  },

  modules: [
    '@nuxt/eslint',
    '@pinia/nuxt',
    'nuxt-lodash',
    '@nuxt/test-utils/module',
    ['@nuxt/ui', { icons: ['mdi'] }],
    '@nuxtjs/i18n'
  ],

  css: ['~/assets/css/tw.css'],

  i18n: {
    locales: [
      { name: 'English', code: 'en-CA', iso: 'en-CA', dir: 'ltr', file: 'en-CA.ts' },
      { name: 'Français', code: 'fr-CA', iso: 'fr-CA', dir: 'ltr', file: 'fr-CA.ts' }
    ],
    bundle: {
      optimizeTranslationDirective: false
    },
    strategy: 'prefix',
    lazy: true,
    // Make this point to your actual locales folder; with srcDir set, prefer 'src/locales'
    langDir: 'locales',
    defaultLocale: 'en-CA',
    detectBrowserLanguage: false,
    // If your config file is under src/, use 'src/i18n.config.ts'
    vueI18n: './i18n.config.ts'
  },

  typescript: {
    tsConfig: {
      compilerOptions: {
        module: 'esnext',
        // dynamicImport is not a TS compiler option; safe to remove if present elsewhere
        // dynamicImport: true,
        noImplicitAny: false,
        strictNullChecks: false,
        strict: true
      }
    },
    typeCheck: false
  },

  vite: {

    css: {
      preprocessorOptions: {
        // for <style lang="scss">
        scss: {
          api: 'modern-compiler' // or 'modern'
        },
        // if you also use <style lang="sass">
        sass: {
          api: 'modern-compiler'
        }
      }
    },

    plugins: [
      vuetify({ styles: { configFile: '/assets/styles/vuetify-variables.scss' } })
    ],

    logLevel: 'silent',

    vue: {
      template: {
        transformAssetUrls
      }
    }
  },

  runtimeConfig: {
    public: {
      version: (appName && appVersion) ? `${appName} v${appVersion}` : '',
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
      sessionIdleTimeout: parseInt(process.env.NUXT_CONNECT_SESSION_INACTIVITY_TIMEOUT!) || 7200000,
      appNameDisplay: 'assets-ui'
    }
  }
})
