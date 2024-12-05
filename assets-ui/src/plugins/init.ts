import { defineNuxtPlugin } from '#app'
import Vuelidate from 'vuelidate'
import tabFocus from './tabFocus'
import { vMaska } from 'maska'
import { initLdClient, setAllFlagDefaults } from '@/utils'

export default defineNuxtPlugin(async (nuxtApp) => {
  // initialize Launch Darkly
  if ((window as any).ldClientId) {
    console.info('Initializing Launch Darkly...')
    await initLdClient()
  }

  // if (getFeatureFlag('sentry-enable')) {
  //   // initialize Sentry
  //   console.info('Initializing Sentry...')
  //   Sentry.init({
  //     app,
  //     dsn: (window as any).sentryDsn
  //   })
  // }

  // Local development only
  console.log('Pre init')
  if (useRuntimeConfig().public.VUE_APP_LOCAL_DEV === 'true') {
    console.log('Inside local dev init')
    // Set all feature flags to true
    setAllFlagDefaults(true)
  }
  
  nuxtApp.vueApp.use(Vuelidate)
  nuxtApp.vueApp.use(tabFocus)
  nuxtApp.vueApp.directive('maska', vMaska)
})