// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import sinon from 'sinon'

// Components
import { RegistrationTable } from '@/components/tables'
import { RegistrationBarTypeAheadList } from '@/components/registration'
import { RegistrationConfirmation } from '@/components/dialogs'


// Other
import {
  mockedRegistration1,
  mockedRegistration2,
  mockedDraft1,
  mockedDraft2
} from './test-data'
import { DraftIF, RegistrationSummaryIF } from '@/interfaces'
import { axios as pprAxios } from '@/utils/axios-ppr'
import { AccountProductCodes, AccountProductMemberships, UIRegistrationTypes } from '@/enums'
import flushPromises from 'flush-promises'

const vuetify = new Vuetify({})
const store = getVuexStore()

const regTable: string = '#registration-table'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchedResult> object with the given parameters.
 */
function createComponent (localVue): Wrapper<any> {
  localVue.use(CompositionApi)
  document.body.setAttribute('data-app', 'true')
  return mount(RegistrationTable, {
    localVue,
    store,
    vuetify
  })
}

describe('Test registration table with results', () => {
  let wrapper: Wrapper<any>
  const pprResp: RegistrationSummaryIF[] = [mockedRegistration1]
  sessionStorage.setItem('PPR_API_URL', 'mock-url-ppr')
  let sandbox
  let localVue = null

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    const get = sandbox.stub(pprAxios, 'get')
    get.returns(
      new Promise(resolve =>
        resolve({
          data: pprResp
        })
      )
    )
    await store.dispatch('setAccountProductSubscribtion', {
      [AccountProductCodes.RPPR]: {
        membership: AccountProductMemberships.MEMBER,
        roles: ['edit']
      }
    })
    localVue = require('vue')
    localVue.use(Vuetify)
    wrapper = createComponent(localVue)
  })

  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
    localVue = null
  })


  it('renders and displays correct registration elements', async () => {
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    // the api is going to be called twice, once for drafts and once for registrations
    // the tests can't tell the difference, so the same one is called twice
    await Vue.nextTick()
    await Vue.nextTick()
    expect(wrapper.vm.tableData.length).toBe(2)

    const registrationTableDisplay = wrapper.findAll(regTable)
    expect(registrationTableDisplay.length).toBe(1)
    const rows = wrapper.findAll('tr')
    // includes header, include the filter row, include registrations called twice
    expect(rows.length).toBe(pprResp.length + 3)

    // the first row is row 2
    expect(rows.at(2).text()).toContain('PDF')
    expect(rows.at(2).text()).toContain(mockedRegistration1.registrationNumber)
    expect(rows.at(2).text()).toContain(UIRegistrationTypes.SECURITY_AGREEMENT)
  })

  it('renders and displays the typeahead dropdown', async () => {
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    // the api is going to be called twice, once for drafts and once for registrations
    // the tests can't tell the difference, so the same one is called twice
    await Vue.nextTick()
    await Vue.nextTick()
    expect(wrapper.findComponent(RegistrationBarTypeAheadList).exists()).toBe(true)
    const autocomplete = wrapper.findComponent(RegistrationBarTypeAheadList)
    expect(autocomplete.text()).toContain('Registration Type')

  })

  it('shows the discharge modal', async () => {
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    // the api is going to be called twice, once for drafts and once for registrations
    // the tests can't tell the difference, so the same one is called twice
    await Vue.nextTick()
    await Vue.nextTick()
    expect(wrapper.findComponent(RegistrationConfirmation).exists()).toBe(true)
    const buttons = wrapper.findAll('.actions__more-actions__btn')
    expect(buttons.length).toBe(2)

    buttons.at(1).trigger('click')
    await Vue.nextTick()

    //it renders the actions drop down
    const menuItems = wrapper.findAll('.v-list-item__subtitle')
    expect(menuItems.length).toBe(4)
    expect(menuItems.at(1).text()).toContain('Total Discharge')

    //click the discharge
    menuItems.at(1).trigger('click')
    await flushPromises()
    const dialog = wrapper.findComponent(RegistrationConfirmation)
    
    expect(dialog.isVisible()).toBe(true)


  })

})

describe('Test draft table with results', () => {
  let wrapper: Wrapper<any>
  const pprResp: DraftIF[] = [mockedDraft1]
  sessionStorage.setItem('PPR_API_URL', 'mock-url-ppr')
  let sandbox
  let localVue = null

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    const get = sandbox.stub(pprAxios, 'get')
    get.returns(
      new Promise(resolve =>
        resolve({
          data: pprResp
        })
      )
    )
    localVue = require('vue')
    localVue.use(Vuetify)
    wrapper = createComponent(localVue)
  })

  afterEach(() => {
    sandbox.restore()
    wrapper.destroy()
    localVue = null
  })

  it('renders and displays correct draft elements', async () => {
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    // the api is going to be called twice, once for drafts and once for registrations
    // the tests can't tell the difference, so the same one is called twice
    await Vue.nextTick()
    await Vue.nextTick()
    expect(wrapper.vm.tableData.length).toBe(2)

    const registrationTableDisplay = wrapper.findAll(regTable)
    expect(registrationTableDisplay.length).toBe(1)
    const rows = wrapper.findAll('tr')
    // includes header, include the filter row, include registrations called twice
    expect(rows.length).toBe(pprResp.length + 3)

    // the first row is row 2
    expect(rows.at(2).text()).toContain('Draft') // draft status
    expect(rows.at(2).text()).toContain('N/A') // N/A for expiry
    expect(rows.at(2).text()).toContain(UIRegistrationTypes.REPAIRERS_LIEN)
  })
})
