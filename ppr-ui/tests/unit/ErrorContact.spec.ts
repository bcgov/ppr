// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { ErrorContact } from '@/components/common'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')

  return mount(ErrorContact, {
    localVue,
    vuetify
  })
}

describe('Error Contact component', () => {
  it('Displays expected content', () => {
    const wrapper = createComponent()

    // verify content
    expect(wrapper.findComponent(ErrorContact).exists()).toBe(true)
    expect(wrapper.find('.contact-container').exists()).toBe(true)
    const contactItems = wrapper.findAll('.contact-item')
    expect(contactItems.length).toBe(3)
    expect(contactItems.at(0).find('.contact-key').text()).toContain('Canada')
    expect(contactItems.at(0).find('.contact-value').text()).toBe('1-877-526-1526')
    expect(contactItems.at(1).find('.contact-key').text()).toContain('Victoria')
    expect(contactItems.at(1).find('.contact-value').text()).toBe('250-952-0568')
    expect(contactItems.at(2).find('.contact-key').text()).toContain('Email')
    expect(contactItems.at(2).find('.contact-value').text()).toBe('BCRegistries@gov.bc.ca')

    wrapper.destroy()
  })
})
