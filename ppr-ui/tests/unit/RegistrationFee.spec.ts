// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { RegistrationFee } from '@/components/common'
import { FeeSummaryIF } from '@/interfaces' // eslint-disable-line no-unused-vars

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events

// Input field selectors / buttons

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
  registrationType: string,
  hint: string,
  updatedFeeSummary: FeeSummaryIF
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(RegistrationFee, {
    localVue,
    propsData: { registrationType, hint, updatedFeeSummary },
    store,
    vuetify
  })
}

describe('Registration Fee component tests', () => {
  let wrapper: Wrapper<any>
  const defaultRegistrationType: string = 'Security Agreement'
  const defaultHint: string = ''
  var feeSummary: FeeSummaryIF = {
    feeAmount: 0,
    serviceFee: 1.50,
    quantity: 0,
    feeCode: ''
  }
  const updatedFeeSummary: FeeSummaryIF = {
    feeAmount: 5.00,
    serviceFee: 1.50,
    quantity: 3,
    feeCode: ''
  }

  beforeEach(async () => {
    wrapper = createComponent(defaultRegistrationType, defaultHint, feeSummary)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default registration fee summary', async () => {
    expect(wrapper.findComponent(RegistrationFee).exists()).toBe(true)
    expect(wrapper.vm.isComplete).toBe(false)
    expect(wrapper.vm.totalFees).toBe(0)
    expect(wrapper.vm.serviceFee).toBe(1.50)
    expect(wrapper.vm.registrationType).toBe(defaultRegistrationType)
  })
  it('renders with updated registration fee summary', async () => {
    expect(wrapper.findComponent(RegistrationFee).exists()).toBe(true)
    wrapper.vm.defaultFeeSummary = updatedFeeSummary
    await Vue.nextTick()
    // expect(wrapper.vm.isComplete).toBe(true)
    // expect(wrapper.vm.totalFees).toBe(15.00)
    // expect(wrapper.vm.totalAmount).toBe(16.50)
    expect(wrapper.vm.serviceFee).toBe(1.50)
    expect(wrapper.vm.registrationType).toBe(defaultRegistrationType)
  })
})
