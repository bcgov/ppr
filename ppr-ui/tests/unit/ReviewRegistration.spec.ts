// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { createLocalVue, mount, shallowMount } from '@vue/test-utils'
import sinon from 'sinon'
// Components
import { ReviewRegistration } from '@/views'
import { Collateral } from '@/components/collateral'
import { RegistrationLengthTrust } from '@/components/registration'
import { RegistrationFee } from '@/components/common'
import {
  DebtorSummary,
  RegisteringPartySummary,
  SecuredPartySummary
} from '@/components/parties/summaries'
// ppr enums/utils/etc.
import { RouteNames } from '@/enums'
import { StateModelIF } from '@/interfaces'
import { axios } from '@/utils/axios-ppr'
// test mocks/data
import mockRouter from './MockRouter'
import { mockedFinancingStatementAll } from './test-data'
import flushPromises from 'flush-promises'


Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Input field selectors / buttons

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
    wrapper = shallowMount(ReviewRegistration, { localVue, store, router, vuetify })
    wrapper.setProps({appReady: true})
    await flushPromises()
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
    sandbox.restore()
  })

  it('renders Review Registration View with child components', async () => {
    expect(wrapper.findComponent(ReviewRegistration).exists()).toBe(true)
    expect(wrapper.vm.$route.name).toBe(RouteNames.REVIEW_DISCHARGE)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)
    const state = wrapper.vm.$store.state.stateModel as StateModelIF
    // check length trust summary
    expect(state.lengthTrustStep.lifeInfinite).toBe(mockedFinancingStatementAll.lifeInfinite)
    expect(state.lengthTrustStep.lifeYears).toBe(mockedFinancingStatementAll.lifeYears)
    expect(state.lengthTrustStep.trustIndenture).toBe(mockedFinancingStatementAll.trustIndenture)
    expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
    // check registering party
    expect(state.addSecuredPartiesAndDebtorsStep.registeringParty).toBe(mockedFinancingStatementAll.registeringParty)
    expect(wrapper.findComponent(RegisteringPartySummary).exists()).toBe(true)
    // check secured parties
    expect(state.addSecuredPartiesAndDebtorsStep.securedParties).toBe(mockedFinancingStatementAll.securedParties)
    expect(wrapper.findComponent(SecuredPartySummary).exists()).toBe(true)
    // check debtors
    expect(state.addSecuredPartiesAndDebtorsStep.debtors).toBe(mockedFinancingStatementAll.debtors)
    expect(wrapper.findComponent(DebtorSummary).exists()).toBe(true)
    // check vehicle collateral
    expect(state.addCollateralStep.vehicleCollateral).toBe(mockedFinancingStatementAll.vehicleCollateral)
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    // check fee summary (whether data for it is in store or by prop may change)
    expect(state.feeSummary.feeAmount).toBe(0)
    expect(state.feeSummary.feeCode).toBe('')
    expect(wrapper.findComponent(RegistrationFee).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationFee).vm.registrationType).toBe('Total Discharge')
  })
})

// describe('ReviewConfirm step 1 tests', () => {
//   let wrapper: any
//   const { assign } = window.location

//   beforeEach(async () => {
//     // reset the store data
//     await store.dispatch('resetNewRegistration')
//     const resetDraft:DraftIF = {
//       type: '',
//       financingStatement: null,
//       createDateTime: null,
//       lastUpdateDateTime: null
//     }
//     await store.dispatch('setDraft', resetDraft)
//     await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement)

//     // mock the window.location.assign function
//     delete window.location
//     window.location = { assign: jest.fn() } as any

//     // create a Local Vue and install router on it
//     const localVue = createLocalVue()
//     localVue.use(VueRouter)
//     const router = mockRouter.mock()
//     await router.push({ name: 'review-confirm' })
//     wrapper = shallowMount(ReviewConfirm, { localVue, store, router, vuetify })
//   })

//   afterEach(() => {
//     window.location.assign = assign
//     wrapper.destroy()
//   })

//   it('Review Confirm View with invalid step 1', async () => {
//     const lengthTrust:LengthTrustIF = JSON.parse(JSON.stringify(mockedNewRegStep1))
//     await wrapper.vm.$store.dispatch('setLengthTrust', lengthTrust)
//     expect(wrapper.findComponent(ReviewConfirm).exists()).toBe(true)
//     expect(wrapper.findComponent(Stepper).exists()).toBe(true)
//     expect(wrapper.findComponent(RegistrationFee).exists()).toBe(true)
//     expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
//     expect(wrapper.findComponent(Collateral).exists()).toBe(true)
//     expect(wrapper.findComponent(Parties).exists()).toBe(true)
//     // expect(wrapper.findComponent(RegistrationLengthTrust).isSummary).toBe(true)
//     // expect(wrapper.findComponent(RegistrationLengthTrust).showErrorSummary).toBe(true)
//     // expect(wrapper.findComponent(RegistrationLengthTrust).lengthSummary).toBe('Not entered')
//     // expect(wrapper.findComponent(RegistrationLengthTrust).trustIndentureSummary).toBe('No')
//   })

//   it('Review Confirm View with valid step 1', async () => {
//     const lengthTrust:LengthTrustIF = JSON.parse(JSON.stringify(mockedNewRegStep1))
//     lengthTrust.valid = true
//     lengthTrust.lifeInfinite = false
//     lengthTrust.lifeYears = 3
//     lengthTrust.trustIndenture = true
//     await wrapper.vm.$store.dispatch('setLengthTrust', lengthTrust)
//     expect(wrapper.findComponent(ReviewConfirm).exists()).toBe(true)
//     expect(wrapper.findComponent(Stepper).exists()).toBe(true)
//     expect(wrapper.findComponent(RegistrationFee).exists()).toBe(true)
//     expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
//     expect(wrapper.findComponent(Collateral).exists()).toBe(true)
//     expect(wrapper.findComponent(Parties).exists()).toBe(true)
//     // expect(wrapper.findComponent(RegistrationLengthTrust).isSummary).toBe(true)
//     // expect(wrapper.findComponent(RegistrationLengthTrust).showErrorSummary).toBe(false)
//     // expect(wrapper.findComponent(RegistrationLengthTrust).lengthSummary).toBe('3')
//     // expect(wrapper.findComponent(RegistrationLengthTrust).trustIndentureSummary).toBe('Yes')
//   })
// })
