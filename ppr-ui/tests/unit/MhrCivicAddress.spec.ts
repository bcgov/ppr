import { nextTick } from 'vue'
import { HomeCivicAddress } from '@/components/mhrRegistration/HomeLocation'
import { createComponent } from './utils'
import { CivicAddressSchema } from '@/schemas/civic-address'
import { MhrCorrectionStaff } from '@/resources'
import { mockedMhrRegistration } from './test-data'
import { useStore } from '@/store/store'
import { useNewMhrRegistration } from '@/composables'
import { CautionBox, UpdatedBadge } from '@/components/common'
import { beforeEach } from 'vitest'

const store = useStore()

// Error message class selector
const ERROR_MSG = '.error--text .v-messages__message'

describe('HomeCivic Address', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(HomeCivicAddress, { schema: CivicAddressSchema })
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

describe('HomeCivic Address Corrections', () => {
  let wrapper
  const { initDraftOrCurrentMhr } = useNewMhrRegistration()

  beforeEach( async () => {
    await store.setRegistrationType(MhrCorrectionStaff)
    await store.setMhrBaseline(mockedMhrRegistration)
    await initDraftOrCurrentMhr(mockedMhrRegistration)
  })

  it('does NOT render the correction badge by default', async () => {
    wrapper = await createComponent(HomeCivicAddress,
      {
        value: { ...mockedMhrRegistration.location.address },
        schema: CivicAddressSchema,
        updatedBadge: {
          baseline: { ...mockedMhrRegistration.location.address },
          currentState: { ...mockedMhrRegistration.location.address }
        }
      })
    await wrapper.vm.$router.push({ path: '/mhr-registration/home-location' })
    await nextTick()

    expect(wrapper.findComponent(UpdatedBadge).isVisible()).toBe(false)
    const civicAddressSection = wrapper.findComponent(HomeCivicAddress)
    expect(civicAddressSection.exists()).toBe(true)

    civicAddressSection.find('#street').exists()
    civicAddressSection.find('#streetAdditional').exists()
    civicAddressSection.find('#city').exists()
    civicAddressSection.find('#region').exists()
  })

  it('renders the correction badge when changes', async () => {
    wrapper = await createComponent(HomeCivicAddress,
      {
        value: { ...mockedMhrRegistration.location.address },
        schema: CivicAddressSchema,
        updatedBadge: {
          baseline: { ...mockedMhrRegistration.location.address },
          currentState: { ...mockedMhrRegistration.location.address, street: '123' }
        }
      })
    await wrapper.vm.$router.push({ path: '/mhr-registration/home-location' })
    await nextTick()

    expect(wrapper.findComponent(UpdatedBadge).isVisible()).toBe(true)
    expect(wrapper.findComponent(CautionBox).exists()).toBe(false)
  })

  it('renders the region change caution message when moving into BC', async () => {
    wrapper = await createComponent(HomeCivicAddress,
      {
        value: { ...mockedMhrRegistration.location.address },
        schema: CivicAddressSchema,
        updatedBadge: {
          baseline: { ...mockedMhrRegistration.location.address },
          currentState: { ...mockedMhrRegistration.location.address, region: 'BC' }
        }
      })
    await wrapper.vm.$router.push({ path: '/mhr-registration/home-location' })
    await nextTick()

    expect(wrapper.findComponent(UpdatedBadge).isVisible()).toBe(true)
    expect(wrapper.findComponent(CautionBox).exists()).toBe(true)
  })
})
