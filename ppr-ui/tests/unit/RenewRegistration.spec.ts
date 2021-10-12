// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { createLocalVue, shallowMount, mount } from '@vue/test-utils'
import sinon from 'sinon'
// Components
import { RenewRegistration } from '@/views'
import { Collateral } from '@/components/collateral'
import { RegistrationLengthTrust, RegistrationRepairersLien } from '@/components/registration'
import { CourtOrder, StickyContainer } from '@/components/common'
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
import { mockedDebtorNames, mockedFinancingStatementAll, mockedFinancingStatementRepairers } from './test-data'
import flushPromises from 'flush-promises'
import { FeeSummaryTypes } from '@/composables/fees/enums'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()
let sandbox
const { assign } = window.location

// Input field selectors / buttons

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Renew registration component', () => {
  let wrapper: any
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')

  beforeEach(async () => {
    delete window.location
    window.location = { assign: jest.fn() } as any
    // setup store values
    await store.dispatch('setRegistrationConfirmDebtorName', mockedDebtorNames[0])
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
      name: RouteNames.RENEW_REGISTRATION,
      query: { 'reg-num': '123456B' }
    })
    wrapper = shallowMount(RenewRegistration, { localVue, store, router, vuetify })
    wrapper.setProps({ appReady: true })
    await flushPromises()
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
    sandbox.restore()
  })

  it('renders Renew Registration View with child components', async () => {
    expect(wrapper.findComponent(RenewRegistration).exists()).toBe(true)
    expect(wrapper.vm.$route.name).toBe(RouteNames.RENEW_REGISTRATION)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)
    const state = wrapper.vm.$store.state.stateModel as StateModelIF
    // check length trust summary
    expect(state.registration.lengthTrust.lifeInfinite).toBe(mockedFinancingStatementAll.lifeInfinite)
    // should start off null
    expect(state.registration.lengthTrust.lifeYears).toBe(null)
    expect(state.registration.lengthTrust.trustIndenture).toBe(mockedFinancingStatementAll.trustIndenture)
    expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
    // check registering party
    expect(state.registration.parties.registeringParty).toBe(mockedFinancingStatementAll.registeringParty)
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
    expect(wrapper.findComponent(StickyContainer).vm.$props.setFeeType).toBe(FeeSummaryTypes.RENEW)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationLength).toEqual({
      lifeInfinite: mockedFinancingStatementAll.lifeInfinite,
      // set life years to 0 so user has to choose
      lifeYears: 0
    })
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setBackBtn).toBe('')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setCancelBtn).toBe('Cancel')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setSubmitBtn).toBe('Confirm and Complete')
  })

  it('processes cancel button action', async () => {
    wrapper.find(StickyContainer).vm.$emit('cancel', true)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })

  it('processes submit button action', async () => {
    await store.dispatch('setLengthTrust', {
      valid: true,
      trustIndenture: false,
      lifeInfinite: false,
      lifeYears: 1,
      showInvalid: false
    })
    wrapper.vm.registrationValid = true
    wrapper.find(StickyContainer).vm.$emit('submit', true)
    await flushPromises()

    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_RENEWAL)
  })

  
  it('doesnt proceed if validation errors', async () => {
    wrapper.vm.registrationValid = false
    wrapper.find(StickyContainer).vm.$emit('submit', true)
    await flushPromises()
    expect(wrapper.vm.showInvalid).toBe(true)
  })
})


describe('Renew registration component for repairers lien', () => {
  let wrapper: any
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')

  beforeEach(async () => {
    delete window.location
    window.location = { assign: jest.fn() } as any
    // setup store values
    await store.dispatch('setRegistrationConfirmDebtorName', mockedDebtorNames[0])
    // stub api call
    sandbox = sinon.createSandbox()
    const get = sandbox.stub(axios, 'get')
    get.returns(new Promise(resolve => resolve({
      data: { ...mockedFinancingStatementRepairers }
    })))
    // create a Local Vue and install router on it
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    await router.push({
      name: RouteNames.RENEW_REGISTRATION,
      query: { 'reg-num': '123456B' }
    })
    wrapper = shallowMount(RenewRegistration, { localVue, store, router, vuetify })
    wrapper.setProps({ appReady: true })
    await flushPromises()
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
    sandbox.restore()
  })

  it('renders Renew Registration View with child components', async () => {
    expect(wrapper.findComponent(RenewRegistration).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationRepairersLien).exists()).toBe(true)
    expect(wrapper.findComponent(CourtOrder).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationLength).toEqual({
      lifeInfinite: false,
     lifeYears: 1
    })
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setBackBtn).toBe('')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setCancelBtn).toBe('Cancel')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setSubmitBtn).toBe('Confirm and Complete')
  })

  
  it('proceeds if valid court order', async () => {
    wrapper.find(CourtOrder).vm.$emit('setCourtOrderValid', true)
    await flushPromises()
    expect(wrapper.vm.registrationValid).toBe(true)
  })

  
  it('doesnt proceed if validation errors', async () => {
    wrapper.find(CourtOrder).vm.$emit('setCourtOrderValid', false)
    wrapper.find(StickyContainer).vm.$emit('submit', true)
    await flushPromises()
    expect(wrapper.vm.showInvalid).toBe(true)
  })
})
