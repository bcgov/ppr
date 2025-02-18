import { defineNuxtPlugin } from '#app'
import Vuelidate from 'vuelidate'
import tabFocus from './tabFocus'
import { vMaska } from 'maska'
import { initLdClient, setAllFlagDefaults } from '@/utils'

export default defineNuxtPlugin(async (nuxtApp) => {
  // initialize Launch Darkly
  if (useRuntimeConfig().public.VUE_APP_PPR_LD_CLIENT_ID) {
    console.info('Initializing Launch Darkly...')
    await initLdClient(useRuntimeConfig().public.VUE_APP_PPR_LD_CLIENT_ID)
  }

  // Local development only
  if (useRuntimeConfig().public.VUE_APP_LOCAL_DEV === 'true') {
    // Set all feature flags to true
    setAllFlagDefaults(true)
  }
  
  nuxtApp.vueApp.use(Vuelidate)
  nuxtApp.vueApp.use(tabFocus)
  nuxtApp.vueApp.directive('maska', vMaska)
})
