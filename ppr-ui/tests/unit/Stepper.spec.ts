// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

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
setActivePinia(createPinia())
const store = useStore()

describe('Stepper component', () => {
  let wrapper: any

  beforeEach(async () => {
    await store.setRegistrationType(mockedSelectSecurityAgreement)
    wrapper = shallowMount((Stepper as any), { store, vuetify, router })
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component properly', () => {
    // FUTURE
  })
})
