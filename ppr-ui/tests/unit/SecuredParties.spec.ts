// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import sinon from 'sinon'
import { axios } from '@/utils/axios-ppr'
import { cloneDeep } from 'lodash'
import {
  mockedSecuredParties1,
  mockedSecuredParties2,
  mockedSecuredParties3,
  mockedRegisteringParty1,
  mockedSelectSecurityAgreement,
  mockedSecuredPartiesAmendment,
  mockedPartyCodeSearchResults,
  mockedOtherCarbon
} from './test-data'

// Components
import { SecuredParties, EditParty, PartySearch } from '@/components/parties'
import { ChangeSecuredPartyDialog } from '@/components/dialogs'
import { SearchPartyIF } from '@/interfaces'
import { ActionTypes, RegistrationFlowType } from '@/enums'

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

  it('is not valid if you remove the secured party for admendment', async () => {
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.AMENDMENT)
    const parties = cloneDeep(mockedSecuredParties2)
    parties[0].action = ActionTypes.REMOVED
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      registeringParty: mockedRegisteringParty1,
      securedParties: parties
    })

    //click remove
    wrapper.find('.v-data-table .party-row .actions__more-actions .v-remove').trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.getSecuredPartyValidity()).toBe(false)
  })

  it('shows the the removed & added secured parties for admendment', async () => {
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.AMENDMENT)
    const parties = cloneDeep(mockedSecuredParties1)
    expect(parties.length).toEqual(1)
    parties[0].action = ActionTypes.REMOVED
    parties[1] = {
      action: ActionTypes.ADDED,
      businessName: 'SECURED PARTY COMPANY LTD.',
      emailAddress: 'test@company.com',
      address: {
        street: '1234 Fort St.',
        streetAdditional: '2nd floor',
        city: 'Victoria',
        region: 'BC',
        country: 'CA',
        postalCode: 'V8R1L2',
        deliveryInstructions: ''
      }
    }
    
    expect(parties.length).toEqual(2)
    wrapper.vm.securedParties = parties
    await Vue.nextTick()
    const rowCount = wrapper.vm.$el.querySelectorAll('.v-data-table .party-row').length
    // one removed party, one added party
    expect(rowCount).toEqual(2)
    const item1 = wrapper.vm.$el.querySelectorAll('.v-data-table .party-row')[0]
    const item2 = wrapper.vm.$el.querySelectorAll('.v-data-table .party-row')[1]
    expect(item1.querySelectorAll('td')[0].textContent).toContain('DELETED')
    expect(item2.querySelectorAll('td')[0].textContent).toContain('ADDED')

  })
})

describe('Secured party amendment tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      securedParties: mockedSecuredPartiesAmendment
    })
    await store.dispatch('setOriginalAddSecuredPartiesAndDebtors', {
      securedParties: mockedSecuredPartiesAmendment
    })
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement())
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.AMENDMENT)
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('displays the correct rows when data is present', () => {
    const rowCount = wrapper.vm.$el.querySelectorAll('.v-data-table .party-row').length
    // three parties, three rows
    expect(rowCount).toEqual(3)
  })

  it('displays the correct chips in the table rows', () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.v-data-table .party-row')[0]
    const item2 = wrapper.vm.$el.querySelectorAll('.v-data-table .party-row')[1]
    const item3 = wrapper.vm.$el.querySelectorAll('.v-data-table .party-row')[2]
    expect(item1.querySelectorAll('td')[0].textContent).toContain('ADDED')
    expect(item2.querySelectorAll('td')[0].textContent).toContain('AMENDED')
    expect(item3.querySelectorAll('td')[0].textContent).toContain('DELETED')
  })

  it('displays the correct actions in the table rows', async () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.v-data-table .party-row')[0]
    const item2 = wrapper.vm.$el.querySelectorAll('.v-data-table .party-row')[1]
    const item3 = wrapper.vm.$el.querySelectorAll('.v-data-table .party-row')[2]
    expect(item1.querySelectorAll('td')[4].textContent).toContain('Edit')
    expect(item2.querySelectorAll('td')[4].textContent).toContain('Undo')
    expect(item3.querySelectorAll('td')[4].textContent).toContain('Undo')

    const dropDowns = wrapper.findAll('.v-data-table .party-row .actions__more-actions__btn')
    // 2 drop downs
    expect(dropDowns.length).toBe(2)
    // click the drop down arrow
    dropDowns.at(0).trigger('click')
    await Vue.nextTick()
    expect(wrapper.findAll('.actions__more-actions .v-list-item__subtitle').length).toBe(1)

    // click the second drop down
    dropDowns.at(1).trigger('click')
    await Vue.nextTick()
    const options = wrapper.findAll('.actions__more-actions .v-list-item__subtitle')
    // options from first drop down
    expect(options.at(0).text()).toContain('Remove')
    expect(options.at(1).text()).toContain('Amend')
    // option from second drop down
    expect(options.at(2).text()).toContain('Delete')

  })

  it('displays the error', async () => {
    const parties = cloneDeep(mockedSecuredParties1)
    expect(parties.length).toEqual(1)
    parties[0].action = ActionTypes.REMOVED
    wrapper.vm.$data.securedParties = parties
    wrapper.vm.$props.setShowInvalid = true
    expect(wrapper.vm.getSecuredPartyValidity()).toBe(false)
    wrapper.vm.$data.showErrorSecuredParties = true
    await Vue.nextTick()
    expect(wrapper.findAll('.invalid-message').length).toBe(1)
  })


  it('goes from valid to invalid', async () => {
    const parties = cloneDeep(mockedSecuredParties1)
    expect(parties.length).toEqual(1)
    wrapper.vm.$data.securedParties = parties
    await Vue.nextTick()
    expect(wrapper.vm.getSecuredPartyValidity()).toBe(true)
    expect(wrapper.findAll('.invalid-message').length).toBe(0)
    // remove said secured party
    // click the drop down arrow
    wrapper.find('.v-data-table .party-row .actions__more-actions__btn').trigger('click')
    await Vue.nextTick()
    //click remove
    wrapper.find('.actions__more-actions .v-list-item__subtitle').trigger('click')
    await Vue.nextTick()
    expect(wrapper.vm.getSecuredPartyValidity()).toBe(false)
    wrapper.vm.$data.showErrorSecuredParties = true
    await Vue.nextTick()
    expect(wrapper.findAll('.invalid-message').length).toBe(1)

  })
})


describe('Secured party with code test', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setAddSecuredPartiesAndDebtors', {
      securedParties: mockedSecuredParties3
    })
    await store.dispatch('setOriginalAddSecuredPartiesAndDebtors', {
      securedParties: mockedSecuredParties3
    })
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement())
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })


  it('displays remove only for a secured party with code', async () => {
    const item1 = wrapper.vm.$el.querySelectorAll('.v-data-table .party-row')[0]
    expect(item1.querySelectorAll('td')[4].textContent).toContain('Remove')
    
    const dropDowns = wrapper.findAll('.v-data-table .party-row .actions__more-actions__btn')
    // 0 drop downs
    expect(dropDowns.length).toBe(0)
  

  })

  

})
