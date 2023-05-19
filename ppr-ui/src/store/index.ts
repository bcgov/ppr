// Libraries
import { createPinia, PiniaVuePlugin } from 'pinia'
import Vue from 'vue'
import Vuex from 'vuex'

// Store modules
import * as State from './state'
import * as Getters from './getters'
import * as Mutations from './mutations'
import * as Actions from './actions'

/**
 * Configures and returns Vuex Store.
 */
export function getVuexStore () {
  Vue.use(Vuex)

  return new Vuex.Store<any>({
    state: { ...State },
    getters: { ...Getters },
    mutations: { ...Mutations },
    actions: { ...Actions }
  })
}

/**
 * Configures and returns Pinia Store.
 */
export function getPiniaStore () {
  Vue.use(PiniaVuePlugin)

  return createPinia()
}
