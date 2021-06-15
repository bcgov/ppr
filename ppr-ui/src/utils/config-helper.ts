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

  /**
   * authConfig is a workaround to fix the user settings call as it expects a URL with no trailing slash.
   * This will be removed when a fix is made to sbc-common-components to handle this
   */
  const authConfig = {
    VUE_APP_AUTH_ROOT_API: response.data.SBC_CONFIG_AUTH_API_URL
  }
  const authConfigString = JSON.stringify(authConfig)
  sessionStorage.setItem('AUTH_API_CONFIG', authConfigString)
  console.log('AUTH_API_CONFIG: ' + authConfigString)

  const authApiUrl: string = response.data.AUTH_API_URL
  sessionStorage.setItem('AUTH_API_URL', authApiUrl)
  console.log('Set Auth API URL to: ' + authApiUrl)

  const payApiUrl: string = response.data.PAY_API_URL
  sessionStorage.setItem('PAY_API_URL', payApiUrl)
  console.log('Set Pay API URL to: ' + payApiUrl)

  const pprApiUrl: string = response.data.PPR_API_URL
  const pprApiKey: string = response.data.PPR_API_KEY
  sessionStorage.setItem('PPR_API_URL', pprApiUrl)
  sessionStorage.setItem('PPR_API_KEY', pprApiKey)
  console.log('Set PPR API URL to: ' + pprApiUrl)

  const registryUrl: string = response.data.REGISTRY_URL
  sessionStorage.setItem('REGISTRY_URL', registryUrl)
  console.log('Set REGISTRY URL to: ' + registryUrl)

  const keycloakConfigPath: string = response.data.KEYCLOAK_CONFIG_PATH
  sessionStorage.setItem('KEYCLOAK_CONFIG_PATH', keycloakConfigPath)
  console.info('Set Keycloak Config Path to: ' + keycloakConfigPath)

  const vonApiUrl: string = response.data.VON_API_URL
  sessionStorage.setItem('VON_API_URL', vonApiUrl)
  console.log('Set VON API URL to: ' + vonApiUrl)

  const ldClientId: string = response.data.LD_CLIENT_ID
  if (ldClientId) {
    (<any>window).ldClientId = ldClientId
    console.info('Set Launch Darkly Client ID.')
  }

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
}
