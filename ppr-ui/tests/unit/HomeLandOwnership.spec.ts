// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { HomeLandOwnership } from '@/components/mhrRegistration'
import flushPromises from 'flush-promises'
import { getTestId } from './utils'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()
/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)

  document.body.setAttribute('data-app', 'true')
  return mount((HomeLandOwnership as any), {
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
    expect(store.getMhrRegistrationOwnLand).toBe(false)
    expect(wrapper.find(getTestId('ownership-checkbox'))).toBeTruthy()
    wrapper.find(getTestId('ownership-checkbox')).setChecked()
    await nextTick()
    expect(store.getMhrRegistrationOwnLand).toBe(true)
  })
})
