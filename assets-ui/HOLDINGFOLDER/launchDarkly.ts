import { initLdClient } from '../src/utils'

export default defineNuxtPlugin(async (nuxtApp) => {
  if ((window as any).ldClientId) {
    console.info('Initializing Launch Darkly...')
    await initLdClient()
  }
})