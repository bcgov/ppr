import Axios from 'axios'
import * as Sentry from '@sentry/browser'

const axios = Axios.create()

axios.interceptors.response.use(
  response => response,
  error => {
    Sentry.captureException(error)
    return Promise.reject(error)
  }
)

export { axios }
