// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { RegistrationLengthTrust } from '@/components/registration'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events

// Input field selectors / buttons
const selectDropDown: string = '.registration-bar-type-select'

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
function createComponent(
  defaultRegistrationType: String
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(RegistrationLengthTrust, {
    localVue,
    propsData: { defaultRegistrationType },
    store,
    vuetify
  })
}

describe('RegistrationLengthTrust SA tests', () => {
  let wrapper: Wrapper<any>
  const defaultRegistrationType: String = String('SA')

  beforeEach(async () => {
    wrapper = createComponent(defaultRegistrationType)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
    expect(wrapper.vm.showTrustIndenture).toBe(true)
    expect(wrapper.vm.lifeInfinite).toBe('')
    expect(wrapper.vm.trustIndenture).toBe(false)
    expect(wrapper.vm.lifeYearsEdit).toBe('')
    expect(wrapper.vm.lifeYearsDisabled).toBe(false)
    expect(wrapper.vm.maxYears).toBe('25')
  })
  it('renders trustIndenture', async () => {
    wrapper.vm.$data.trustIndenture = true
    expect(wrapper.vm.trustIndenture).toBe(true)
  })
  it('renders lifeYears', async () => {
    wrapper.vm.$data.lifeInfinite = 'false'
    wrapper.vm.$data.lifeYearsEdit = '3'
    expect(wrapper.vm.trustIndenture).toBe(true)
    await Vue.nextTick()
    wrapper.vm.$data.lifeYearsEdit = 'XX'
    await Vue.nextTick()
    expect(wrapper.vm.lifeYearsMessage).toBe('Registration length must be a number between 1 and 25.')
  })
  it('renders lifeInfinite', async () => {
    wrapper.vm.$data.lifeInfinite = 'true'
    await Vue.nextTick()
    wrapper.vm.$data.lifeYearsEdit = ''
    expect(wrapper.vm.lifeInfinite).toBe('true')
  })
})

describe('RegistrationLengthTrust RL tests', () => {
  let wrapper: Wrapper<any>
  const defaultRegistrationType: String = String('RL')

  beforeEach(async () => {
    wrapper = createComponent(defaultRegistrationType)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with RL values', async () => {
    expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
    expect(wrapper.vm.showTrustIndenture).toBe(false)
    expect(wrapper.vm.lifeInfinite).toBe('')
    expect(wrapper.vm.lifeYearsEdit).toBe('3')
    expect(wrapper.vm.lifeYearsDisabled).toBe(false)
  })
})

describe('RegistrationLengthTrust SG tests', () => {
  let wrapper: Wrapper<any>
  const defaultRegistrationType: String = String('SG')
  beforeEach(async () => {
    await store.dispatch('setLengthTrust', {
      valid: false,
      trustIndenture: true,
      lifeInfinite: false,
      lifeYears: 3
    })
    wrapper = createComponent(defaultRegistrationType)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with SG values', async () => {
    expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
    expect(wrapper.vm.showTrustIndenture).toBe(true)
    expect(wrapper.vm.lifeInfinite).toBe('')
    expect(wrapper.vm.lifeYearsEdit).toBe('3')
    expect(wrapper.vm.lifeYearsDisabled).toBe(false)
    expect(wrapper.vm.trustIndenture).toBe(true)
  })
})

describe('RegistrationLengthTrust life infinite tests', () => {
  let wrapper: Wrapper<any>
  const defaultRegistrationType: String = String('SG')
  beforeEach(async () => {
    await store.dispatch('setLengthTrust', {
      valid: true,
      trustIndenture: true,
      lifeInfinite: true,
      lifeYears: 0
    })
    wrapper = createComponent(defaultRegistrationType)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('life infinite renders with SG values', async () => {
    expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
    expect(wrapper.vm.showTrustIndenture).toBe(true)
    expect(wrapper.vm.lifeInfinite).toBe('true')
    expect(wrapper.vm.lifeYearsEdit).toBe('')
    expect(wrapper.vm.lifeYearsDisabled).toBe(true)
    expect(wrapper.vm.trustIndenture).toBe(true)
  })
})
