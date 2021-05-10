// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { RegistrationBar } from '@/components/registration'
import { RegistrationTypeIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { mockedSelectSecurityAgreement } from './test-data'
import { RegistrationTypes } from '@/resources'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events

// Input field selectors / buttons
const registrationButton: string = '.registration-bar-btn'

/**
 * Returns the last event for a given name, to be used for testing event propagation in response to component changes.
 *
 * @param wrapper the wrapper for the component that is being tested.
 * @param name the name of the event that is to be returned.
 *
 * @returns the value of the last named event for the wrapper.
 */
function getLastEvent (wrapper: Wrapper<any>, name: string): any {
  const eventsList: Array<any> = wrapper.emitted(name)
  if (!eventsList) {
    return null
  }
  const events: Array<any> = eventsList[eventsList.length - 1]
  return events[0]
}

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (
  defaultSelectedRegistrationType: RegistrationTypeIF,
  registrationTitle: string
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(RegistrationBar, {
    localVue,
    propsData: { defaultSelectedRegistrationType, registrationTitle },
    store,
    vuetify
  })
}

describe('RegistrationBar select tests', () => {
  let wrapper: Wrapper<any>
  const registrationTitle: string = 'My Registrations'
  const selectedRegistrationType: RegistrationTypeIF = mockedSelectSecurityAgreement

  beforeEach(async () => {
    wrapper = createComponent(selectedRegistrationType, registrationTitle)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with selected registration type', async () => {
    expect(wrapper.findComponent(RegistrationBar).exists()).toBe(true)
    expect(wrapper.find(registrationButton).exists()).toBe(true)
    expect(wrapper.vm.selectedRegistrationType).toBe(selectedRegistrationType)
  })
  it('renders all selected registration types and allows you to click on one', async () => {

    wrapper.find('.actions__more-actions__btn').trigger('click')

    await Vue.nextTick()

    // Verify list of other registration types
    expect(wrapper.find('.actions__more-actions').exists()).toBeTruthy()

    const registrationTypes = wrapper.findAll('.actions__more-actions .v-list-item')
    expect(registrationTypes.at(0).exists()).toBeTruthy()

    registrationTypes.at(0).trigger('click')

    const events = wrapper.emitted('selected-registration-type')
    expect(events.length).toBe(1)

  })
})
