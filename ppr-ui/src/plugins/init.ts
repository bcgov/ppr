import { defineNuxtPlugin } from '#app'
import { vMaska } from 'maska'
import { fetchConfig } from '@/utils/config-helper'
import { initLdClient } from '@/utils/feature-flags'

export default defineNuxtPlugin(async (nuxtApp) => {
  if (typeof window === 'undefined' || typeof sessionStorage === 'undefined') {
    return
  }

  // Set Configurations
  await fetchConfig()

  // initialize Launch Darkly
  if (useRuntimeConfig().public.VUE_APP_PPR_LD_CLIENT_ID) {
    console.info('Initializing Launch Darkly...')
    await initLdClient(useRuntimeConfig().public.VUE_APP_PPR_LD_CLIENT_ID)
  }

  nuxtApp.vueApp.directive('maska', vMaska)
})
