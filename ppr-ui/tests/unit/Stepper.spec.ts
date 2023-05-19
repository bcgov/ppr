// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'

import { shallowMount } from '@vue/test-utils'

// Components
import { Stepper } from '@/components/common'

// Other
import {
  mockedSelectSecurityAgreement
} from './test-data'

Vue.use(Vuetify)
Vue.use(VueRouter)
const router = new VueRouter()

const vuetify = new Vuetify({})
const store = getVuexStore()

describe('Stepper component', () => {
  let wrapper: any

  beforeEach(async () => {
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement)
    wrapper = shallowMount((Stepper as any), { store, vuetify, router })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component properly', () => {
    // FUTURE
  })
})
