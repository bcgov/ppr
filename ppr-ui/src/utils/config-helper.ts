/**
 * Fetches config from environment and API.
 * @returns A promise to get & set session storage keys with appropriate values.
 */
export async function fetchConfig (): Promise<any> {
  // get config from environment
  const origin: string = window.location.origin
  const processEnvVueAppPath: string = process.env.VUE_APP_PATH
  const processEnvBaseUrl = process.env.BASE_URL
  const windowLocationPathname = window.location.pathname // eg, /basePath/...
  const windowLocationOrigin = window.location.origin // eg, http://localhost:8080
  const windowLocationSearch = window.location.search

  if (!origin || !processEnvVueAppPath || !processEnvBaseUrl || !windowLocationPathname || !windowLocationOrigin) {
    return Promise.reject(new Error('Missing environment variables'))
  }

  const authApiUrl: string = process.env.VUE_APP_AUTH_API_URL + process.env.VUE_APP_AUTH_API_VERSION + '/'
  sessionStorage.setItem('AUTH_API_URL', authApiUrl)

  const payApiUrl: string = process.env.VUE_APP_PAY_API_URL + process.env.VUE_APP_PAY_API_VERSION + '/'
  sessionStorage.setItem('PAY_API_URL', payApiUrl)

  const pprApiUrl: string = process.env.VUE_APP_PPR_API_URL + process.env.VUE_APP_PPR_API_VERSION + '/'
  const pprApiKey: string = process.env.VUE_APP_PPR_API_KEY
  sessionStorage.setItem('PPR_API_URL', pprApiUrl)
  sessionStorage.setItem('PPR_API_KEY', pprApiKey)

  const mhrApiUrl: string = process.env.VUE_APP_MHR_API_URL + process.env.VUE_APP_MHR_API_VERSION + '/'
  const mhrApiKey: string = process.env.VUE_APP_PPR_API_KEY
  sessionStorage.setItem('MHR_API_URL', mhrApiUrl)
  sessionStorage.setItem('MHR_API_KEY', mhrApiKey)

  const ltsaApiUrl: string = process.env.VUE_APP_LTSA_API_URL + process.env.VUE_APP_LTSA_API_VERSION + '/'
  const ltsaApiKey: string = process.env.VUE_APP_PPR_API_KEY
  sessionStorage.setItem('LTSA_API_URL', ltsaApiUrl)
  sessionStorage.setItem('LTSA_API_KEY', ltsaApiKey)

  const searchApiUrl: string = process.env.VUE_APP_REGISTRIES_SEARCH_API_URL +
    process.env.VUE_APP_REGISTRIES_SEARCH_API_VERSION + '/'
  const searchApiKey: string = process.env.VUE_APP_REGISTRIES_SEARCH_API_KEY
  sessionStorage.setItem('REGISTRIES_SEARCH_API_URL', searchApiUrl)
  sessionStorage.setItem('REGISTRIES_SEARCH_API_KEY', searchApiKey)

  const registryUrl: string = process.env.VUE_APP_REGISTRY_URL
  sessionStorage.setItem('REGISTRY_URL', registryUrl)

  const vonApiUrl: string = process.env.VUE_APP_VON_API_URL + process.env.VUE_APP_VON_API_VERSION
  sessionStorage.setItem('VON_API_URL', vonApiUrl)

  // for system alert banner (sbc-common-components)
  const statusApiUrl: string = process.env.VUE_APP_STATUS_API_URL + process.env.VUE_APP_STATUS_API_VERSION
  sessionStorage.setItem('STATUS_API_URL', statusApiUrl)

  // for sbc header (sbc-common-components)
  const authWebUrl: string = process.env.VUE_APP_AUTH_WEB_URL
  sessionStorage.setItem('AUTH_WEB_URL', authWebUrl)

  // get and store account id, if present
  const accountId = new URLSearchParams(windowLocationSearch).get('accountid')
  if (accountId) {
    sessionStorage.setItem('ACCOUNT_ID', accountId)
  }

  const ldClientId: string = process.env.VUE_APP_PPR_LD_CLIENT_ID
  if (ldClientId) {
    (<any>window).ldClientId = ldClientId
  }

  const pprStaffPartyCode: string = process.env.VUE_APP_PPR_STAFF_PARTY_CODE
  if (pprStaffPartyCode) {
    sessionStorage.setItem('PPR_STAFF_PARTY_CODE', pprStaffPartyCode)
  }

  const bcolStaffPartyCode: string = process.env.VUE_APP_BCOL_STAFF_PARTY_CODE
  if (bcolStaffPartyCode) {
    sessionStorage.setItem('BCOL_STAFF_PARTY_CODE', bcolStaffPartyCode)
  }

  const sentryDsn: string = process.env.VUE_APP_SENTRY_DSN
  if (sentryDsn) {
    (<any>window).sentryDsn = sentryDsn
  }

  const keycloakAuthUrl: string = process.env.VUE_APP_KEYCLOAK_AUTH_URL;
  (<any>window).keycloakAuthUrl = keycloakAuthUrl

  const keycloakRealm: string = process.env.VUE_APP_KEYCLOAK_REALM;
  (<any>window).keycloakRealm = keycloakRealm

  const keycloakClientId: string = process.env.VUE_APP_KEYCLOAK_CLIENTID;
  (<any>window).keycloakClientId = keycloakClientId

  // set Base for Vue Router
  // eg, "/basePath/xxxx/"
  const vueRouterBase = processEnvBaseUrl
  sessionStorage.setItem('VUE_ROUTER_BASE', vueRouterBase)
  console.info('Set Vue Router Base to: ' + vueRouterBase)

  // set Base URL for returning from redirects
  // eg, http://localhost:8080/basePath/xxxx/
  const baseUrl = windowLocationOrigin + vueRouterBase
  sessionStorage.setItem('BASE_URL', baseUrl)
  console.info('Set Base URL to: ' + baseUrl)

  const podNamespace = process.env.VUE_APP_POD_NAMESPACE
  sessionStorage.setItem('POD_NAMESPACE', podNamespace)
  console.log('POD_NAMESPACE: ' + podNamespace)

  const addressCompleteKey: string = process.env.VUE_APP_ADDRESS_COMPLETE_KEY
  if (addressCompleteKey) {
    (<any>window).addressCompleteKey = addressCompleteKey
    console.info('Set Address Complete Key.')
  }

  const siteminderLogoutUrl: string = process.env.VUE_APP_SITEMINDER_LOGOUT_URL
  if (siteminderLogoutUrl) {
    sessionStorage.setItem('SITEMINDER_LOGOUT_URL', siteminderLogoutUrl)
  }
}
