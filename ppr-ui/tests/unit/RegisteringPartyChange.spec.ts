// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import flushPromises from 'flush-promises'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  mockedDebtors1,
  mockedRegisteringParty1,
  mockedSecuredParties1,
  mockedSelectSecurityAgreement
} from './test-data'

// Components
import PartySummary from '@/components/parties/PartySummary.vue' // need to import like this
import { EditParty, PartySearch, RegisteringParty, RegisteringPartyChange } from '@/components/parties/party'
import { CautionBox } from '@/components/common'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

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
  return mount(RegisteringPartyChange, {
    localVue,
    store,
    vuetify
  })
}

describe('Parties tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setAuthRoles', [])
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement())
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      debtors: [],
      securedParties: [],
      registeringParty: mockedRegisteringParty1
    })
    wrapper = createComponent()
    await flushPromises()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(RegisteringPartyChange).exists()).toBe(true)
    expect(wrapper.findComponent(RegisteringParty).exists()).toBe(true)
    //does not show party search and edit when not change
    expect(wrapper.findComponent(PartySearch).exists()).toBe(false)
    expect(wrapper.findComponent(EditParty).exists()).toBe(false)
  })

  it('shows the search on change', async () => {
    wrapper.vm.openChangeScreen = true
    await Vue.nextTick()
    //does not show party search and edit when not change
    expect(wrapper.findComponent(PartySearch).exists()).toBe(true)
    expect(wrapper.findComponent(EditParty).exists()).toBe(false)
  })

  it('handles address country change in registering party', async () => {
    const newRegParty = {
      ...mockedRegisteringParty1
    }
    // default is saved properly in store
    expect(wrapper.vm.registeringParty).toEqual(newRegParty)

    // update address
    const addressChange1 = {
      street: 'test change 1',
      streetAdditional: '1',
      city: 'Vancouver',
      region: 'BC',
      country: 'CA',
      postalCode: 'V0N 1G0',
      deliveryInstructions: ''
    }
    newRegParty.address = addressChange1
    await wrapper.vm.$store.dispatch(
      'setAddSecuredPartiesAndDebtors',
      { registeringParty: newRegParty, debtors: [], securedParties: [] }
    )
    expect(
      wrapper.vm.$store.state.stateModel.registration.parties.registeringParty.address
    ).toEqual(addressChange1)
    expect(wrapper.vm.registeringParty).toEqual(newRegParty)

    // update address again - change country
    const addressChange2 = {
      street: 'test change 2',
      streetAdditional: '1',
      city: 'Philadelphia',
      region: 'PA',
      country: 'US',
      postalCode: '19132-4594',
      deliveryInstructions: ''
    }
    newRegParty.address = addressChange2
    await wrapper.vm.$store.dispatch(
      'setAddSecuredPartiesAndDebtors',
      { registeringParty: newRegParty, debtors: [], securedParties: [] }
    )
    expect(
      wrapper.vm.$store.state.stateModel.registration.parties.registeringParty.address
    ).toEqual(addressChange2)
    expect(wrapper.vm.registeringParty).toEqual(newRegParty)
  })

  

  it('trigger change registering party edit', async () => {
    wrapper.vm.changeRegisteringParty()
    await Vue.nextTick()
    // show cancel button
    expect(wrapper.find('#cancel-btn-chg-reg-party').exists()).toBeTruthy()
  })
})

describe('Parties sbc user tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    const registrationType = mockedSelectSecurityAgreement()
    await store.dispatch('setRegistrationType', registrationType)
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      debtors: mockedDebtors1,
      securedParties: mockedSecuredParties1,
      registeringParty: mockedRegisteringParty1
    })
    store.dispatch('setRoleSbc', true)
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  
  it('shows the party search screen for sbc', async () => {
    expect(wrapper.findComponent(PartySearch).isVisible()).toBe(true)
    // no tooltip
    expect(wrapper.find('.registering-tooltip').exists()).toBeFalsy()
    // no cancel button
    expect(wrapper.find('#cancel-btn-chg-reg-party').exists()).toBeFalsy()
  })
})
