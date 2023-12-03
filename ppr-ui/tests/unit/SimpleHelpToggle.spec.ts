// Libraries
import { SimpleHelpToggle } from '@/components/common'
import { createComponent, getTestId } from './utils'

describe('SimpleHelpToggle', () => {
  it('renders the component properly', async () => {
    const wrapper = await createComponent(SimpleHelpToggle, { toggleButtonTitle: 'test' })
    expect(wrapper.findComponent(SimpleHelpToggle).exists()).toBe(true)
    const toggleButton = wrapper.find(getTestId('help-toggle-btn'))
    expect(toggleButton.text()).toBe('test')
    expect(toggleButton.text().includes('Hide')).toBe(false)
  })

  it('has the proper hide text - default hide text', async () => {
    const wrapper = await createComponent(SimpleHelpToggle)
    const toggleButton = wrapper.find(getTestId('help-toggle-btn'))
    await toggleButton.trigger('click')
    expect(toggleButton.text()).not.toBe('test')
    expect(toggleButton.text()).toBe('Hide Help')
  })

  it('has the proper hide text - none default hide text', async () => {
    const wrapper = await createComponent(SimpleHelpToggle, { toggleButtonTitle: 'test', defaultHideText: false })
    const toggleButton = wrapper.find(getTestId('help-toggle-btn'))
    await toggleButton.trigger('click')
    expect(toggleButton.text()).not.toBe('test')
    expect(toggleButton.text()).toBe('Hide test')
  })
})
