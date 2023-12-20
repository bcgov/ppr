import { createComponent, setupMockStaffUser } from './utils'
import { MhrTransportPermit } from '@/views'
import { beforeEach, expect } from 'vitest'
import { DocumentId, FormCard, SimpleHelpToggle } from '@/components/common'
import { nextTick } from 'vue'
import flushPromises from 'flush-promises'

describe('MhrTransportPermit', () => {
  let wrapper
  beforeEach(async () => {
    await setupMockStaffUser()
    wrapper = await createComponent(MhrTransportPermit)
  })

  it('does not render location change content when isChangeLocationActive is false', async () => {
    expect(wrapper.findComponent(MhrTransportPermit).exists()).toBe(true)
    expect(wrapper.findComponent(SimpleHelpToggle).exists()).toBe(false)
    expect(wrapper.findComponent(DocumentId).exists()).toBe(false)
    expect(wrapper.findComponent(FormCard).exists()).toBe(false)
    expect(wrapper.find('#location-change-type-section').exists()).toBe(false)
  })

  it('renders location change content when isChangeLocationActive is true', async () => {
    // Open Change Location Flow
    const changeLocationBtn= await wrapper.find('#home-location-change-btn')
    changeLocationBtn.trigger('click')
    await nextTick()

    expect(wrapper.findComponent(MhrTransportPermit).exists()).toBe(true)
    expect(wrapper.findComponent(SimpleHelpToggle).exists()).toBe(true)
    expect(wrapper.findComponent(DocumentId).exists()).toBe(true)
    expect(wrapper.findComponent(FormCard).exists()).toBe(true)
    expect(wrapper.find('#location-change-type-section').exists()).toBe(true)
  })

  it('enables change location by default', async () => {
    expect(wrapper.vm.disable).toBe(false)
    const changeLocationBtn= await wrapper.find('#home-location-change-btn')
    expect(changeLocationBtn.attributes().disabled).toBeUndefined()
  })

  it('disables change location when prop is set', async () => {
    wrapper = await createComponent(MhrTransportPermit, { disable: true })
    await nextTick()
    await flushPromises()

    expect(wrapper.vm.disable).toBe(true)
    const changeLocationBtn= await wrapper.find('#home-location-change-btn')
    expect(changeLocationBtn.attributes().disabled).toBeDefined()
  })
})
