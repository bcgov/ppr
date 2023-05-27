// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import { shallowMount, createLocalVue } from '@vue/test-utils'
import sinon from 'sinon'
import { axios } from '@/utils/axios-ppr'
import {
  mockedFinancingStatementAll,
  mockedDebtorNames,
  mockedRenewalResponse,
  mockedFinancingStatementRepairers,
  mockedPartyCodeSearchResults
} from './test-data'

// Components
import { ConfirmRenewal } from '@/views'
import { FolioNumberSummary, StickyContainer, CertifyInformation, CourtOrder } from '@/components/common'
import { BaseDialog, StaffPaymentDialog } from '@/components/dialogs'
import { RegistrationLengthTrustSummary } from '@/components/registration'

// Other
import mockRouter from './MockRouter'
import { RouteNames } from '@/enums'
import { StateModelIF } from '@/interfaces'
import flushPromises from 'flush-promises'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { RegisteringPartyChange } from '@/components/parties/party'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Confirm Renewal new registration component', () => {
  let wrapper: any
  let sandbox
  const { assign } = window.location
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any
    // store setup
    await store.setRegistrationConfirmDebtorName(mockedDebtorNames[0])
    // stub api call
    sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'get')
    get.returns(new Promise(resolve => resolve({
      data: { ...mockedFinancingStatementAll }
    })))

    const post = sandbox.stub(axios, 'post')
    post.returns(new Promise(resolve => resolve({
      data: { ...mockedRenewalResponse }
    })))

    // create a Local Vue and install router on it
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    await router.push({
      name: RouteNames.CONFIRM_RENEWAL,
      query: { 'reg-num': '123456B' }
    })
    wrapper = shallowMount((ConfirmRenewal as any), { localVue, store, router, vuetify })
    wrapper.setProps({ appReady: true })
    await flushPromises()
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
    sandbox.restore()
  })

  it('renders Review Confirm View with child components', () => {
    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_RENEWAL)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)
    const state = store.getStateModel as StateModelIF

    expect(wrapper.findComponent(ConfirmRenewal).exists()).toBe(true)
    expect(wrapper.findComponent(FolioNumberSummary).exists()).toBe(true)
    // check registering party
    expect(state.registration.parties.registeringParty).toBe(null)
    expect(wrapper.findComponent(RegisteringPartyChange).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationLengthTrustSummary).exists()).toBe(true)
    // check fee summary + buttons
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowFeeSummary).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setBackBtn).toBe('Back')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setCancelBtn).toBe('Cancel')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setSubmitBtn).toBe('Register Renewal and Pay')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setFeeType).toBe(FeeSummaryTypes.RENEW)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setErrMsg).toBe('')
    // dialog
    expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)
    expect(wrapper.findComponent(StaffPaymentDialog).exists()).toBe(true)
    // certify
    expect(wrapper.findComponent(CertifyInformation).exists()).toBe(true)
    expect(wrapper.findComponent(CourtOrder).exists()).toBe(false)
  })

  it('allows back to previous page', async () => {
    expect(wrapper.findComponent(ConfirmRenewal).exists()).toBe(true)
    await wrapper.findComponent(StickyContainer).vm.$emit('back', true)
    expect(wrapper.vm.$route.name).toBe(RouteNames.RENEW_REGISTRATION)
  })

  it('processes cancel button action', async () => {
    // setup
    await store.setUnsavedChanges(true)
    // dialog doesn't start visible
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(false)
    // pressing cancel triggers dialog
    await wrapper.findComponent(StickyContainer).vm.$emit('cancel', true)
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(true)
    // if dialog emits proceed false it closes + stays on page
    await wrapper.findComponent(BaseDialog).vm.$emit('proceed', true)
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(false)
    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_RENEWAL)
    // if dialog emits proceed true it goes to dashboard
    await wrapper.findComponent(StickyContainer).vm.$emit('cancel', true)
    await wrapper.findComponent(BaseDialog).vm.$emit('proceed', false)
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(false)
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })

  it('allows submit of renewal', async () => {
    // Set up for valid discharge request
    await store.setRegistrationNumber('023001B')
    await store.setFolioOrReferenceNumber('A-00000402')
    await store.setRegistrationConfirmDebtorName(mockedDebtorNames[0])
    const state = store.getStateModel as StateModelIF
    const parties = state.registration.parties
    parties.registeringParty = mockedPartyCodeSearchResults[0]
    await store.setAddSecuredPartiesAndDebtors(parties)

    await wrapper.findComponent(CertifyInformation).vm.$emit('certifyValid', true)
    await nextTick()
    await wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
    await nextTick()
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
    // new renew registration is in store regTableData
    expect(store.getStateModel.registrationTable.newItem.addedReg).toBe(
      mockedRenewalResponse.renewalRegistrationNumber
    )
    expect(store.getStateModel.registrationTable.newItem.addedRegParent).toBe(
      mockedRenewalResponse.baseRegistrationNumber
    )
  })
})

describe('Confirm Renewal new RL registration component', () => {
  let wrapper: any
  let sandbox
  const { assign } = window.location
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any
    // store setup
    await store.setRegistrationConfirmDebtorName(mockedDebtorNames[0])
    // stub api call
    sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'get')
    get.returns(new Promise(resolve => resolve({
      data: { ...mockedFinancingStatementRepairers }
    })))

    const post = sandbox.stub(axios, 'post')
    post.returns(new Promise(resolve => resolve({
      data: { ...mockedRenewalResponse }
    })))

    // create a Local Vue and install router on it
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    await router.push({
      name: RouteNames.CONFIRM_RENEWAL,
      query: { 'reg-num': '123456B' }
    })
    wrapper = shallowMount((ConfirmRenewal as any), { localVue, store, router, vuetify })
    wrapper.setProps({ appReady: true })
    await flushPromises()
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
    sandbox.restore()
  })

  it('renders Review Confirm View with child components including court order', () => {
    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_RENEWAL)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)
    expect(wrapper.findComponent(CourtOrder).exists()).toBe(true)
  })
})
