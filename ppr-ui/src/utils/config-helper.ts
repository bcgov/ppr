/* eslint-disable no-console */

import { axios } from '@/utils'

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

  // fetch config from API
  // eg, http://localhost:8080/basePath/config/configuration.json
  // eg, https://ppr-dev.pathfinder.gov.bc.ca/ppr/config/configuration.json
  const url = `${origin}/${processEnvVueAppPath}/config/configuration.json`
  const headers = {
    Accept: 'application/json',
    ResponseType: 'application/json',
    'Cache-Control': 'no-cache'
  }

  const response = await axios.get(url, { headers }).catch(() => {
    return Promise.reject(new Error('Could not fetch configuration.json'))
  })

  const authApiUrl: string = response.data.AUTH_API_URL + response.data.AUTH_API_VERSION + '/'
  sessionStorage.setItem('AUTH_API_URL', authApiUrl)
  console.log('Set Auth API URL to: ' + authApiUrl)

  const payApiUrl: string = response.data.PAY_API_URL + response.data.PAY_API_VERSION + '/'
  sessionStorage.setItem('PAY_API_URL', payApiUrl)
  console.log('Set Pay API URL to: ' + payApiUrl)

  const pprApiUrl: string = response.data.PPR_API_URL + response.data.PPR_API_VERSION + '/'
  const pprApiKey: string = response.data.PPR_API_KEY
  sessionStorage.setItem('PPR_API_URL', pprApiUrl)
  sessionStorage.setItem('PPR_API_KEY', pprApiKey)
  console.log('Set PPR API URL to: ' + pprApiUrl)

  const mhrApiUrl: string = response.data.MHR_API_URL + response.data.MHR_API_VERSION + '/'
  const mhrApiKey: string = response.data.PPR_API_KEY
  sessionStorage.setItem('MHR_API_URL', mhrApiUrl)
  sessionStorage.setItem('MHR_API_KEY', mhrApiKey)
  console.log('Set MHR API URL to: ' + mhrApiUrl)

  const searchApiUrl: string = response.data.REGISTRIES_SEARCH_API_URL +
    response.data.REGISTRIES_SEARCH_API_VERSION + '/'
  const searchApiKey: string = response.data.REGISTRY_SEARCH_API_KEY
  sessionStorage.setItem('REGISTRIES_SEARCH_API_URL', searchApiUrl)
  sessionStorage.setItem('REGISTRIES_SEARCH_API_KEY', searchApiKey)
  console.log('Set REGISTRIES SEARCH API URL to: ' + searchApiUrl)

  const registryUrl: string = response.data.REGISTRY_URL
  sessionStorage.setItem('REGISTRY_URL', registryUrl)
  console.log('Set REGISTRY URL to: ' + registryUrl)

  const systemMessage: string = response.data.SYSTEM_MESSAGE
  sessionStorage.setItem('SYSTEM_MESSAGE', systemMessage)
  console.log('Set SYSTEM MESSAGE to: ' + systemMessage)

  const systemMessageType: string = response.data.SYSTEM_MESSAGE_TYPE
  sessionStorage.setItem('SYSTEM_MESSAGE_TYPE', systemMessageType)
  console.log('Set SYSTEM MESSAGE TYPE to: ' + systemMessageType)

  const keycloakConfigPath: string = response.data.KEYCLOAK_CONFIG_PATH
  sessionStorage.setItem('KEYCLOAK_CONFIG_PATH', keycloakConfigPath)
  console.info('Set Keycloak Config Path to: ' + keycloakConfigPath)

  const vonApiUrl: string = response.data.VON_API_URL + response.data.VON_API_VERSION
  sessionStorage.setItem('VON_API_URL', vonApiUrl)
  console.log('Set VON API URL to: ' + vonApiUrl)

  // for system alert banner (sbc-common-components)
  const statusApiUrl: string = response.data.STATUS_API_URL + response.data.STATUS_API_VERSION
  sessionStorage.setItem('STATUS_API_URL', statusApiUrl)
  console.log('Set Status API URL to: ' + statusApiUrl)

  // for sbc header (sbc-common-components)
  const authWebUrl: string = response.data.AUTH_WEB_URL
  sessionStorage.setItem('AUTH_WEB_URL', authWebUrl)
  console.log('Set Auth Web URL to: ' + authWebUrl)

  // get and store account id, if present
  const accountId = new URLSearchParams(windowLocationSearch).get('accountid')
  if (accountId) {
    sessionStorage.setItem('ACCOUNT_ID', accountId)
    console.log('Set Account ID to: ' + accountId)
  }

  const ldClientId: string = response.data.PPR_LD_CLIENT_ID
  if (ldClientId) {
    (<any>window).ldClientId = ldClientId
    console.info('Set Launch Darkly Client ID.')
  }

  const pprStaffPartyCode: string = response.data.PPR_STAFF_PARTY_CODE
  if (pprStaffPartyCode) {
    sessionStorage.setItem('PPR_STAFF_PARTY_CODE', pprStaffPartyCode)
  }

  const bcolStaffPartyCode: string = response.data.BCOL_STAFF_PARTY_CODE
  if (bcolStaffPartyCode) {
    sessionStorage.setItem('BCOL_STAFF_PARTY_CODE', bcolStaffPartyCode)
  }

  const sentryEnable = response.data.SENTRY_ENABLE;
  (<any>window).sentryEnable = sentryEnable

  const sentryDsn = response.data.SENTRY_DSN
  if (sentryDsn) {
    (<any>window).sentryDsn = sentryDsn
    console.log('Set Sentry DSN.')
  }

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

  const podNamespace = response.data.POD_NAMESPACE
  sessionStorage.setItem('POD_NAMESPACE', podNamespace)
  console.log('POD_NAMESPACE: ' + podNamespace)

  const addressCompleteKey: string = response.data.ADDRESS_COMPLETE_KEY
  if (addressCompleteKey) {
    (<any>window).addressCompleteKey = addressCompleteKey
    console.info('Set Address Complete Key.')
  }

  const siteminderLogoutUrl: string = response.data.SITEMINDER_LOGOUT_URL
  if (siteminderLogoutUrl) {
    sessionStorage.setItem('SITEMINDER_LOGOUT_URL', siteminderLogoutUrl)
  }
}
