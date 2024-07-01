import { describe, it, expect, beforeEach } from 'vitest'
import { TabbedContainer } from '@/components/common'
import { createComponent } from './utils'

const tabConfigMock = [
  { label: 'Tab 1', icon: 'mdi-home' },
  { label: 'Tab 2', icon: 'mdi-settings' },
]

describe('YourComponent.vue', () => {
  let wrapper
  beforeEach(async () => {
    wrapper = await createComponent(TabbedContainer, {
      tabConfig: tabConfigMock
    })
  })
  it('renders correctly', async () => {
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('#tabbed-container').exists()).toBe(true)
    expect(wrapper.findAll('.tab').length).toBe(tabConfigMock.length)
  })

  it('switches tabs correctly', async () => {
    const tabs = wrapper.findAll('.tab')
    expect(tabs.length).toBe(tabConfigMock.length)

    await tabs[1].trigger('click')
    expect(wrapper.vm.tab).toBe(1)

    await tabs[0].trigger('click')
    expect(wrapper.vm.tab).toBe(0)
  })
})
