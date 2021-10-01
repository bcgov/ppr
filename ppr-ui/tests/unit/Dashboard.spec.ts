// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { shallowMount, createLocalVue } from '@vue/test-utils'
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
  mockedDraftFinancingStatementAll
} from './test-data'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events
const selectedType = "selected-registration-type"

// selectors
const searchHeader = "#search-header"
const historyHeader = "#search-history-header"
const myRegHeader = "#registration-header"
const myRegTblFilter = "#my-reg-table-filter"
const myRegTblColSelection = "#column-selection"

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Dashboard component', () => {
  let wrapper: any
  let sandbox
  const { assign } = window.location

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any
    // stub api call
    sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'get')
    get.returns(new Promise(resolve => resolve({
      data: { ...mockedDraftFinancingStatementAll }
    })))

    // create a Local Vue and install router on it
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    await router.push({ name: 'dashboard' })
    wrapper = shallowMount(Dashboard, { localVue, store, router, vuetify })
    await flushPromises()
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
    sandbox.restore()
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

  it('displays my registration header and content', () => {
    const header = wrapper.findAll(myRegHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('My Registrations (0)')
    expect(wrapper.find(myRegTblFilter).exists()).toBe(true)
    expect(wrapper.find(myRegTblColSelection).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
  })

  it('updates the registration table when the filter is updated', async () => {
    const filterText = 'test'
    expect(wrapper.find(myRegTblFilter).exists()).toBe(true)
    wrapper.vm.$data.myRegSearch = filterText
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
    wrapper.findComponent(RegistrationTable).vm.$emit('editFinancingDraft', 'D0034001')
    await flushPromises()
    await Vue.nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.LENGTH_TRUST)
  })

  it('routes to edit amendment statement from draft', async () => {
    wrapper.findComponent(RegistrationTable).vm.$emit('editAmendmentDraft', { regNum: '100119B', docId: 'D9000207' })
    await Vue.nextTick()
    expect(wrapper.vm.$route.name).toBe(RouteNames.AMEND_REGISTRATION)
  })
})
