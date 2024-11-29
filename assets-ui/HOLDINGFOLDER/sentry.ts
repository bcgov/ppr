import { defineNuxtPlugin } from '#app'
import * as Sentry from '@sentry/vue'
import { getFeatureFlag } from '../src/utils'

export default defineNuxtPlugin((nuxtApp) => {
  if (getFeatureFlag('sentry-enable')) {
    Sentry.init({
      app: nuxtApp.vueApp,
      dsn: (window as any).sentryDsn
    })
  }
})