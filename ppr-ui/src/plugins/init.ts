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

  // Local development only
  if (useRuntimeConfig().public.VUE_APP_LOCAL_DEV === 'true') {
    console.log('Local development detected.')
    // Set all feature flags to true
    setAllFlagDefaults(true)
  }

  // initialize Launch Darkly
  if ((window as any).ldClientId) {
    console.info('Initializing Launch Darkly...')  
    await initLdClient()
  }
  
  nuxtApp.vueApp.use(Vuelidate)
  nuxtApp.vueApp.use(tabFocus)
  nuxtApp.vueApp.directive('maska', vMaska)
})