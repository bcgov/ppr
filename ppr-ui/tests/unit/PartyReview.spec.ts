import { mount } from '@vue/test-utils'
import { PartyReview } from '@/components/common'
import { createComponent } from './utils'
import { nextTick } from 'vue'
import { beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '@/store/store'

describe('PartyReview', () => {
  let wrapper, store, pinia

  const initializedParty = {
    businessName: '',
    address: {
      // ... address data
    },
    emailAddress: '',
    phoneNumber: ''
  }
  const partyData = {
    businessName: 'Sample Business',
    address: {
      // ... address data
    },
    emailAddress: 'sample@example.com',
    phoneNumber: '123-456-7890'
  }

  beforeEach(async () => {
    pinia = createPinia()
    setActivePinia(pinia)
    store = useStore()

    wrapper = await createComponent(PartyReview, { baseParty: initializedParty }, null, null, [pinia])
    await nextTick()
  })

  it('renders the component', async () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the default header slot content', async () => {
    const headerSlot = wrapper.find('.review-header')
    expect(headerSlot.exists()).toBe(true)
    expect(wrapper.text()).toContain('Submitting Party')
  })

  it.skip('renders the custom header slot content', async () => {
    const headerSlotContent = '<div class="review-header">Custom Header Slot</div>'
    // For ease of testing the custom slots, we use mount instead of our custom createComponent function.
    wrapper = mount(PartyReview,
      {
        props: { baseParty: initializedParty },
        slots: {
          headerSlot: headerSlotContent
        }
    })
    await nextTick()

    const headerSlot = wrapper.find('.review-header')
    expect(headerSlot.exists()).toBe(true)
    expect(wrapper.text()).toContain('Custom Header Slot')
  })

  it('renders party information when data is available', async () => {
    wrapper = await createComponent(PartyReview, { baseParty: partyData })

    const partyInfo = wrapper.find('.party-info')
    expect(partyInfo.exists()).toBe(true)
  })

  it('does not render party information when no data is available', async () => {
    const partyInfo = wrapper.find('.party-info')
    expect(partyInfo.exists()).toBe(false)
  })
})
