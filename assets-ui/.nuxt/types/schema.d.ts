import { NuxtModule, RuntimeConfig } from '@nuxt/schema'
declare module '@nuxt/schema' {
  interface NuxtOptions {
    /**
     * Configuration for `@pinia/nuxt`
     */
    ["pinia"]: typeof import("@pinia/nuxt").default extends NuxtModule<infer O> ? O : Record<string, any>
    /**
     * Configuration for `@nuxt/eslint`
     */
    ["eslint"]: typeof import("@nuxt/eslint").default extends NuxtModule<infer O> ? O : Record<string, any>
    /**
     * Configuration for `vuetify-nuxt-module`
     */
    ["vuetify"]: typeof import("vuetify-nuxt-module").default extends NuxtModule<infer O> ? O : Record<string, any>
    /**
     * Configuration for `nuxt-lodash`
     */
    ["lodash"]: typeof import("nuxt-lodash").default extends NuxtModule<infer O> ? O : Record<string, any>
    /**
     * Configuration for `@nuxt/devtools`
     */
    ["devtools"]: typeof import("@nuxt/devtools").default extends NuxtModule<infer O> ? O : Record<string, any>
    /**
     * Configuration for `@nuxt/telemetry`
     */
    ["telemetry"]: typeof import("@nuxt/telemetry").default extends NuxtModule<infer O> ? O : Record<string, any>
  }
  interface NuxtConfig {
    /**
     * Configuration for `@pinia/nuxt`
     */
    ["pinia"]?: typeof import("@pinia/nuxt").default extends NuxtModule<infer O> ? Partial<O> : Record<string, any>
    /**
     * Configuration for `@nuxt/eslint`
     */
    ["eslint"]?: typeof import("@nuxt/eslint").default extends NuxtModule<infer O> ? Partial<O> : Record<string, any>
    /**
     * Configuration for `vuetify-nuxt-module`
     */
    ["vuetify"]?: typeof import("vuetify-nuxt-module").default extends NuxtModule<infer O> ? Partial<O> : Record<string, any>
    /**
     * Configuration for `nuxt-lodash`
     */
    ["lodash"]?: typeof import("nuxt-lodash").default extends NuxtModule<infer O> ? Partial<O> : Record<string, any>
    /**
     * Configuration for `@nuxt/devtools`
     */
    ["devtools"]?: typeof import("@nuxt/devtools").default extends NuxtModule<infer O> ? Partial<O> : Record<string, any>
    /**
     * Configuration for `@nuxt/telemetry`
     */
    ["telemetry"]?: typeof import("@nuxt/telemetry").default extends NuxtModule<infer O> ? Partial<O> : Record<string, any>
    modules?: (undefined | null | false | NuxtModule<any> | string | [NuxtModule | string, Record<string, any>] | ["@pinia/nuxt", Exclude<NuxtConfig["pinia"], boolean>] | ["@nuxt/eslint", Exclude<NuxtConfig["eslint"], boolean>] | ["vuetify-nuxt-module", Exclude<NuxtConfig["vuetify"], boolean>] | ["nuxt-lodash", Exclude<NuxtConfig["lodash"], boolean>] | ["@nuxt/devtools", Exclude<NuxtConfig["devtools"], boolean>] | ["@nuxt/telemetry", Exclude<NuxtConfig["telemetry"], boolean>])[],
  }
}
declare module 'nuxt/schema' {
  interface NuxtOptions {
    /**
     * Configuration for `@pinia/nuxt`
     * @see https://www.npmjs.com/package/@pinia/nuxt
     */
    ["pinia"]: typeof import("@pinia/nuxt").default extends NuxtModule<infer O> ? O : Record<string, any>
    /**
     * Configuration for `@nuxt/eslint`
     * @see https://www.npmjs.com/package/@nuxt/eslint
     */
    ["eslint"]: typeof import("@nuxt/eslint").default extends NuxtModule<infer O> ? O : Record<string, any>
    /**
     * Configuration for `vuetify-nuxt-module`
     * @see https://www.npmjs.com/package/vuetify-nuxt-module
     */
    ["vuetify"]: typeof import("vuetify-nuxt-module").default extends NuxtModule<infer O> ? O : Record<string, any>
    /**
     * Configuration for `nuxt-lodash`
     * @see https://www.npmjs.com/package/nuxt-lodash
     */
    ["lodash"]: typeof import("nuxt-lodash").default extends NuxtModule<infer O> ? O : Record<string, any>
    /**
     * Configuration for `@nuxt/devtools`
     * @see https://www.npmjs.com/package/@nuxt/devtools
     */
    ["devtools"]: typeof import("@nuxt/devtools").default extends NuxtModule<infer O> ? O : Record<string, any>
    /**
     * Configuration for `@nuxt/telemetry`
     * @see https://www.npmjs.com/package/@nuxt/telemetry
     */
    ["telemetry"]: typeof import("@nuxt/telemetry").default extends NuxtModule<infer O> ? O : Record<string, any>
  }
  interface NuxtConfig {
    /**
     * Configuration for `@pinia/nuxt`
     * @see https://www.npmjs.com/package/@pinia/nuxt
     */
    ["pinia"]?: typeof import("@pinia/nuxt").default extends NuxtModule<infer O> ? Partial<O> : Record<string, any>
    /**
     * Configuration for `@nuxt/eslint`
     * @see https://www.npmjs.com/package/@nuxt/eslint
     */
    ["eslint"]?: typeof import("@nuxt/eslint").default extends NuxtModule<infer O> ? Partial<O> : Record<string, any>
    /**
     * Configuration for `vuetify-nuxt-module`
     * @see https://www.npmjs.com/package/vuetify-nuxt-module
     */
    ["vuetify"]?: typeof import("vuetify-nuxt-module").default extends NuxtModule<infer O> ? Partial<O> : Record<string, any>
    /**
     * Configuration for `nuxt-lodash`
     * @see https://www.npmjs.com/package/nuxt-lodash
     */
    ["lodash"]?: typeof import("nuxt-lodash").default extends NuxtModule<infer O> ? Partial<O> : Record<string, any>
    /**
     * Configuration for `@nuxt/devtools`
     * @see https://www.npmjs.com/package/@nuxt/devtools
     */
    ["devtools"]?: typeof import("@nuxt/devtools").default extends NuxtModule<infer O> ? Partial<O> : Record<string, any>
    /**
     * Configuration for `@nuxt/telemetry`
     * @see https://www.npmjs.com/package/@nuxt/telemetry
     */
    ["telemetry"]?: typeof import("@nuxt/telemetry").default extends NuxtModule<infer O> ? Partial<O> : Record<string, any>
    modules?: (undefined | null | false | NuxtModule<any> | string | [NuxtModule | string, Record<string, any>] | ["@pinia/nuxt", Exclude<NuxtConfig["pinia"], boolean>] | ["@nuxt/eslint", Exclude<NuxtConfig["eslint"], boolean>] | ["vuetify-nuxt-module", Exclude<NuxtConfig["vuetify"], boolean>] | ["nuxt-lodash", Exclude<NuxtConfig["lodash"], boolean>] | ["@nuxt/devtools", Exclude<NuxtConfig["devtools"], boolean>] | ["@nuxt/telemetry", Exclude<NuxtConfig["telemetry"], boolean>])[],
  }
  interface RuntimeConfig {
   app: {
      buildId: string,

      baseURL: string,

      buildAssetsDir: string,

      cdnURL: string,
   },

   nitro: {
      envPrefix: string,
   },
  }
  interface PublicRuntimeConfig {
   VUE_APP_PATH: string,

   BASE_URL: string,

   VUE_APP_AUTH_API_URL: string,

   VUE_APP_AUTH_API_VERSION: string,

   VUE_APP_PAY_API_URL: string,

   VUE_APP_PAY_API_VERSION: string,

   VUE_APP_PPR_API_URL: string,

   VUE_APP_PPR_API_VERSION: string,

   VUE_APP_PPR_API_KEY: string,

   VUE_APP_MHR_API_URL: string,

   VUE_APP_MHR_API_VERSION: string,

   VUE_APP_DOC_API_URL: string,

   VUE_APP_DOC_API_VERSION: string,

   VUE_APP_DOC_API_KEY: string,

   VUE_APP_LTSA_API_URL: string,

   VUE_APP_LTSA_API_VERSION: string,

   VUE_APP_REGISTRIES_SEARCH_API_URL: string,

   VUE_APP_REGISTRIES_SEARCH_API_VERSION: string,

   VUE_APP_REGISTRIES_SEARCH_API_KEY: string,

   VUE_APP_REGISTRY_URL: string,

   VUE_APP_DOCUMENTS_UI_URL: string,

   VUE_APP_VON_API_URL: string,

   VUE_APP_VON_API_VERSION: string,

   VUE_APP_STATUS_API_URL: string,

   VUE_APP_STATUS_API_VERSION: string,

   VUE_APP_AUTH_WEB_URL: string,

   VUE_APP_PPR_LD_CLIENT_ID: string,

   VUE_APP_PPR_STAFF_PARTY_CODE: string,

   VUE_APP_BCOL_STAFF_PARTY_CODE: string,

   VUE_APP_SENTRY_DSN: string,

   VUE_APP_KEYCLOAK_AUTH_URL: string,

   VUE_APP_KEYCLOAK_REALM: string,

   VUE_APP_KEYCLOAK_CLIENTID: string,

   VUE_APP_POD_NAMESPACE: string,

   VUE_APP_ADDRESS_COMPLETE_KEY: string,

   VUE_APP_SITEMINDER_LOGOUT_URL: string,

   keycloakAuthUrl: string,

   keycloakRealm: string,

   keycloakClientId: string,

   appNameDisplay: string,
  }
}
declare module 'vue' {
        interface ComponentCustomProperties {
          $config: RuntimeConfig
        }
      }