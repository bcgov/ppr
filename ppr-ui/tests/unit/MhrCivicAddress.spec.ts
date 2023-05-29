import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import { HomeCivicAddress } from '@/components/mhrRegistration/HomeLocation'

Vue.use(Vuetify)
setActivePinia(createPinia())
const store = useStore()
const vuetify = new Vuetify({})

/**
 * Creates and mounts a component, so that it can be tested.
 * @returns a Wrapper object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()

  return mount((HomeCivicAddress as any), {
    localVue,
    store,
    vuetify
  })
}

// Error message class selector
const ERROR_MSG = '.error--text .v-messages__message'

describe('mhr home civic address', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component', async () => {
    const civicAddressSection = wrapper.findComponent(HomeCivicAddress)
    expect(civicAddressSection.exists()).toBe(true)

    civicAddressSection.find('#street').exists()
    civicAddressSection.find('#streetAdditional').exists()
    civicAddressSection.find('#city').exists()
    civicAddressSection.find('#region').exists()
  })

  it('has the right validations for an address', async () => {
    const civicAddressSection = wrapper.findComponent(HomeCivicAddress)
    expect(civicAddressSection.exists()).toBe(true)

    const street = civicAddressSection.find('.street-address')
    expect(civicAddressSection.exists()).toBe(true)

    expect(civicAddressSection.findAll(ERROR_MSG).length).toBe(0)
    await nextTick()
    expect(civicAddressSection.findAll(ERROR_MSG).length).toBe(0)

    const city = civicAddressSection.find('#city')
    city.setValue('Vancouver')
    await nextTick()
    await nextTick()
    expect(civicAddressSection.findAll(ERROR_MSG).length).toBe(0)

    const region = civicAddressSection.find('#region')
    city.setValue('British Columbia')
    await nextTick()
    await nextTick()
    expect(civicAddressSection.findAll(ERROR_MSG).length).toBe(0)
  })
})
