// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import flushPromises from 'flush-promises'
import { getVuexStore } from '@/store'
import { mount, createLocalVue } from '@vue/test-utils'

// Components
import SbcSignout from 'sbc-common-components/src/components/SbcSignout.vue'
import { Signout } from '@/views'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Signout component', () => {
  let wrapper: any
  const baseURL = 'myhost/basePath'
  sessionStorage.setItem('REGISTRY_URL', baseURL)

  beforeEach(async () => {
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    wrapper = mount(Signout, { localVue, store, vuetify })

    // wait for all queries to complete
    await flushPromises()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with signout component', () => {
    expect(wrapper.vm.logoutURL).toBe(`${baseURL}?logout=true`)
    expect(wrapper.findComponent(Signout).exists()).toBe(true)
    expect(wrapper.findComponent(SbcSignout).exists()).toBe(true)
  })
})
