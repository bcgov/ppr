// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import sinon from 'sinon'
import { axios } from '@/utils/axios-ppr'
import { mockedPartyCodeSearchResults, mockedSecuredParties2 } from './test-data'
import {
  mockedSecuredParties1,
  mockedRegisteringParty1,
  mockedSelectSecurityAgreement,
  mockedOtherCarbon
} from './test-data'

// Components
import { SecuredParties, EditParty, PartySearch } from '@/components/parties'
import { ChangeSecuredPartyDialog } from '@/components/dialogs'
import { SearchPartyIF } from '@/interfaces'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

const partyAutoComplete = '#secured-party-autocomplete'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<Debtors> object with the given parameters.
 */
function createComponent (
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(SecuredParties, {
    localVue,
    propsData: {},
    store,
    vuetify
  })
}

describe('Secured Party SA tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement())
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(SecuredParties).exists()).toBe(true)
    expect(wrapper.findComponent(PartySearch).exists()).toBeTruthy()
    // won't show edit collateral component until click
    expect(wrapper.findComponent(EditParty).exists()).toBeFalsy()
  })
})

describe('Secured Party store tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      securedParties: mockedSecuredParties1
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders secured party table and headers', async () => {
    expect(wrapper.find('.party-table').exists()).toBeTruthy()
    // column header class is text-start
    expect(wrapper.findAll('.text-start').length).toBe(5)
  })

  it('displays the correct rows when data is present', () => {
    const rowCount = wrapper.vm.$el.querySelectorAll('.v-data-table .party-row').length

    expect(rowCount).toEqual(1)
  })

  it('displays the correct data in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.v-data-table .party-row')[0]

    expect(item1.querySelectorAll('td')[0].textContent).toContain('SECURED PARTY COMPANY LTD.')
    expect(item1.querySelectorAll('td')[1].textContent).toContain('1234 Fort St.')
    expect(item1.querySelectorAll('td')[2].textContent).toContain('test@company.com')
  })
})

describe('Secured Party Other registration type tests', () => {
  let wrapper: Wrapper<any>
  const pprResp: Array<SearchPartyIF> = mockedPartyCodeSearchResults
  sessionStorage.setItem('PPR_API_URL', 'mock-url-ppr')
  let sandbox

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'get')
    get.returns(
      new Promise(resolve =>
        resolve({
          data: pprResp
        })
      )
    )
    await store.dispatch('setRegistrationType', mockedOtherCarbon())
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      registeringParty: mockedRegisteringParty1,
      securedParties: mockedSecuredParties2
    })
    wrapper = createComponent()
  })
  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
  })

  it('renders with default values', async () => {
    expect(wrapper.findComponent(SecuredParties).exists()).toBe(true)
    // won't show edit collateral component until click
    expect(wrapper.findComponent(EditParty).exists()).toBeFalsy()
    // shouldn't show party code search for other registration types
    expect(wrapper.findComponent(PartySearch).exists()).toBeFalsy()
    // should have autocomplete instead
    expect(wrapper.find(partyAutoComplete).exists()).toBeTruthy()

    // should have the dialog
    expect(wrapper.find(ChangeSecuredPartyDialog).exists()).toBeTruthy()
  })

  it('shows the dialog with a secured party code change', async () => {
    expect(wrapper.findComponent(SecuredParties).exists()).toBe(true)
    
    // should have the dialog
    expect(wrapper.find(ChangeSecuredPartyDialog).exists()).toBeTruthy()

    expect(wrapper.find('#secured-party-autocomplete').exists()).toBeTruthy()

    const autocompleteControls = wrapper.findAll(".v-input__slot")
    expect(autocompleteControls.length).toBe(1)
    
    // change the party code and then the dialog should show
    wrapper.vm.selectResult({code: 123, businessName: 'Forrest Gump'})

    expect(wrapper.find(ChangeSecuredPartyDialog).isVisible()).toBeTruthy()

  })
})
