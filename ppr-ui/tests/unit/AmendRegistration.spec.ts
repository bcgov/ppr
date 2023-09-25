// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import sinon from 'sinon'
// Components
import AmendRegistration from '@/views/amendment/AmendRegistration.vue'
import { Collateral } from '@/components/collateral'
import {
  AmendmentDescription, RegistrationLengthTrustAmendment, RegistrationLengthTrustSummary
} from '@/components/registration'
import { StickyContainer } from '@/components/common'
import { Debtors } from '@/components/parties/debtor'
import { SecuredParties } from '@/components/parties/party'
import { DebtorSummary, RegisteringPartySummary, SecuredPartySummary } from '@/components/parties/summaries'
// ppr enums/utils/etc.
import { ActionTypes, RouteNames } from '@/enums'
import { StateModelIF } from '@/interfaces'
import { axios } from '@/utils/axios-ppr'
// test mocks/data
import mockRouter from './MockRouter'
import {
  mockedDebtorNames,
  mockedDraftAmendmentStatement,
  mockedFinancingStatementAll,
  mockedFinancingStatementRepairers
} from './test-data'
import flushPromises from 'flush-promises'
import { FeeSummaryTypes } from '@/composables/fees/enums'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Amendment registration component', () => {
  let wrapper: any
  let sandbox
  const { assign } = window.location
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')

  beforeEach(async () => {
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
      data: { ...mockedDraftAmendmentStatement }
    })))

    // create a Local Vue and install router on it
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    await router.push({
      name: RouteNames.AMEND_REGISTRATION,
      query: { 'reg-num': '123456B' }
    })
    wrapper = shallowMount(AmendRegistration as any, { localVue, store, router, stubs: { Affix: true }, vuetify })
    wrapper.setProps({ appReady: true })
    await flushPromises()
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
    sandbox.restore()
  })

  it('renders Amend Registration View with child components', async () => {
    expect(wrapper.findComponent(AmendRegistration).exists()).toBe(true)
    expect(wrapper.vm.$route.name).toBe(RouteNames.AMEND_REGISTRATION)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)
    // wait because store getting set still
    await nextTick()
    const state = store.getStateModel
    // check length trust summary
    expect(state.registration.lengthTrust.lifeInfinite).toBe(mockedFinancingStatementAll.lifeInfinite)
    expect(state.registration.lengthTrust.lifeYears).toBe(5)
    expect(state.registration.lengthTrust.trustIndenture).toBe(mockedFinancingStatementAll.trustIndenture)
    expect(wrapper.findComponent(RegistrationLengthTrustAmendment).exists()).toBe(true)
    // check amendment description
    expect(state.registration.amendmentDescription).toBe('')
    expect(wrapper.findComponent(AmendmentDescription).exists()).toBe(true)
    // check registering party
    expect(state.registration.parties.registeringParty).toBe(null)
    expect(state.originalRegistration.parties.registeringParty).toEqual(mockedFinancingStatementAll.registeringParty)
    expect(wrapper.findComponent(RegisteringPartySummary).exists()).toBe(true)
    // check secured parties
    expect(state.registration.parties.securedParties).toEqual(mockedFinancingStatementAll.securedParties)
    expect(wrapper.findComponent(SecuredParties).exists()).toBe(true)
    // check debtors
    expect(state.registration.parties.debtors).toEqual(mockedFinancingStatementAll.debtors)
    expect(wrapper.findComponent(Debtors).exists()).toBe(true)
    // check vehicle collateral
    expect(state.registration.collateral.vehicleCollateral).toEqual(mockedFinancingStatementAll.vehicleCollateral)
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    // check fee summary + buttons
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowFeeSummary).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setFeeType).toBe(FeeSummaryTypes.AMEND)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setBackBtn).toBe('Save and Resume Later')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setCancelBtn).toBe('Cancel')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setSubmitBtn).toBe('Review and Complete')
  })

  it('processes cancel button action', async () => {
    await store.setUnsavedChanges(false)
    await nextTick()
    await wrapper.findComponent(StickyContainer).vm.$emit('cancel', true)
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })

  it('doesnt proceed if validation errors', async () => {
    wrapper.vm.setValidDebtor(false)
    wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
    await flushPromises()
    expect(wrapper.vm.showInvalid).toBe(true)
  })

  it('goes to the confirmation page', async () => {
    wrapper.vm.courtOrderValid = true
    await store.setAmendmentDescription('test12')
    wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_AMENDMENT)
  })

  it('does not go to the confirmation page if component open', async () => {
    wrapper.vm.debtorOpen = true
    await nextTick()
    wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.AMEND_REGISTRATION)
  })

  it('saves the draft and redirects to dashboard', async () => {
    wrapper.findComponent(StickyContainer).vm.$emit('back', true)
    await nextTick()
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })

  it('checks for length trust indenture & court order validity -if valid', async () => {
    await store.setLengthTrust({
      valid: true,
      trustIndenture: true,
      lifeInfinite: false,
      lifeYears: 5,
      showInvalid: false,
      surrenderDate: '',
      lienAmount: '',
      action: ActionTypes.EDITED
    })
    wrapper.vm.courtOrderValid = true
    wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_AMENDMENT)
  })
})

describe('Amendment for repairers lien component', () => {
  let wrapper: any
  let sandbox
  const { assign } = window.location
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')

  beforeEach(async () => {
    delete window.location
    window.location = { assign: jest.fn() } as any
    // stub api call
    sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'get')
    get.returns(new Promise(resolve => resolve({
      data: { ...mockedFinancingStatementRepairers }
    })))

    const post = sandbox.stub(axios, 'post')
    post.returns(new Promise(resolve => resolve({
      data: { ...mockedDraftAmendmentStatement }
    })))

    // create a Local Vue and install router on it
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    await router.push({
      name: RouteNames.AMEND_REGISTRATION,
      query: { 'reg-num': '123456B' }
    })
    wrapper = shallowMount((AmendRegistration as any), { localVue, store, router, vuetify })
    wrapper.setProps({ appReady: true })
    await flushPromises()
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
    sandbox.restore()
  })

  it('renders Amend Registration View with child components', async () => {
    expect(wrapper.findComponent(AmendRegistration).exists()).toBe(true)
    expect(wrapper.vm.$route.name).toBe(RouteNames.AMEND_REGISTRATION)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)
    const state = store.getStateModel
    // check length trust summary
    expect(state.registration.lengthTrust.lifeInfinite).toBe(mockedFinancingStatementAll.lifeInfinite)
    expect(state.registration.lengthTrust.lifeYears).toBe(1)
    expect(state.registration.lengthTrust.trustIndenture).toBe(mockedFinancingStatementAll.trustIndenture)
    expect(wrapper.findComponent(RegistrationLengthTrustAmendment).exists()).toBe(false)
    expect(wrapper.findComponent(RegistrationLengthTrustSummary).exists()).toBe(true)
    // check amendment description
    expect(state.registration.amendmentDescription).toBe('')
    expect(wrapper.findComponent(AmendmentDescription).exists()).toBe(true)
    // check registering party
    expect(state.registration.parties.registeringParty).toBe(null)
    expect(state.originalRegistration.parties.registeringParty).toEqual(mockedFinancingStatementAll.registeringParty)
    expect(wrapper.findComponent(RegisteringPartySummary).exists()).toBe(true)
    // check secured parties
    expect(state.registration.parties.securedParties).toEqual(mockedFinancingStatementAll.securedParties)
    expect(wrapper.findComponent(SecuredPartySummary).exists()).toBe(true)
    // check debtors
    expect(state.registration.parties.debtors).toEqual(mockedFinancingStatementAll.debtors)
    expect(wrapper.findComponent(DebtorSummary).exists()).toBe(true)
    // check vehicle collateral
    expect(state.registration.collateral.vehicleCollateral).toEqual(mockedFinancingStatementAll.vehicleCollateral)
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    // check fee summary + buttons
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowFeeSummary).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setFeeType).toBe(FeeSummaryTypes.AMEND)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setBackBtn).toBe('Save and Resume Later')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setCancelBtn).toBe('Cancel')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setSubmitBtn).toBe('Review and Complete')
  })
})
