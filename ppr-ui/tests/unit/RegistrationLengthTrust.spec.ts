// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  LengthTrustIF, StateModelIF
} from '@/interfaces'
import {
  mockedSelectSecurityAgreement,
  mockedSaleOfGoods,
  mockedMarriageMH
} from './test-data'

// Components
import { RegistrationLengthTrust } from '@/components/registration'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

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
  isRenewal: Boolean
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(RegistrationLengthTrust, {
    localVue,
    propsData: { isRenewal },
    store,
    vuetify
  })
}

describe('RegistrationLengthTrust SA tests', () => {
  let wrapper: Wrapper<any>
 
  beforeEach(async () => {
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement())
    wrapper = createComponent(false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
    // show trust indenture will be true for security agreement only
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
    expect(wrapper.vm.lifeYearsMessage).toBe('Registration length must be a number between 1 and 25')
    const state = wrapper.vm.$store.state.stateModel as StateModelIF
    expect(state.registration.lengthTrust.valid).toBe(false)
  })

  it('renders lifeInfinite', async () => {
    wrapper.find('#length-infinite').trigger('click')
    await Vue.nextTick()
    wrapper.vm.$data.lifeYearsEdit = ''
    expect(wrapper.vm.lifeInfinite).toBe('true')
    expect(wrapper.vm.$store.state.stateModel.registration.lengthTrust.valid).toBe(true)
  })
})

describe('RegistrationLengthTrust SG tests', () => {
  let wrapper: Wrapper<any>
  beforeEach(async () => {
    await store.dispatch('setLengthTrust', {
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 3,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
    })
    await store.dispatch('setRegistrationType', mockedSaleOfGoods())
    wrapper = createComponent(false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with SG values', async () => {
    expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
    // show trust indenture will be true for security agreement only
    expect(wrapper.vm.showTrustIndenture).toBe(false)
    expect(wrapper.vm.lifeInfinite).toBe('false')
    expect(wrapper.vm.lifeYearsEdit).toBe('3')
    expect(wrapper.vm.lifeYearsDisabled).toBe(false)
    expect(wrapper.vm.trustIndenture).toBe(false)
    await Vue.nextTick()
    expect(wrapper.vm.$store.state.stateModel.registration.lengthTrust.lifeYears).toBe(3)
    expect(wrapper.vm.$store.state.stateModel.registration.lengthTrust.lifeInfinite).toBe(false)
    expect(wrapper.vm.$store.state.stateModel.registration.lengthTrust.valid).toBe(true)
  })
})

describe('RegistrationLengthTrust life infinite tests', () => {
  let wrapper: Wrapper<any>
  beforeEach(async () => {
    await store.dispatch('setLengthTrust', {
      valid: true,
      trustIndenture: false,
      lifeInfinite: true,
      lifeYears: 0,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
    })
    wrapper = createComponent(false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('life infinite renders with SG values', async () => {
    expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
    expect(wrapper.vm.lifeInfinite).toBe('true')
    expect(wrapper.vm.lifeYearsEdit).toBe('')
    expect(wrapper.vm.lifeYearsDisabled).toBe(true)
    expect(wrapper.vm.trustIndenture).toBe(false)
    expect(wrapper.vm.$store.state.stateModel.registration.lengthTrust.valid).toBe(true)
  })
})


describe('RegistrationLengthTrust Crown tests', () => {
  let wrapper: Wrapper<any>
  beforeEach(async () => {
    await store.dispatch('setRegistrationType', mockedMarriageMH())
    wrapper = createComponent(false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default infinite values', async () => {
    expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
    expect(wrapper.vm.showTrustIndenture).toBe(false)
    expect(wrapper.find('#trust-indenture-checkbox').exists()).toBe(false)
    expect(wrapper.find('#length-in-years').exists()).toBe(false)
    
    expect(wrapper.find('#lien-amount').exists()).toBe(false)
    
    expect(wrapper.vm.infinityPreselected()).toBe(true)
    expect(wrapper.vm.$store.state.stateModel.registration.lengthTrust.valid).toBe(true)
   
  })
  
})

describe('RegistrationLengthTrust SA renewal test', () => {
  let wrapper: Wrapper<any>
  beforeEach(async () => {
    await store.dispatch('setLengthTrust', {
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 0,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: ''
    })
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement())
    await store.dispatch('setRegistrationExpiryDate', '2021-03-31T07:00:00+00:00')
    
    wrapper = createComponent(true)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
    expect(wrapper.find('#length-in-years').exists()).toBe(true)
    // set renewal length to 1 year
    wrapper.vm.$data.lifeYearsEdit = '1'
    await Vue.nextTick()
    expect(wrapper.find('#new-expiry').text()).toContain('March 31, 2022')
    expect(wrapper.vm.$store.state.stateModel.registration.lengthTrust.lifeYears).toBe(1)
    expect(wrapper.vm.$store.state.stateModel.registration.lengthTrust.valid).toBe(true)
  })
  
})

