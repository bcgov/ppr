// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'

// Local
import { RegistrationBarTypeAheadList } from '@/components/registration'
import { RegistrationOtherDialog } from '@/components/dialogs'
import {
  RegistrationTypes,
  RegistrationTypesMiscellaneousCC,
  RegistrationTypesMiscellaneousOT,
  RegistrationTypesStandard
} from '@/resources'
import { RegistrationTypeIF } from '@/interfaces' // eslint-disable-line no-unused-vars
import { UIRegistrationTypes } from '@/enums'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// registration lists
const standardRegistrations: Array<RegistrationTypeIF> = RegistrationTypesStandard
const miscCrownChargeRegistrations: Array<RegistrationTypeIF> = RegistrationTypesMiscellaneousCC
const miscOtherRegistrations: Array<RegistrationTypeIF> = RegistrationTypesMiscellaneousOT
const allRegistrations: Array<RegistrationTypeIF> = RegistrationTypes

// Events
const selected = 'selected'

// Input field selectors / buttons
const registrationTypeAhead = '.registrationTypeAhead'

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
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(RegistrationBarTypeAheadList, {
    localVue,
    propsData: {},
    store,
    vuetify
  })
}

describe('RegistrationBar rppr subscribed autocomplete tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders registration autocomplete type ahead box', async () => {
    expect(wrapper.findComponent(RegistrationBarTypeAheadList).exists()).toBe(true)
    // check autocomplete displayed
    expect(wrapper.find(registrationTypeAhead).exists()).toBe(true)
  })

  it('emits registration on select', async () => {
    wrapper.vm.$data.selected = miscCrownChargeRegistrations[4]
    await flushPromises()
    expect(getLastEvent(wrapper, selected)).toBe(miscCrownChargeRegistrations[4])
  })

  it('gives dialog when *other* type is selected', async () => {
    const otherRegistration = miscCrownChargeRegistrations[miscCrownChargeRegistrations.length - 1]
    expect(otherRegistration.registrationTypeUI).toBe(UIRegistrationTypes.OTHER)
    wrapper.vm.$data.selected = otherRegistration
    await flushPromises()
    expect(getLastEvent(wrapper, selected)).toBeNull()
    const dialog = wrapper.findComponent(RegistrationOtherDialog)
    expect(dialog.exists()).toBe(true)
    expect(dialog.vm.$props.display).toBe(true)
    dialog.vm.$emit('proceed', false)
    await flushPromises()
    expect(getLastEvent(wrapper, selected)).toBeNull()
    expect(dialog.vm.$props.display).toBe(false)
    expect(wrapper.vm.$data.selected).toBeNull()
    wrapper.vm.$data.selected = otherRegistration
    await flushPromises()
    dialog.vm.$emit('proceed', true)
    await flushPromises()
    expect(getLastEvent(wrapper, selected)).toBe(otherRegistration)
    expect(dialog.vm.$props.display).toBe(false)
  })
})
