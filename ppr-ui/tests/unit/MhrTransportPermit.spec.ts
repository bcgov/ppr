import { createComponent, setupMockStaffUser } from './utils'
import { MhrTransportPermit } from '@/views'
import { beforeEach, expect } from 'vitest'
import { DocumentId, FormCard, SimpleHelpToggle } from '@/components/common'
import { nextTick } from 'vue'
import flushPromises from 'flush-promises'
import { LocationChange } from '@/components/mhrTransfers'
import { AuthRoles, LocationChangeTypes, ProductCode } from '@/enums'
import { useStore } from '@/store/store'

const store = useStore()

describe('MhrTransportPermit', () => {
  let wrapper

  const activateLocationChange = async () => {
    const changeLocationBtn = await wrapper.find('#home-location-change-btn')
    changeLocationBtn.trigger('click')
    await nextTick()
  }

  beforeEach(async () => {
    await setupMockStaffUser()
    wrapper = await createComponent(MhrTransportPermit)
  })

  afterEach(async () => {
    wrapper.vm.setLocationChange(false)
    await store.setAuthRoles(['staff', 'ppr'])
  })

  it('does not render location change content when isChangeLocationActive is false', async () => {
    expect(wrapper.findComponent(MhrTransportPermit).exists()).toBe(true)
    expect(wrapper.findComponent(SimpleHelpToggle).exists()).toBe(false)
    expect(wrapper.findComponent(DocumentId).exists()).toBe(false)
    expect(wrapper.findComponent(FormCard).exists()).toBe(false)
    expect(wrapper.find('#location-change-type-section').exists()).toBe(false)
    expect(wrapper.findComponent(LocationChange).exists()).toBe(false)
  })

  it('renders location change content when isChangeLocationActive is true', async () => {
    // Open Change Location Flow
    const changeLocationBtn = await wrapper.find('#home-location-change-btn')
    changeLocationBtn.trigger('click')
    await nextTick()

    expect(wrapper.findComponent(MhrTransportPermit).exists()).toBe(true)
    expect(wrapper.findComponent(SimpleHelpToggle).exists()).toBe(true)
    expect(wrapper.findComponent(DocumentId).exists()).toBe(true)
    expect(wrapper.findComponent(FormCard).exists()).toBe(true)
    expect(wrapper.find('#location-change-type-section').exists()).toBe(true)
    expect(wrapper.findComponent(LocationChange).exists()).toBe(true)
  })

  it('enables change location by default', async () => {
    expect(wrapper.vm.disable).toBe(false)
    const changeLocationBtn = await wrapper.find('#home-location-change-btn')
    expect(changeLocationBtn.attributes().disabled).toBeUndefined()
  })


  it('disables change location when prop is set', async () => {
    wrapper = await createComponent(MhrTransportPermit, { disable: true })
    await nextTick()
    await flushPromises()

    expect(wrapper.vm.disable).toBe(true)
    const changeLocationBtn = await wrapper.find('#home-location-change-btn')
    expect(changeLocationBtn.attributes().disabled).toBeDefined()
  })

  it('should render two location change options for Qualified Supplier', async () => {
    // setup Qualified Supplier as Manufacturer
    await store.setAuthRoles([AuthRoles.MHR_TRANSFER_SALE])
    await store.setUserProductSubscriptionsCodes([ProductCode.MANUFACTURER])
    await activateLocationChange()
    await nextTick()

    const locationChangeDropdown = wrapper.findComponent(LocationChange).findComponent('.v-select')
    expect(locationChangeDropdown.vm.items.length).toBe(2)
  })

  it('should render different location change options', async () => {
    await activateLocationChange()

    const locationChange = wrapper.findComponent(LocationChange)
    const locationChangeDropdown = locationChange.findComponent('.v-select')

    expect(locationChangeDropdown.exists()).toBe(true)
    expect(locationChangeDropdown.vm.items.length).toBe(3)

    // select transport permit
    locationChange.vm.state.locationChangeType = LocationChangeTypes.TRANSPORT_PERMIT
    await nextTick()
    expect(locationChange.find('#transport-permit-location-type').exists()).toBe(true)

    // select transport permit within same park
    locationChange.vm.state.locationChangeType = LocationChangeTypes.TRANSPORT_PERMIT_SAME_PARK
    await nextTick()
    expect(locationChange.find('#transport-permit-location-type').exists()).toBe(false)
  })
})
