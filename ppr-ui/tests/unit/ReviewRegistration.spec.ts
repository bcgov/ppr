// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import sinon from 'sinon'
import flushPromises from 'flush-promises'
// Components
import { ReviewRegistration } from '@/views'
import { Collateral } from '@/components/collateral'
import { RegistrationLengthTrustSummary } from '@/components/registration'
import { CautionBox, StickyContainer } from '@/components/common'
import { BaseDialog } from '@/components/dialogs'
import {
  DebtorSummary,
  RegisteringPartySummary,
  SecuredPartySummary
} from '@/components/parties/summaries'
// ppr enums/utils/etc.
import { RouteNames } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { StateModelIF } from '@/interfaces'
import { axios } from '@/utils/axios-ppr'
// test mocks/data
import mockRouter from './MockRouter'
import { mockedDebtorNames, mockedFinancingStatementAll } from './test-data'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('ReviewConfirm new registration component', () => {
  let wrapper: any
  let sandbox
  const { assign } = window.location
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')

  beforeEach(async () => {
    delete window.location
    window.location = { assign: jest.fn() } as any
    // setup store values
    await store.setRegistrationConfirmDebtorName(mockedDebtorNames[0])
    // stub api call
    sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'get')
    get.returns(new Promise(resolve => resolve({
      data: { ...mockedFinancingStatementAll }
    })))
    // create a Local Vue and install router on it
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    await router.push({
      name: RouteNames.REVIEW_DISCHARGE,
      query: { 'reg-num': '123456B' }
    })
    wrapper = shallowMount((ReviewRegistration as any), { localVue, store, router, vuetify })
    wrapper.setProps({ appReady: true })
    await flushPromises()
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
    sandbox.restore()
  })

  it('renders Review Registration View with child components', async () => {
    expect(wrapper.findComponent(ReviewRegistration).exists()).toBe(true)
    expect(wrapper.findComponent(CautionBox).exists()).toBe(true)
    expect(wrapper.findComponent(CautionBox).vm.setMsg).toContain(
      'provide the verification statement to all Secured Parties')
    expect(wrapper.vm.$route.name).toBe(RouteNames.REVIEW_DISCHARGE)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)
    // wait because store getting set still
    await nextTick()
    const state = store.getStateModel
    // check length trust summary
    expect(state.registration.lengthTrust.lifeInfinite).toBe(mockedFinancingStatementAll.lifeInfinite)
    expect(state.registration.lengthTrust.lifeYears).toBe(mockedFinancingStatementAll.lifeYears)
    expect(state.registration.lengthTrust.trustIndenture).toBe(mockedFinancingStatementAll.trustIndenture)
    expect(wrapper.findComponent(RegistrationLengthTrustSummary).exists()).toBe(true)
    // check registering party
    expect(state.registration.parties.registeringParty).toBe(null)
    expect(state.originalRegistration.parties.registeringParty).toBe(mockedFinancingStatementAll.registeringParty)
    expect(wrapper.findComponent(RegisteringPartySummary).exists()).toBe(true)
    // check secured parties
    expect(state.registration.parties.securedParties).toBe(mockedFinancingStatementAll.securedParties)
    expect(wrapper.findComponent(SecuredPartySummary).exists()).toBe(true)
    // check debtors
    expect(state.registration.parties.debtors).toBe(mockedFinancingStatementAll.debtors)
    expect(wrapper.findComponent(DebtorSummary).exists()).toBe(true)
    // check vehicle collateral
    expect(state.registration.collateral.vehicleCollateral).toBe(mockedFinancingStatementAll.vehicleCollateral)
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    // check fee summary + buttons
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowFeeSummary).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setBackBtn).toBe('')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setCancelBtn).toBe('Cancel')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setSubmitBtn).toBe('Confirm and Complete')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setFeeType).toBe(FeeSummaryTypes.DISCHARGE)
  })

  it('processes cancel button action', async () => {
    wrapper.find(StickyContainer).vm.$emit('cancel', true)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.REVIEW_DISCHARGE)
    expect(wrapper.find(BaseDialog).exists()).toBe(true)
    wrapper.find(BaseDialog).vm.$emit('proceed', false)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })

  it('processes submit button action', async () => {
    wrapper.find(StickyContainer).vm.$emit('submit', true)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_DISCHARGE)
  })
})
