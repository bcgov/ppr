import { defineNuxtPlugin } from '#app'
import * as Vuelidate from 'vuelidate'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(Vuelidate)
})