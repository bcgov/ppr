import { nextTick } from 'vue'

import { HomeCivicAddress } from '@/components/mhrRegistration/HomeLocation'
import { createComponent } from './utils'

// Error message class selector
const ERROR_MSG = '.error--text .v-messages__message'

describe('mhr home civic address', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(HomeCivicAddress)
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

    expect(civicAddressSection.findAll(ERROR_MSG).length).toBe(0)
    await nextTick()
    expect(civicAddressSection.findAll(ERROR_MSG).length).toBe(0)

    const country = civicAddressSection.find('#country')
    country.setValue('Canada')
    await nextTick()
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
