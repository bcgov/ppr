// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'

// Components
import { SimpleHelpToggle } from '@/components/common'

// Utilities
import { getTestId } from './utils'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<Any> object with the given parameters.
 */
function createComponent (propsData: any): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)

  return mount((SimpleHelpToggle as any), {
    localVue,
    propsData,
    vuetify
  })
}

describe('SimpleHelpToggle', () => {
  it('renders the component properly', () => {
    const wrapper: Wrapper<any> = createComponent({ toggleButtonTitle: 'test' })
    expect(wrapper.findComponent(SimpleHelpToggle).exists()).toBe(true)
    const toggleButton = wrapper.find(getTestId('help-toggle-btn'))
    expect(toggleButton.text()).toBe('test')
    expect(toggleButton.text().includes('Hide')).toBe(false)
  })

  it('has the proper hide text - none default hide text', async () => {
    const wrapper: Wrapper<any> = createComponent({ toggleButtonTitle: 'test' })
    const toggleButton = wrapper.find(getTestId('help-toggle-btn'))
    await toggleButton.trigger('click')
    expect(toggleButton.text()).not.toBe('test')
    expect(toggleButton.text()).toBe('Hide test')
  })

  it('has the proper hide text - default hide text', async () => {
    const wrapper: Wrapper<any> = createComponent({ toggleButtonTitle: 'test', defaultHideText: true })
    const toggleButton = wrapper.find(getTestId('help-toggle-btn'))
    await toggleButton.trigger('click')
    expect(toggleButton.text()).toBe('Hide Help')
  })
})
