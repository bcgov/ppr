import Axios from 'axios'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import * as Sentry from '@sentry/browser'

const axios = Axios.create()

axios.interceptors.request.use(
  config => {
    config.headers.common.Authorization = `Bearer ${sessionStorage.getItem(SessionStorageKeys.KeyCloakToken)}`
    const currentAccount = sessionStorage.getItem(SessionStorageKeys.CurrentAccount)
    if (currentAccount) {
      const accountInfo = JSON.parse(currentAccount)
      config.headers.common['Account-Id'] = accountInfo.id
    }
    return config
  },
  error => Promise.reject(error)
)

axios.interceptors.response.use(
  response => response,
  error => {
    Sentry.captureException(error)
    return Promise.reject(error)
  }
)

export { axios }
