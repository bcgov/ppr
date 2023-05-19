// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { createLocalVue, Wrapper, mount, shallowMount } from '@vue/test-utils'
import flushPromises from 'flush-promises'
import sinon from 'sinon'
import { StatusCodes } from 'http-status-codes'
import { cloneDeep } from 'lodash'
// local components
import { Dashboard } from '@/views'
import { BaseSnackbar } from '@/components/common'
import { RegistrationConfirmation } from '@/components/dialogs'
import { SearchBar } from '@/components/search'
import { RegistrationTable, SearchHistory } from '@/components/tables'
import { RegistrationBar } from '@/components/registration'
// local types/helpers, etc.
import { AuthRoles, ProductCode, RouteNames, SettingOptions, TableActions, UISearchTypes } from '@/enums'
import { DraftResultIF, RegistrationSummaryIF, RegTableNewItemI } from '@/interfaces'
import { registrationTableHeaders } from '@/resources'
import {
  amendConfirmationDialog,
  dischargeConfirmationDialog,
  registrationFoundDialog,
  renewConfirmationDialog,
  tableDeleteDialog,
  tableRemoveDialog
} from '@/resources/dialogOptions'
import { axios } from '@/utils/axios-ppr'
// unit test data, etc.
import mockRouter from './MockRouter'
import {
  mockedSearchResponse,
  mockedSearchHistory,
  mockedSelectSecurityAgreement,
  mockedRegistration1,
  mockedDraft1,
  mockedFinancingStatementComplete,
  mockedDraftFinancingStatementAll,
  mockedDebtorNames,
  mockedDraftAmend,
  mockedRegistration2,
  mockedUpdateRegTableUserSettingsResponse
} from './test-data'
import { getLastEvent, setupIntersectionObserverMock } from './utils'
import { SessionStorageKeys } from 'sbc-common-components/src/util/constants'
import { defaultFlagSet } from '@/utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Events
const selectedType = 'selected-registration-type'

// selectors
const searchHeader = '#search-header'
const historyHeader = '#search-history-header'
const myRegAddDialog = '#myRegAddDialog'
const myRegDeleteDialog = '#myRegDeleteDialog'
const myRegHeader = '#registration-header'
const myRegAddTextBox = '#my-reg-add'
const myRegTblColSelection = '#column-selection'

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Dashboard component', () => {
  setupIntersectionObserverMock()
  let wrapper: Wrapper<any>
  let sandbox
  const { assign } = window.location
  sessionStorage.setItem('PPR_API_URL', 'mock-url-ppr')
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')

  const regNum = '123456B'
  const draftDocId = 'D0034001'
  const currentAccount = { id: 'test_id' }
  sessionStorage.setItem(SessionStorageKeys.CurrentAccount, JSON.stringify(currentAccount))

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any
    // stub api calls
    sandbox = sinon.createSandbox()
    const getStub = sandbox.stub(axios, 'get')
    const getSearchHistory = getStub.withArgs('search-history?from_ui=true')
    getSearchHistory.returns(new Promise(resolve => resolve({ data: { searches: [] } })))
    const getDraft = getStub.withArgs(`drafts/${draftDocId}`)
    getDraft.returns(new Promise(resolve => resolve({ data: mockedDraftFinancingStatementAll })))
    const getMyRegDrafts = getStub.withArgs('drafts?fromUI=true&sortCriteriaName=startDateTime&sortDirection=desc')
    getMyRegDrafts.returns(new Promise(resolve => resolve({ data: [] })))
    const getMyRegHistory = getStub.withArgs(
      'financing-statements/registrations?collapse=true&pageNumber=1&fromUI' +
        '=true&sortCriteriaName=startDateTime&sortDirection=desc'
    )
    getMyRegHistory.returns(new Promise(resolve => resolve({ data: [] })))
    const getRegistration = getStub.withArgs(`financing-statements/${regNum}`)
    getRegistration.returns(new Promise(resolve => resolve({ data: mockedFinancingStatementComplete })))
    const getDebtorNames = getStub.withArgs(`financing-statements/${regNum}/debtorNames`)
    getDebtorNames.returns(new Promise(resolve => resolve({ data: mockedDebtorNames })))
    const patchStub = sandbox.stub(axios, 'patch')
    const patchUserSettings = patchStub.withArgs('user-profile')
    await store.dispatch('setAuthRoles', [AuthRoles.PUBLIC, 'ppr'])
    await store.dispatch('setUserProductSubscriptionsCodes', [ProductCode.PPR])

    patchUserSettings.returns(new Promise(resolve => resolve({ data: mockedUpdateRegTableUserSettingsResponse })))
    // create a Local Vue and install router on it
    const localVue = createLocalVue()
    localVue.use(Vuetify)
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    await router.push({ name: 'dashboard' })
    wrapper = mount((Dashboard as any), {
      localVue,
      store,
      propsData: { appReady: true },
      router,
      vuetify,
      stubs: {
        SearchHistory: true
      }
    })

    await flushPromises()
  })

  afterEach(() => {
    // window.location.assign = assign
    sandbox.restore()
    wrapper.destroy()
  })

  it('renders Dashboard View with child components', async () => {
    expect(wrapper.findComponent(Dashboard).exists()).toBe(true)
    expect(wrapper.findComponent(SearchBar).exists()).toBe(true)
    expect(wrapper.findComponent(SearchHistory).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationBar).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    expect(wrapper.findComponent(Dashboard).exists()).toBe(true)
    // fee settings set correctly based on store
    expect(wrapper.vm.$store.state.stateModel.userInfo.feeSettings).toBeNull()
    expect(wrapper.findComponent(SearchBar).vm.$props.isNonBillable).toBe(false)
    expect(wrapper.findComponent(SearchBar).vm.$props.serviceFee).toBe(1.5)
    // update fee settings and check search bar updates
    wrapper.vm.$store.state.stateModel.userInfo.feeSettings = {
      isNonBillable: true,
      serviceFee: 1
    }
    await flushPromises()
    expect(wrapper.findComponent(SearchBar).vm.$props.isNonBillable).toBe(true)
    expect(wrapper.findComponent(SearchBar).vm.$props.serviceFee).toBe(1)
    // dialogs
    expect(wrapper.find(myRegAddDialog).exists()).toBe(true)
    expect(wrapper.find(myRegAddDialog).vm.$props.setDisplay).toBe(false)
    expect(wrapper.find(myRegDeleteDialog).exists()).toBe(true)
    expect(wrapper.find(myRegDeleteDialog).vm.$props.setDisplay).toBe(false)
    expect(wrapper.findComponent(RegistrationConfirmation).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationConfirmation).vm.$props.display).toBe(false)
    expect(wrapper.findComponent(BaseSnackbar).exists()).toBe(true)
    expect(wrapper.findComponent(BaseSnackbar).vm.$props.toggleSnackbar).toBe(false)
  })

  it('displays the search header', async () => {
    const header = wrapper.findAll(searchHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('Personal Property Registry Search')

    defaultFlagSet['mhr-ui-enabled'] = true
    await store.dispatch('setAuthRoles', [AuthRoles.STAFF, AuthRoles.MHR, AuthRoles.PPR])
    await expect(header.at(0).text()).toContain('Manufactured Home and Personal Property Registries Search')
  })

  it('displays default search history header', () => {
    expect(store.getters.getSearchHistory).toEqual({ searches: [] })
    expect(wrapper.vm.searchHistoryLength).toBe(0)
    const header = wrapper.findAll(historyHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('Searches (0)')
  })

  it('updates the search history header based on history data', async () => {
    expect(store.getters.getSearchHistoryLength).toBe(0)
    await store.dispatch('setSearchHistory', mockedSearchHistory.searches)
    await flushPromises()
    expect(store.getters.getSearchHistory?.length).toBe(6)
    expect(store.getters.getSearchHistoryLength).toBe(6)
    expect(wrapper.vm.searchHistoryLength).toBe(6)
    const header = wrapper.findAll(historyHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('Searches (6)')
    // snackbar should trigger
    expect(wrapper.findComponent(BaseSnackbar).exists()).toBe(true)
    expect(wrapper.findComponent(BaseSnackbar).vm.$props.toggleSnackbar).toBe(true)
    expect(wrapper.findComponent(BaseSnackbar).vm.$props.setMessage).toBe(
      'Your search was successfully added to your table.'
    )
  })

  it('routes to search after getting a search response', async () => {
    wrapper.vm.saveResults(mockedSearchResponse[UISearchTypes.SERIAL_NUMBER])
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe('search')
  })

  it('routes to new registration after selecting registration type', async () => {
    wrapper.findComponent(RegistrationBar).vm.$emit(selectedType, mockedSelectSecurityAgreement)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.LENGTH_TRUST)
  })

  it('completes the beginning of discharge flow', async () => {
    // emit discharge action
    wrapper.findComponent(RegistrationTable).vm.$emit('action', { action: TableActions.DISCHARGE, regNum: regNum })
    await flushPromises()
    // dialog shows
    expect(wrapper.findComponent(RegistrationConfirmation).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationConfirmation).vm.$props.display).toBe(true)
    expect(wrapper.findComponent(RegistrationConfirmation).vm.$props.options).toEqual(dischargeConfirmationDialog)
    expect(wrapper.findComponent(RegistrationConfirmation).vm.$props.registrationNumber).toBe(regNum)
    // emit proceed to discharge
    wrapper.findComponent(RegistrationConfirmation).vm.$emit('proceed', true)
    await flushPromises()
    // goes to review discharge page
    expect(wrapper.vm.$route.name).toBe(RouteNames.REVIEW_DISCHARGE)
  })

  it('completes the beginning of renew flow', async () => {
    // emit renew action
    wrapper.findComponent(RegistrationTable).vm.$emit('action', { action: TableActions.RENEW, regNum: regNum })
    await flushPromises()
    // dialog shows
    expect(wrapper.findComponent(RegistrationConfirmation).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationConfirmation).vm.$props.display).toBe(true)
    expect(wrapper.findComponent(RegistrationConfirmation).vm.$props.options).toEqual(renewConfirmationDialog)
    expect(wrapper.findComponent(RegistrationConfirmation).vm.$props.registrationNumber).toBe(regNum)
    // emit proceed to renew
    wrapper.findComponent(RegistrationConfirmation).vm.$emit('proceed', true)
    // goes to renew page
    expect(wrapper.vm.$route.name).toBe(RouteNames.RENEW_REGISTRATION)
  })

  it('completes the beginning of new amend flow', async () => {
    // emit amend action
    wrapper.findComponent(RegistrationTable).vm.$emit('action', { action: TableActions.AMEND, regNum: regNum })
    await flushPromises()
    // dialog shows
    expect(wrapper.findComponent(RegistrationConfirmation).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationConfirmation).vm.$props.display).toBe(true)
    expect(wrapper.findComponent(RegistrationConfirmation).vm.$props.options).toEqual(amendConfirmationDialog)
    expect(wrapper.findComponent(RegistrationConfirmation).vm.$props.registrationNumber).toBe(regNum)
    // emit proceed to amend
    wrapper.findComponent(RegistrationConfirmation).vm.$emit('proceed', true)
    // goes to amend page
    expect(wrapper.vm.$route.name).toBe(RouteNames.AMEND_REGISTRATION)
  })

  it('routes to edit financing statement after table emits edit draft action', async () => {
    wrapper.findComponent(RegistrationTable).vm.$emit('action', { action: TableActions.EDIT_NEW, docId: draftDocId })
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.LENGTH_TRUST)
  })

  it('routes to edit amendment statement after table emits edit amend action', async () => {
    wrapper
      .findComponent(RegistrationTable)
      .vm.$emit('action', { action: TableActions.EDIT_AMEND, docId: draftDocId, regNum: regNum })
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.AMEND_REGISTRATION)
  })
})

describe('Dashboard error modal tests', () => {
  setupIntersectionObserverMock()
  let wrapper: Wrapper<any>
  let sandbox
  const { assign } = window.location
  const myRegAdd: RegistrationSummaryIF = mockedRegistration1
  sessionStorage.setItem('PPR_API_URL', 'mock-url-ppr')
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    const getStub = sandbox.stub(axios, 'get')
    const getSearchHistory = getStub.withArgs('search-history?from_ui=true')
    getSearchHistory.returns(new Promise(resolve => resolve({ data: { searches: [] } })))
    const getMyRegDrafts = getStub.withArgs('drafts?fromUI=true&sortCriteriaName=startDateTime&sortDirection=desc')
    getMyRegDrafts.returns(new Promise(resolve => resolve({ data: [] })))
    const getMyRegHistory = getStub.withArgs(
      'financing-statements/registrations?collapse=true&pageNumber=1&fromUI' +
        '=true&sortCriteriaName=startDateTime&sortDirection=desc'
    )
    getMyRegHistory.returns(new Promise(resolve => resolve({ data: [mockedRegistration2] })))

    const getMyRegAdd = getStub.withArgs(`financing-statements/registrations/${myRegAdd.baseRegistrationNumber}`)
    getMyRegAdd.returns(new Promise(resolve => resolve({ data: myRegAdd })))

    const postMyRegAdd = sandbox
      .stub(axios, 'post')
      .withArgs(`financing-statements/registrations/${myRegAdd.baseRegistrationNumber}`)
    postMyRegAdd.returns(new Promise(resolve => resolve({ data: myRegAdd })))
    // patch stubs
    const patchStub = sandbox.stub(axios, 'patch')
    const patchUserSettings = patchStub.withArgs('user-profile')
    patchUserSettings.returns(new Promise(resolve => resolve({ data: mockedUpdateRegTableUserSettingsResponse })))

    const localVue = createLocalVue()
    localVue.use(Vuetify)
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    await router.push({ name: 'dashboard' })
    wrapper = shallowMount((Dashboard as any), { localVue, store, propsData: { appReady: true }, router, vuetify })
    await flushPromises()
  })

  afterEach(() => {
    window.location.assign = assign
    sandbox.restore()
    wrapper.destroy()
  })

  it('emits error for search', async () => {
    const error = { statusCode: 404 }
    expect(getLastEvent(wrapper, 'error')).not.toEqual(error)
    wrapper.findComponent(SearchBar).vm.$emit('search-error', error)
    await flushPromises()
    expect(getLastEvent(wrapper, 'error')).toEqual(error)
  })

  it('emits error for search pdf', async () => {
    const error = { statusCode: 404 }
    expect(getLastEvent(wrapper, 'error')).not.toEqual(error)
    wrapper.findComponent(SearchHistory).vm.$emit('error', error)
    await flushPromises()
    expect(getLastEvent(wrapper, 'error')).toEqual(error)
  })
})
