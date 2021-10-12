// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { shallowMount, createLocalVue, Wrapper, mount } from '@vue/test-utils'
import CompositionApi from '@vue/composition-api'
import flushPromises from 'flush-promises'
import sinon from 'sinon'
// local components
import { Dashboard } from '@/views'
import { SearchBar } from '@/components/search'
import { RegistrationTable, SearchHistory } from '@/components/tables'
import { RegistrationBar } from '@/components/registration'
// local types/helpers, etc.
import { RouteNames, UISearchTypes } from '@/enums'
import { registrationTableHeaders } from '@/resources'
import { axios } from '@/utils/axios-ppr'
// unit test data, etc.
import mockRouter from './MockRouter'
import {
  mockedSearchResponse,
  mockedSearchHistory,
  mockedSelectSecurityAgreement,
  mockedDraftFinancingStatementStep1,
  mockedRegistration1,
  mockedDraft1
} from './test-data'
import { DraftResultIF, RegistrationSummaryIF } from '@/interfaces'
import { BaseDialog } from '@/components/dialogs'
import { registrationFoundDialog } from '@/resources/dialogOptions'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events
const selectedType = "selected-registration-type"

// selectors
const searchHeader = "#search-header"
const historyHeader = "#search-history-header"
const myRegHeader = "#registration-header"
const myRegAddTextBox = "#my-reg-add"
const myRegTblFilter = "#my-reg-table-filter"
const myRegTblColSelection = "#column-selection"

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Dashboard component', () => {
  let wrapper: Wrapper<any>
  let sandbox
  const { assign } = window.location
  sessionStorage.setItem('PPR_API_URL', 'mock-url-ppr')
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')

  const draftDocId = 'D0034001'

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any
    // stub api calls
    sandbox = sinon.createSandbox()
    const getStub = sandbox.stub(axios, 'get')
    const getSearchHistory = getStub.withArgs('search-history')
    getSearchHistory.returns(new Promise(resolve => resolve({ data: { searches: [] }})))
    const getDraft = getStub.withArgs(`drafts/${draftDocId}`)
    getDraft.returns(new Promise(resolve => resolve({ data: mockedDraftFinancingStatementStep1 })))
    const getMyRegDrafts = getStub.withArgs('drafts')
    getMyRegDrafts.returns(new Promise(resolve => resolve({ data: [] })))
    const getMyRegHistory = getStub.withArgs('financing-statements/registrations')
    getMyRegHistory.returns(new Promise(resolve => resolve({ data: [] })))

    // create a Local Vue and install router on it
    const localVue = createLocalVue()
    localVue.use(CompositionApi)
    localVue.use(Vuetify)
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    await router.push({ name: 'dashboard' })
    wrapper = mount(Dashboard, { localVue, store, propsData: { appReady: true }, router, vuetify })
    await flushPromises()
  })

  afterEach(() => {
    window.location.assign = assign
    sandbox.restore()
    wrapper.destroy()
  })

  it('renders Dashboard View with child components', () => {
    expect(wrapper.findComponent(Dashboard).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationBar).exists()).toBe(true)
    expect(wrapper.findComponent(SearchBar).exists()).toBe(true)
    expect(wrapper.findComponent(SearchHistory).exists()).toBe(true)
  })

  it('displays the search header', () => {
    const header = wrapper.findAll(searchHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('Personal Property Search')
  })

  it('displays default search history header', () => {
    expect(wrapper.vm.getSearchHistory).toBeNull // eslint-disable-line no-unused-expressions
    expect(wrapper.vm.searchHistoryLength).toBe(0)
    const header = wrapper.findAll(historyHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('My Searches (0)')
  })

  it('updates the search history header based on history data', async () => {
    wrapper.vm.setSearchHistory(mockedSearchHistory.searches)
    await Vue.nextTick()
    await Vue.nextTick()
    expect(wrapper.vm.getSearchHistory?.length).toBe(6)
    expect(wrapper.vm.searchHistoryLength).toBe(6)
    const header = wrapper.findAll(historyHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('My Searches (6)')
  })

  it('routes to search after getting a search response', async () => {
    wrapper.vm.setSearchResults(mockedSearchResponse[UISearchTypes.SERIAL_NUMBER])
    await Vue.nextTick()
    expect(wrapper.vm.$route.name).toBe('search')
  })

  it('routes to new registration after selecting registration type', async () => {
    wrapper.findComponent(RegistrationBar).vm.$emit(selectedType, mockedSelectSecurityAgreement)
    await Vue.nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.LENGTH_TRUST)
  })

  it('routes to discharge after selecting registration type', async () => {
    wrapper.findComponent(RegistrationTable).vm.$emit('discharge', '123456B')
    await Vue.nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.REVIEW_DISCHARGE)
  })

  it('routes to renew after selecting registration type', async () => {
    wrapper.findComponent(RegistrationTable).vm.$emit('renew', '123456B')
    await Vue.nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.RENEW_REGISTRATION)
  })

  it('routes to edit financing statement', async () => {
    wrapper.findComponent(RegistrationTable).vm.$emit('editFinancingDraft', draftDocId)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.LENGTH_TRUST)
  })

  it('routes to edit amendment statement from draft', async () => {
    wrapper.findComponent(RegistrationTable).vm.$emit('editAmendmentDraft', { regNum: '100119B', docId: 'D9000207' })
    await Vue.nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.AMEND_REGISTRATION)
  })
})

describe('Dashboard registration table tests', () => {
  let wrapper: Wrapper<any>
  let sandbox
  const { assign } = window.location
  const myRegDrafts: DraftResultIF[] = [mockedDraft1]
  const myRegHistory: RegistrationSummaryIF[] = [mockedRegistration1]
  sessionStorage.setItem('PPR_API_URL', 'mock-url-ppr')
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    const getStub = sandbox.stub(axios, 'get')
    const getSearchHistory = getStub.withArgs('search-history')
    getSearchHistory.returns(new Promise(resolve => resolve({ data: { searches: [] }})))
    const getMyRegDrafts = getStub.withArgs('drafts')
    getMyRegDrafts.returns(new Promise(resolve => resolve({ data: myRegDrafts })))
    const getMyRegHistory = getStub.withArgs('financing-statements/registrations')
    getMyRegHistory.returns(new Promise(resolve => resolve({ data: myRegHistory })))

    const localVue = createLocalVue()
    localVue.use(CompositionApi)
    localVue.use(Vuetify)
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    await router.push({ name: 'dashboard' })
    wrapper = mount(Dashboard, { localVue, store, propsData: { appReady: true }, router, vuetify })
    await flushPromises()
  })

  afterEach(() => {
    window.location.assign = assign
    sandbox.restore()
    wrapper.destroy()
  })

  it('displays my registration header and content', () => {
    expect(wrapper.vm.myRegDataDrafts).toEqual(myRegDrafts)
    expect(wrapper.vm.myRegDataHistory).toEqual(myRegHistory)
    const header = wrapper.findAll(myRegHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('My Registrations (2)')
    expect(wrapper.find(myRegTblFilter).exists()).toBe(true)
    expect(wrapper.find(myRegTblColSelection).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setRegistrationHistory)
      .toEqual([myRegDrafts[0], myRegHistory[0]])
  })

  it('updates the registration table when the filter is updated', async () => {
    const filterText = 'test'
    expect(wrapper.find(myRegTblFilter).exists()).toBe(true)
    wrapper.vm.$data.myRegFilter = filterText
    await flushPromises()
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setSearch).toBe(filterText)
  })

  it('updates the registration table with column selection', async () => {
    const newColumnSelection = [...registrationTableHeaders].slice(0,2)
    expect(wrapper.find(myRegTblColSelection).exists()).toBe(true)
    wrapper.vm.$data.myRegHeaders = newColumnSelection
    await flushPromises()
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setHeaders).toEqual(newColumnSelection)
  })
})

describe('Dashboard add registration tests', () => {
  let wrapper: Wrapper<any>
  let sandbox
  const { assign } = window.location
  const myRegAdd: RegistrationSummaryIF = mockedRegistration1
  sessionStorage.setItem('PPR_API_URL', 'mock-url-ppr')
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    const getStub = sandbox.stub(axios, 'get')
    const getSearchHistory = getStub.withArgs('search-history')
    getSearchHistory.returns(new Promise(resolve => resolve({ data: { searches: [] }})))
    const getMyRegDrafts = getStub.withArgs('drafts')
    getMyRegDrafts.returns(new Promise(resolve => resolve({ data: [] })))
    const getMyRegHistory = getStub.withArgs('financing-statements/registrations')
    getMyRegHistory.returns(new Promise(resolve => resolve({ data: [] })))

    const getMyRegAdd = getStub.withArgs(
      `financing-statements/registrations/${myRegAdd.baseRegistrationNumber}`
    )
    getMyRegAdd.returns(new Promise(resolve => resolve({ data: myRegAdd })))

    const postMyRegAdd = sandbox.stub(axios, 'post').withArgs(
      `financing-statements/registrations/${myRegAdd.baseRegistrationNumber}`
    )
    postMyRegAdd.returns(new Promise(resolve => resolve({ data: myRegAdd })))

    const localVue = createLocalVue()
    localVue.use(CompositionApi)
    localVue.use(Vuetify)
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    await router.push({ name: 'dashboard' })
    wrapper = mount(Dashboard, { localVue, store, propsData: { appReady: true }, router, vuetify })
    await flushPromises()
  })

  afterEach(() => {
    window.location.assign = assign
    sandbox.restore()
    wrapper.destroy()
  })

  it('displays the add registration text box + shows dialog + adds it to table', async () => {
    // FUTURE: add all cases (i.e. simulate error flows etc.)
    expect(wrapper.find(myRegAddTextBox).exists()).toBe(true)
    expect(wrapper.vm.myRegAdd).toBe('')
    await wrapper.find(myRegAddTextBox).setValue('123')
    expect(wrapper.vm.myRegAdd).toBe('123')
    expect(wrapper.vm.myRegAddInvalid).toBe(true)
    await wrapper.find(myRegAddTextBox).setValue(myRegAdd.baseRegistrationNumber)
    expect(wrapper.vm.myRegAddInvalid).toBe(false)
    // simulate add
    wrapper.vm.findRegistration(myRegAdd.baseRegistrationNumber)
    await Vue.nextTick()
    expect(wrapper.vm.loading).toBe(true)
    await flushPromises()
    expect(wrapper.vm.myRegAddDialogDisplay).toBe(true)
    expect(wrapper.vm.loading).toBe(false)
    expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(true)
    expect(wrapper.findComponent(BaseDialog).vm.$props.setOptions.text)
      .toContain(registrationFoundDialog.text)
    expect(wrapper.vm.myRegAddDialogError).toBe(false)
    expect(wrapper.vm.myRegDataHistory).toEqual([])
    wrapper.findComponent(BaseDialog).vm.$emit('proceed', true)
    await flushPromises()
    expect(wrapper.vm.myRegDataHistory).toEqual([myRegAdd])
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(false)
  })
})
