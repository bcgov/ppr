import { useStore } from '@/store/store'
import flushPromises from 'flush-promises'
import { Dashboard } from '@/views'
import { BaseSnackbar } from '@/components/common'
import { RegistrationConfirmation } from '@/components/dialogs'
import { SearchBar } from '@/components/search'
import { RegistrationTable, SearchHistory } from '@/components/tables'
import { RegistrationBar } from '@/components/registration'
import { AuthRoles, ProductCode, RouteNames, TableActions, UISearchTypes } from '@/enums'
import {
  amendConfirmationDialog,
  dischargeConfirmationDialog,
  renewConfirmationDialog
} from '@/resources/dialogOptions'
import {
  mockedSearchResponse,
  mockedSearchHistory,
  mockedSelectSecurityAgreement,
  mockedRegistration1,
  mockedDraftFinancingStatementAll,
  mockedDebtorNames,
  mockedUpdateRegTableUserSettingsResponse,
  mockedManufacturerAuthRoles
} from './test-data'
import { createComponent, getLastEvent } from './utils'
import { defaultFlagSet } from '@/utils'
import { DashboardTabs } from '@/components/dashboard'
import { vi } from 'vitest'
import { nextTick } from 'vue'

const store = useStore()

// Events
const selectedType = 'selectedRegistrationType'

// selectors
const regNum = '123456B'
const draftDocId = 'D0034001'
const searchHeader = '#search-header'
const historyHeader = '#search-history-header'

vi.mock('@/utils/ppr-api-helper', () => ({
  searchHistory: vi.fn(() =>
    Promise.resolve({ searches: [] })),
  getDraft: vi.fn(() =>
    Promise.resolve({ ...mockedDraftFinancingStatementAll })),
  draftHistory: vi.fn(() =>
    Promise.resolve([mockedDraftFinancingStatementAll])),
  registrationHistory: vi.fn(() =>
    Promise.resolve({ ...mockedRegistration1 })),
  updateUserSettings: vi.fn(() =>
    Promise.resolve({ ...mockedUpdateRegTableUserSettingsResponse })),
  debtorNames: vi.fn(() =>
    Promise.resolve(mockedDebtorNames))
}))

describe('Dashboard component', () => {
  let wrapper

  beforeAll(() => {
    defaultFlagSet['mhr-registration-enabled'] = true
    defaultFlagSet['mhr-ui-enabled'] = true
  })

  afterAll(() => {
    defaultFlagSet['mhr-registration-enabled'] = false
    defaultFlagSet['mhr-ui-enabled'] = false
  })

  beforeEach(async () => {
    await store.setAuthRoles([AuthRoles.PUBLIC, 'ppr'])
    await store.setUserProductSubscriptionsCodes([ProductCode.PPR])
    wrapper = await createComponent(Dashboard, { appReady: true })

    await flushPromises()
  })

  it('renders Dashboard View with child components', async () => {
    expect(wrapper.findComponent(Dashboard).exists()).toBe(true)
    expect(wrapper.findComponent(SearchBar).exists()).toBe(true)
    expect(wrapper.findComponent(SearchHistory).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationBar).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    // fee settings set correctly based on store
    expect(store.getStateModel.userInfo.feeSettings).toBeNull()
    expect(wrapper.findComponent(SearchBar).vm.$props.isNonBillable).toBe(false)
    expect(wrapper.findComponent(SearchBar).vm.$props.serviceFee).toBe(1.5)
    // update fee settings and check search bar updates
    store.getStateModel.userInfo.feeSettings = {
      isNonBillable: true,
      serviceFee: 1
    }
    await flushPromises()
    expect(wrapper.findComponent(SearchBar).vm.$props.isNonBillable).toBe(true)
    expect(wrapper.findComponent(SearchBar).vm.$props.serviceFee).toBe(1)
    // dialogs should not show
    expect(wrapper.findComponent(BaseSnackbar).exists()).toBe(true)
    expect(wrapper.findComponent(BaseSnackbar).vm.$props.toggleSnackbar).toBe(false)
  })

  it('displays the search header', async () => {
    const header = wrapper.findAll(searchHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('Personal Property Registry Search')
  })

  it('displays default search history header', () => {
    expect(store.getSearchHistory).toEqual([])
    expect(wrapper.vm.searchHistoryLength).toBe(0)
    const header = wrapper.findAll(historyHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('Searches (0)')
  })

  it('updates the search history header based on history data', async () => {
    expect(store.getSearchHistoryLength).toBe(0)
    await store.setSearchHistory(mockedSearchHistory.searches)
    await flushPromises()
    expect(store.getSearchHistory?.length).toBe(6)
    expect(store.getSearchHistoryLength).toBe(6)
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
    await nextTick()
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

  it('Renders dashboard with only MHR table for manufacturer with MHR product and Manufacturer', async () => {
    // setup
    await store.setAuthRoles(mockedManufacturerAuthRoles)
    await store.setUserProductSubscriptionsCodes([ProductCode.MHR, ProductCode.MANUFACTURER])

    // Test
    expect(wrapper.findComponent(Dashboard).exists()).toBe(true)
    expect(wrapper.findComponent(SearchBar).exists()).toBe(true)
    expect(wrapper.findComponent(SearchHistory).exists()).toBe(true)
    expect(wrapper.findComponent(DashboardTabs).exists()).toBe(false)
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationTable).vm.$props.isMhr).toBe(true)
    expect(wrapper.findComponent(RegistrationBar).exists()).toBe(true)
  })
})

// These tests PASS as they emit the errors successfully, but the errors pollute the terminal output.
// describe('Dashboard error modal tests', () => {
//   let wrapper
//
//   beforeEach(async () => {
//     wrapper = await createComponent(Dashboard, { appReady: true })
//
//     await flushPromises()
//   })
//
//   it('emits error for search', async () => {
//     const error = { statusCode: 404 }
//     expect(getLastEvent(wrapper, 'error')).not.toEqual(error)
//     wrapper.findComponent(SearchBar).vm.$emit('searchError', error)
//     await flushPromises()
//     expect(getLastEvent(wrapper, 'error')).toEqual(error)
//   })
//
//   it('emits error for search pdf', async () => {
//     const error = { statusCode: 404 }
//     expect(getLastEvent(wrapper, 'error')).not.toEqual(error)
//     wrapper.findComponent(SearchHistory).vm.$emit('error', error)
//     await flushPromises()
//     expect(getLastEvent(wrapper, 'error')).toEqual(error)
//   })
// })
