import Axios from 'axios'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import * as Sentry from '@sentry/browser'

const axios = Axios.create()

// Set the request headers for all PPR API requests: Authorization, x-apikey, Account-Id
axios.interceptors.request.use(
  config => {
    config.headers.common.Authorization = `Bearer ${sessionStorage.getItem(SessionStorageKeys.KeyCloakToken)}`
    config.headers.common['x-apikey'] = sessionStorage.getItem('PPR_API_KEY')
    const currentAccount = sessionStorage.getItem(SessionStorageKeys.CurrentAccount)
    if (currentAccount) {
      const accountInfo = JSON.parse(currentAccount)
      config.headers.common['Account-Id'] = accountInfo.id
    }
    return config
  },
  error => {
    // console.log('axios interceptor set request headers error: ' + error)
    Promise.reject(error)
  }
)

axios.interceptors.response.use(
  response => response,
  error => {
    Sentry.captureException(error)
    return Promise.reject(error)
  }
)

export { axios }
