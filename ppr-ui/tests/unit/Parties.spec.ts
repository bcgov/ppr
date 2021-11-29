// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper, shallowMount } from '@vue/test-utils'

// Components
import { Debtors, EditParty, Parties, PartySearch, RegisteringParty, SecuredParties } from '@/components/parties'
import { mockedDebtors1, mockedRegisteringParty1, mockedSecuredParties1, mockedSelectSecurityAgreement } from './test-data'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()


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
  
  return shallowMount(Parties, {
    localVue,
    propsData: {},
    store,
    vuetify
  })
}

describe('Parties component tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    const registrationType = mockedSelectSecurityAgreement()
    await store.dispatch('setAuthRoles', [])

    await store.dispatch('setRegistrationType', registrationType)
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      debtors: mockedDebtors1,
      securedParties: mockedSecuredParties1,
      registeringParty: mockedRegisteringParty1
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(Parties).exists()).toBe(true)
    expect(wrapper.findComponent(Debtors).exists()).toBe(true)
    expect(wrapper.findComponent(SecuredParties).exists()).toBe(true)
    expect(wrapper.findComponent(RegisteringParty).exists()).toBe(true)
    
  })


  it('does show the registering party', async () => {
    expect(wrapper.findComponent(RegisteringParty).isVisible()).toBe(true)
  })
})


describe('Parties component tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    const registrationType = mockedSelectSecurityAgreement()
    await store.dispatch('setRegistrationType', registrationType)
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      debtors: mockedDebtors1,
      securedParties: mockedSecuredParties1,
      registeringParty: mockedRegisteringParty1
    })
    await store.dispatch('setAuthRoles', ['staff', 'gov_account_user'])
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(Parties).exists()).toBe(true)
    expect(wrapper.findComponent(Debtors).exists()).toBe(true)
    expect(wrapper.findComponent(SecuredParties).exists()).toBe(true)
    // initially registering party does not show up, only party search
    expect(wrapper.findComponent(RegisteringParty).exists()).toBe(false)
    
  })

  it('shows the party search screen for sbc', async () => {
    expect(wrapper.findComponent(PartySearch).isVisible()).toBe(true)
  })

  
})
