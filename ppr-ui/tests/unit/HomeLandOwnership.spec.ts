// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi, { nextTick } from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { HomeLandOwnership } from '@/components/mhrRegistration'
import flushPromises from 'flush-promises'
import { getTestId } from './utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(HomeLandOwnership, {
    localVue,
    propsData: {},
    store,
    vuetify
  })
}

describe('Home Land Ownership', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent()
    await nextTick()
    await flushPromises()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders base component', async () => {
    expect(wrapper.findComponent(HomeLandOwnership).exists()).toBe(true)
  })

  it('ownership checkbox performs as expected', async () => {
    expect(store.getters.getMhrRegistrationOwnLand).toBe(false)
    expect(wrapper.find(getTestId('ownership-checkbox'))).toBeTruthy()
    wrapper.find(getTestId('ownership-checkbox')).setChecked()
    await nextTick()
    expect(store.getters.getMhrRegistrationOwnLand).toBe(true)
  })
})
