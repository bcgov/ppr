import { defineNuxtPlugin } from '#app'
import { vMaska } from 'maska'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.directive('maska', vMaska)
})