import Axios from 'axios'
import * as Sentry from '@sentry/browser'

const axios = Axios.create()

axios.interceptors.request.use(
  config => {
    config.headers['x-apikey'] = sessionStorage.getItem('PPR_API_KEY')
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
