// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import sinon from 'sinon'
// Components
import { ConfirmDischarge } from '@/views'
import { ButtonsStacked, CautionBox, DischargeConfirmSummary, RegistrationFee } from '@/components/common'
import { RegisteringPartySummary } from '@/components/parties/summaries'
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
const back = '#btn-stacked-back'
const cancel = '#btn-stacked-cancel'
const submit = '#btn-stacked-submit'

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('ConfirmDischarge registration view', () => {
  let wrapper: any
  let sandbox
  const { assign } = window.location
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')
  const regNum = '123456B'

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
      name: RouteNames.CONFIRM_DISCHARGE,
      query: { 'reg-num': regNum }
    })
    wrapper = shallowMount(ConfirmDischarge, { localVue, store, router, vuetify })
    wrapper.setProps({ appReady: true })
    await flushPromises()
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
    sandbox.restore()
  })

  it('renders Confirm Registration View with child components', async () => {
    expect(wrapper.findComponent(ConfirmDischarge).exists()).toBe(true)
    expect(wrapper.findComponent(CautionBox).exists()).toBe(true)
    expect(wrapper.findComponent(CautionBox).vm.setMsg).toContain(
      'will receive a copy of the Total Discharge Verification Statement.')
    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_DISCHARGE)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)
    const state = wrapper.vm.$store.state.stateModel as StateModelIF
    // check registering party
    expect(state.registration.parties.registeringParty).toBe(mockedFinancingStatementAll.registeringParty)
    expect(wrapper.findComponent(RegisteringPartySummary).exists()).toBe(true)
    // check confirm discharge section
    expect(wrapper.findComponent(DischargeConfirmSummary).exists()).toBe(true)
    expect(wrapper.findComponent(DischargeConfirmSummary).vm.setRegNum).toContain(regNum)
    expect(wrapper.findComponent(DischargeConfirmSummary).vm.setRegType).toContain(state.registration.registrationType.registrationTypeUI)
    expect(wrapper.findComponent(DischargeConfirmSummary).vm.setCollateralSummary).toBe('General Collateral and 2 Vehicles')
    expect(wrapper.findComponent(DischargeConfirmSummary).vm.setShowErrors).toBe(false)
    // check fee summary (whether data for it is in store or by prop may change)
    expect(state.feeSummary.feeAmount).toBe(0)
    expect(state.feeSummary.feeCode).toBe('')
    expect(wrapper.findComponent(RegistrationFee).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationFee).vm.registrationType).toBe('Total Discharge')
    // buttons
    expect(wrapper.findComponent(ButtonsStacked).exists()).toBe(true)
  })

  it('processes back button action', async () => {
    wrapper.findComponent(ButtonsStacked).vm.$emit('back', true)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.REVIEW_DISCHARGE)
  })

  it('processes cancel button action', async () => {
    await wrapper.findComponent(ButtonsStacked).vm.$emit('cancel', true)
    // fill in with the rest of the flow once built
  })

  it('updates validity from checkboxes', async () => {
    expect(wrapper.vm.$data.validConfirm).toBe(false)
    await wrapper.findComponent(DischargeConfirmSummary).vm.$emit('valid', true)
    expect(wrapper.vm.$data.validConfirm).toBe(true)
  })

  it('shows validation errors when needed when submitting', async () => {
    await wrapper.findComponent(ButtonsStacked).vm.$emit('submit', true)
    expect(wrapper.findComponent(DischargeConfirmSummary).vm.setShowErrors).toBe(true)
  })

  it('processes submit button action', async () => {
    await wrapper.findComponent(DischargeConfirmSummary).vm.$emit('valid', true)
    await wrapper.findComponent(ButtonsStacked).vm.$emit('submit', true)
    // fill in with the rest of the flow once built
  })
})
