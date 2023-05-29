// Libraries
import { createPinia, PiniaVuePlugin } from 'pinia'
import Vue from 'vue'
import Vuex from 'vuex'

// Store modules
import * as State from './state'

/**
 * Configures and returns Vuex Store.
 */
export function getVuexStore () {
  Vue.use(Vuex)

  return new Vuex.Store<any>({
    state: { ...State }
  })
}

/**
 * Configures and returns Pinia Store.
 */
export function getPiniaStore () {
  Vue.use(PiniaVuePlugin)

  return createPinia()
}
