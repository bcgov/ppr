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
import { RegistrationsWrapper } from '@/components/common'
import { RegistrationTable } from '@/components/tables'
import { SettingOptions, TableActions } from '@/enums'
import { DraftResultIF, RegistrationSummaryIF, RegTableNewItemI } from '@/interfaces'
import { registrationTableHeaders } from '@/resources'
import {
  registrationFoundDialog,
  tableDeleteDialog,
  tableRemoveDialog
} from '@/resources/dialogOptions'
import { axios } from '@/utils/axios-ppr'
// unit test data, etc.
import mockRouter from './MockRouter'
import {
  mockedRegistration1,
  mockedDraft1,
  mockedDebtorNames,
  mockedDraftAmend,
  mockedRegistration2,
  mockedUpdateRegTableUserSettingsResponse
} from './test-data'
import { setupIntersectionObserverMock } from './utils'

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

describe('Ppr registration table tests', () => {
  setupIntersectionObserverMock()
  let wrapper: Wrapper<any>
  let sandbox
  const { assign } = window.location
  const myRegDrafts: DraftResultIF[] = [{ ...mockedDraft1 }, { ...mockedDraftAmend }]
  const myRegHistory: RegistrationSummaryIF[] = [{ ...mockedRegistration1 }]
  const parentDrafts: DraftResultIF[] = [{ ...mockedDraft1 }]
  // setup baseReg with added child draft
  const baseReg = { ...mockedRegistration1 }
  baseReg.changes = [{ ...mockedDraftAmend }]
  baseReg.expand = false
  const myRegHistoryWithChildren = [baseReg]
  const newColumnSelection = [...registrationTableHeaders].slice(3)

  sessionStorage.setItem('PPR_API_URL', 'mock-url-ppr')
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')

  beforeEach(async () => {
    sandbox = sinon.createSandbox()
    // get stubs
    const getStub = sandbox.stub(axios, 'get')
    const getSearchHistory = getStub.withArgs('search-history?from_ui=true')
    getSearchHistory.returns(new Promise(resolve => resolve({ data: { searches: [] } })))
    const getMyRegDrafts = getStub.withArgs('drafts?fromUI=true&sortCriteriaName=startDateTime&sortDirection=desc')
    getMyRegDrafts.returns(new Promise(resolve => resolve({ data: cloneDeep(myRegDrafts) })))
    const getMyRegHistory = getStub.withArgs('financing-statements/registrations?collapse=true&pageNumber=1&fromUI' +
      '=true&sortCriteriaName=startDateTime&sortDirection=desc')
    getMyRegHistory.returns(new Promise(resolve => resolve({ data: cloneDeep(myRegHistory) })))
    const getDebtorNames = getStub
      .withArgs(`financing-statements/${mockedRegistration1.baseRegistrationNumber}/debtorNames`)
    getDebtorNames.returns(new Promise(resolve => resolve({ data: mockedDebtorNames })))
    // delete stubs
    const deleteStub = sandbox.stub(axios, 'delete')
    deleteStub.returns(new Promise(resolve => resolve({ status: StatusCodes.NO_CONTENT })))
    // patch stubs
    const patchStub = sandbox.stub(axios, 'patch')
    const patchUserSettings = patchStub.withArgs('user-profile')
    patchUserSettings.returns(new Promise(resolve => resolve(
      // error will cause UI to ignore response and use default / whatever the user selected
      { data: { [SettingOptions.REGISTRATION_TABLE]: { columns: newColumnSelection } } }
    )))

    // set base selected columns
    await store.dispatch(
      'setUserInfo',
      {
        settings: {
          [SettingOptions.REGISTRATION_TABLE]: { columns: registrationTableHeaders }
        }
      }
    )

    const localVue = createLocalVue()
    localVue.use(Vuetify)
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    await router.push({ name: 'dashboard' })
    wrapper = mount(RegistrationsWrapper, {
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
    sandbox.restore()
    wrapper.destroy()
  })

  it('displays my registration header and content', () => {
    expect(wrapper.findComponent(RegistrationsWrapper).exists()).toBe(true)
    // myRegDrafts contains a child that will be put into a baseReg
    expect(store.getters.getRegTableDraftsBaseReg).toEqual(parentDrafts)
    expect(store.getters.getRegTableBaseRegs).toEqual(myRegHistoryWithChildren)
    const header = wrapper.findAll(myRegHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain(
      `Registrations (${parentDrafts.length + myRegHistoryWithChildren.length})`
    )
    // expect(wrapper.find(myRegTblFilter).exists()).toBe(true)
    expect(wrapper.find(myRegTblColSelection).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setRegistrationHistory)
      .toEqual([...parentDrafts, ...myRegHistoryWithChildren])
  })

  it('updates the registration table with new headers', async () => {
    // ensure original is based off settings patch stub
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setHeaders).toEqual(registrationTableHeaders)
    // update dashboard headers variable directly
    expect(wrapper.find(myRegTblColSelection).exists()).toBe(true)
    wrapper.vm.$data.myRegHeaders = newColumnSelection
    await flushPromises()
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setHeaders).toEqual(newColumnSelection)
  })

  it('updates the registration table with new headers from column selection', async () => {
    // ensure original selection is based off settings patch stub
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setHeaders).toEqual(registrationTableHeaders)
    // update column selection
    expect(wrapper.find(myRegTblColSelection).exists()).toBe(true)
    wrapper.vm.myRegHeadersSelected = newColumnSelection
    await flushPromises()
    // verify dashboard values updated
    expect(wrapper.vm.myRegHeadersSelected).toEqual(newColumnSelection)
    expect(wrapper.vm.myRegHeaders).toEqual(newColumnSelection)
    // verify store updated with patch response
    expect(wrapper.vm.$store.state.stateModel.userInfo.settings[SettingOptions.REGISTRATION_TABLE].columns)
      .toEqual(newColumnSelection)
    // verify table props updated
    expect(wrapper.findComponent(RegistrationTable).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setHeaders).toEqual(newColumnSelection)
  })

  it('deletes parent drafts', async () => {
    const myRegDraftsCopy = [...parentDrafts]
    // check setup
    expect(store.getters.getRegTableDraftsBaseReg).toEqual(myRegDraftsCopy)
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setRegistrationHistory)
      .toEqual([...myRegDraftsCopy, ...myRegHistoryWithChildren])
    // emit delete action
    wrapper.findComponent(RegistrationTable).vm.$emit(
      'action', { action: TableActions.DELETE, docId: myRegDraftsCopy[0].documentId }
    )
    await flushPromises()
    // dialog shows
    expect(wrapper.find(myRegDeleteDialog).exists()).toBe(true)
    expect(wrapper.find(myRegDeleteDialog).vm.$props.setDisplay).toBe(true)
    expect(wrapper.find(myRegDeleteDialog).vm.$props.setOptions).toEqual(tableDeleteDialog)
    // emit proceed with delete
    wrapper.find(myRegDeleteDialog).vm.$emit('proceed', true)
    await flushPromises()
    // draft is removed from table
    myRegDraftsCopy.shift()
    expect(store.getters.getRegTableDraftsBaseReg).toEqual(myRegDraftsCopy)
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setRegistrationHistory)
      .toEqual([...myRegDraftsCopy, ...myRegHistoryWithChildren])
  })

  it('deletes child drafts', async () => {
    const myRegDraftsCopy = myRegHistoryWithChildren[0].changes[0] as DraftResultIF
    // check setup
    expect(store.getters.getRegTableDraftsBaseReg).toEqual(parentDrafts)
    expect(store.getters.getRegTableBaseRegs).toEqual(myRegHistoryWithChildren)
    expect(store.getters.getRegTableBaseRegs[0].changes[0]).toEqual(myRegDraftsCopy)
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setRegistrationHistory)
      .toEqual([...parentDrafts, ...myRegHistoryWithChildren])
    // emit delete action
    wrapper.findComponent(RegistrationTable).vm.$emit(
      'action',
      {
        action: TableActions.DELETE,
        docId: myRegDraftsCopy.documentId,
        regNum: myRegDraftsCopy.baseRegistrationNumber
      }
    )
    await flushPromises()
    // dialog shows
    expect(wrapper.find(myRegDeleteDialog).exists()).toBe(true)
    expect(wrapper.find(myRegDeleteDialog).vm.$props.setDisplay).toBe(true)
    expect(wrapper.find(myRegDeleteDialog).vm.$props.setOptions).toEqual(tableDeleteDialog)
    // emit proceed with delete
    wrapper.find(myRegDeleteDialog).vm.$emit('proceed', true)
    await flushPromises()
    // draft is removed from table
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setRegistrationHistory)
      .toEqual([...parentDrafts, ...myRegHistory])
  })

  it('removes complete registrations', async () => {
    const myRegHistoryCopy = [...myRegHistoryWithChildren]
    // check setup
    expect(store.getters.getRegTableBaseRegs).toEqual(myRegHistoryCopy)
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setRegistrationHistory)
      .toEqual([...parentDrafts, ...myRegHistoryCopy])
    // emit delete action
    expect(wrapper.find(myRegDeleteDialog).exists()).toBe(true)
    wrapper.findComponent(RegistrationTable).vm.$emit(
      'action', { action: TableActions.REMOVE, regNum: myRegHistoryCopy[0].baseRegistrationNumber }
    )
    await flushPromises()
    // dialog shows
    expect(wrapper.find(myRegDeleteDialog).exists()).toBe(true)
    expect(wrapper.find(myRegDeleteDialog).vm.$props.setDisplay).toBe(true)
    expect(wrapper.find(myRegDeleteDialog).vm.$props.setOptions).toEqual(tableRemoveDialog)
    // emit proceed with delete
    wrapper.find(myRegDeleteDialog).vm.$emit('proceed', true)
    await flushPromises()
    // registration is removed from table
    myRegHistoryCopy.shift()
    expect(store.getters.getRegTableBaseRegs).toEqual(myRegHistoryCopy)
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setRegistrationHistory)
      .toEqual([...parentDrafts, ...myRegHistoryCopy])
  })
})

describe('Dashboard add registration tests', () => {
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
    const getMyRegHistory = getStub.withArgs('financing-statements/registrations?collapse=true&pageNumber=1&fromUI' +
      '=true&sortCriteriaName=startDateTime&sortDirection=desc')
    getMyRegHistory.returns(new Promise(resolve => resolve({ data: [mockedRegistration2] })))

    const getMyRegAdd = getStub.withArgs(
      `financing-statements/registrations/${myRegAdd.baseRegistrationNumber}`
    )
    getMyRegAdd.returns(new Promise(resolve => resolve({ data: myRegAdd })))

    const postMyRegAdd = sandbox.stub(axios, 'post').withArgs(
      `financing-statements/registrations/${myRegAdd.baseRegistrationNumber}`
    )
    postMyRegAdd.returns(new Promise(resolve => resolve({ data: myRegAdd })))
    // patch stubs
    const patchStub = sandbox.stub(axios, 'patch')
    const patchUserSettings = patchStub.withArgs('user-profile')
    patchUserSettings.returns(new Promise(resolve => resolve(
      { data: mockedUpdateRegTableUserSettingsResponse }
    )))

    const localVue = createLocalVue()
    localVue.use(Vuetify)
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    await router.push({ name: 'dashboard' })
    wrapper = mount(RegistrationsWrapper, {
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
    wrapper.destroy()
  })

  it('displays the add registration text box + shows dialog + adds it to table', async () => {
    // FUTURE: add all cases (i.e. simulate error flows etc.)
    expect(wrapper.find(myRegAddTextBox).exists()).toBe(true)
    expect(wrapper.vm.myRegAdd).toBe('')
    await wrapper.find(myRegAddTextBox).setValue('123')
    expect(wrapper.vm.myRegAdd).toBe('123')
    expect(wrapper.vm.myRegAddInvalid).toBe(true)
    // set to lowercase to test it gets uppercase reg num
    await wrapper.find(myRegAddTextBox).setValue(myRegAdd.baseRegistrationNumber.toLowerCase())
    expect(wrapper.vm.myRegAddInvalid).toBe(false)
    // simulate add
    await wrapper.find(myRegAddTextBox).trigger('click:append')
    await Vue.nextTick()
    expect(wrapper.vm.loading).toBe(true)
    await flushPromises()
    expect(wrapper.vm.myRegAddDialogDisplay).toBe(true)
    expect(wrapper.vm.loading).toBe(false)
    expect(wrapper.find(myRegAddDialog).exists()).toBe(true)
    expect(wrapper.find(myRegAddDialog).vm.$props.setDisplay).toBe(true)
    expect(wrapper.find(myRegAddDialog).vm.$props.setOptions.text)
      .toContain(registrationFoundDialog.text)
    expect(wrapper.vm.myRegAddDialogError).toBe(null)
    expect(store.getters.getRegTableBaseRegs).toEqual([mockedRegistration2])
    wrapper.find(myRegAddDialog).vm.$emit('proceed', true)
    await flushPromises()
    expect(store.getters.getRegTableBaseRegs).toEqual([myRegAdd, mockedRegistration2])
    expect(wrapper.find(myRegAddDialog).vm.$props.setDisplay).toBe(false)
    expect(wrapper.vm.myRegAdd).toBe('')
    // reg table data updated with new reg
    const expectedRegTableData: RegTableNewItemI = {
      addedReg: myRegAdd.registrationNumber, addedRegParent: '', addedRegSummary: myRegAdd, prevDraft: ''
    }
    expect(wrapper.vm.$store.state.stateModel.registrationTable.newItem).toEqual(expectedRegTableData)
    expect(wrapper.findComponent(RegistrationTable).vm.$props.setNewRegItem).toEqual(expectedRegTableData)
    // reg table data updated with blank values after 5 sec
    const emptyRegTableData: RegTableNewItemI = {
      addedReg: '', addedRegParent: '', addedRegSummary: null, prevDraft: ''
    }
    setTimeout(() => {
      expect(wrapper.vm.$store.state.stateModel.registrationTable.newItem).toEqual(emptyRegTableData)
      expect(wrapper.findComponent(RegistrationTable).vm.$props.setNewRegItem).toEqual(emptyRegTableData)
    }, 5100)
  })
})
