// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  LengthTrustIF
} from '@/interfaces'
import {
  mockedSelectSecurityAgreement,
  mockedRepairersLien,
  mockedSaleOfGoods,
  mockedMarriageMH
} from './test-data'

// Components
import { RegistrationRepairersLien } from '@/components/registration'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

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
function createComponent (
  isRenewal: Boolean
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(RegistrationRepairersLien, {
    localVue,
    propsData: { isRenewal },
    store,
    vuetify
  })
}


describe('RegistrationLengthTrust RL tests', () => {
  let wrapper: Wrapper<any>
  const defaultRegistrationType: String = String('RL')
  beforeEach(async () => {
    await store.dispatch('setRegistrationType', mockedRepairersLien())
    wrapper = createComponent(false)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with RL values', async () => {
    expect(wrapper.findComponent(RegistrationRepairersLien).exists()).toBe(true)
    expect(wrapper.vm.showTrustIndenture).toBe(false)
    expect(wrapper.vm.lifeInfinite).toBe('false')
    expect(wrapper.vm.surrenderDate).toBe('')
    expect(wrapper.vm.showErrorLienAmount).toBe(false)
    expect(wrapper.vm.showErrorSurrenderDate).toBe(false)
    expect(wrapper.vm.minSurrenderDate).toBeDefined()
    expect(wrapper.vm.lienAmount).toBe('')
    expect(wrapper.vm.lengthSummary).toBe('180 Days')
    expect(wrapper.vm.lifeYearsEdit).toBe('1')
    expect(wrapper.vm.lifeYearsDisabled).toBe(false)
    expect(wrapper.vm.lienAmountSummary).toBe('Not entered')
    expect(wrapper.vm.surrenderDateSummary).toBe('Not entered')
  })
  it('renders lienAmount', async () => {
    wrapper.vm.$data.lienAmount = '$1,000,000'
    await Vue.nextTick()
    expect(wrapper.vm.lienAmountMessage).toBe('')
    expect(wrapper.vm.showErrorLienAmount).toBe(false)
    wrapper.vm.$data.lienAmount = '$1'
    await Vue.nextTick()
    expect(wrapper.vm.lienAmountMessage).toBe('')
    expect(wrapper.vm.showErrorLienAmount).toBe(false)
    wrapper.vm.$data.lienAmount = 'junk'
    await Vue.nextTick()
    expect(wrapper.vm.lienAmountMessage).toBe('Lien amount must be a number greater than 0.')
    expect(wrapper.vm.showErrorLienAmount).toBe(true)
    wrapper.vm.$data.lienAmount = '$1$'
    await Vue.nextTick()
    expect(wrapper.vm.lienAmountMessage).toBe('Lien amount must be a number greater than 0.')
    expect(wrapper.vm.showErrorLienAmount).toBe(true)
  })
})


describe('RegistrationLengthTrust RL renewal test', () => {
  let wrapper: Wrapper<any>
  const defaultRegistrationType: String = String('RL')
  beforeEach(async () => {
    await store.dispatch('setRegistrationType', mockedRepairersLien())
    await store.dispatch('setRegistrationExpiryDate', '2021-07-28T07:00:00+00:00')
    await store.dispatch('setLengthTrust', {
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 0,
      showInvalid: false,
      surrenderDate: '2021-01-21T07:00:00+00:00',
      lienAmount: ''
    })
    
    wrapper = createComponent(true)
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(RegistrationRepairersLien).exists()).toBe(true)
    expect(wrapper.find('#length-in-years').exists()).toBe(false)
    // new expiry date (180 days)
    expect(wrapper.find('#new-expiry-rl').text()).toContain('January 24, 2022')
    // surrender date
    expect(wrapper.find('#surrender-date').text()).toContain('January 21, 2021')
    
  })
  
})
