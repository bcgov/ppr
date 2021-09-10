// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import sinon from 'sinon'
// Components
import { RenewRegistration } from '@/views'
import { Collateral } from '@/components/collateral'
import { RegistrationLengthTrust } from '@/components/registration'
import { ButtonsStacked } from '@/components/common'
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

describe('Renew registration component', () => {
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
    expect(state.registration.lengthTrust.lifeYears).toBe(mockedFinancingStatementAll.lifeYears)
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
    // check fee summary (whether data for it is in store or by prop may change)
    // FUTURE: add during renew fee summary ticket
    expect(wrapper.findComponent(ButtonsStacked).exists()).toBe(true)
  })

  it('processes cancel button action', async () => {
    wrapper.find(ButtonsStacked).vm.$emit('cancel', true)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })

  it('processes submit button action', async () => {
    wrapper.find(ButtonsStacked).vm.$emit('submit', true)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_RENEWAL)
  })
})
