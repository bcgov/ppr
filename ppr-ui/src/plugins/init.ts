import { defineNuxtPlugin } from '#app'
import { useVuelidate } from '@vuelidate/core'
import tabFocus from './tabFocus'
import { vMaska } from 'maska'
import { fetchConfig, initLdClient } from '@/utils'

export default defineNuxtPlugin(async (nuxtApp) => {
  // Set Configurations
  await fetchConfig()

  // initialize Launch Darkly
  if (useRuntimeConfig().public.VUE_APP_PPR_LD_CLIENT_ID) {
    console.info('Initializing Launch Darkly...')
    await initLdClient(useRuntimeConfig().public.VUE_APP_PPR_LD_CLIENT_ID)
  }

  // nuxtApp.vueApp.use(Vuelidate)
  nuxtApp.vueApp.use(tabFocus)
  nuxtApp.vueApp.directive('maska', vMaska)
})
