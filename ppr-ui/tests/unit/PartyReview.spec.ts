import { shallowMount } from '@vue/test-utils'
import { PartyReview } from '@/components/common'

describe('PartyReview', () => {
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

  it('renders the component', () => {
    const wrapper = shallowMount((PartyReview as any), {
      propsData: {
        baseParty: initializedParty
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the header slot content', () => {
    const headerSlotContent = '<div class="review-header">Custom Header Slot</div>'
    const wrapper = shallowMount((PartyReview as any), {
      propsData: {
        baseParty: initializedParty
      },
      slots: {
        headerSlot: headerSlotContent
      }
    })

    const headerSlot = wrapper.find('.review-header')
    expect(headerSlot.exists()).toBe(true)
    expect(headerSlot.html()).toContain(headerSlotContent)
  })

  it('renders party information when data is available', () => {
    const wrapper = shallowMount((PartyReview as any), {
      propsData: {
        baseParty: partyData
      }
    })

    const partyInfo = wrapper.find('.party-info')
    expect(partyInfo.exists()).toBe(true)
    // Add more assertions to check if party information is rendered correctly.
  })

  it('does not render party information when no data is available', () => {
    const wrapper = shallowMount((PartyReview as any), {
      propsData: {
        baseParty: initializedParty
      }
    })

    const partyInfo = wrapper.find('.party-info')
    expect(partyInfo.exists()).toBe(false)
  })
})
