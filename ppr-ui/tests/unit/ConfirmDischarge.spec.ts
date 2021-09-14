// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { createLocalVue, shallowMount } from '@vue/test-utils'
import sinon from 'sinon'
import flushPromises from 'flush-promises'
// Components
import { ConfirmDischarge } from '@/views'
import {
  CautionBox,
  DischargeConfirmSummary,
  FolioNumberSummary,
  StickyContainer
} from '@/components/common'
import { BaseDialog } from '@/components/dialogs'
import { RegisteringPartySummary } from '@/components/parties/summaries'
// ppr enums/utils/etc.
import { RouteNames } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { StateModelIF } from '@/interfaces'
import { axios } from '@/utils/axios-ppr'
// test mocks/data
import mockRouter from './MockRouter'
import { mockedDebtorNames, mockedDischargeResponse, mockedFinancingStatementAll } from './test-data'

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
    const post = sandbox.stub(axios, 'post')
    post.returns(new Promise(resolve => resolve({
      data: { ...mockedDischargeResponse }
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
    // eslint-disable-next-line max-len
    expect(wrapper.findComponent(DischargeConfirmSummary).vm.setRegType).toContain(state.registration.registrationType.registrationTypeUI)
    // eslint-disable-next-line max-len
    expect(wrapper.findComponent(DischargeConfirmSummary).vm.setCollateralSummary).toBe('General Collateral and 2 Vehicles')
    expect(wrapper.findComponent(DischargeConfirmSummary).vm.setShowErrors).toBe(false)
    // check fee summary + buttons
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowFeeSummary).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setBackBtn).toBe('Back')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setCancelBtn).toBe('Cancel')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setSubmitBtn).toBe('Submit Total Discharge')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setFeeType).toBe(FeeSummaryTypes.DISCHARGE)
    // folio
    expect(wrapper.findComponent(FolioNumberSummary).exists()).toBe(true)
  })

  it('processes back button action', async () => {
    wrapper.findComponent(StickyContainer).vm.$emit('back', true)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.REVIEW_DISCHARGE)
  })

  it('processes cancel button action', async () => {
    // dialog doesn't start visible
    expect(wrapper.findComponent(BaseDialog).vm.$props.display).toBe(false)
    // pressing cancel triggers dialog
    await wrapper.findComponent(StickyContainer).vm.$emit('cancel', true)
    expect(wrapper.findComponent(BaseDialog).vm.$props.display).toBe(true)
    // if dialog emits proceed false it closes + stays on page
    await wrapper.findComponent(BaseDialog).vm.$emit('proceed', false)
    expect(wrapper.findComponent(BaseDialog).vm.$props.display).toBe(false)
    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_DISCHARGE)
    // if dialog emits proceed true it goes to dashboard
    await wrapper.findComponent(StickyContainer).vm.$emit('cancel', true)
    await wrapper.findComponent(BaseDialog).vm.$emit('proceed', true)
    expect(wrapper.findComponent(BaseDialog).vm.$props.display).toBe(false)
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })

  it('updates validity from checkboxes', async () => {
    expect(wrapper.vm.$data.validConfirm).toBe(false)
    await wrapper.findComponent(DischargeConfirmSummary).vm.$emit('valid', true)
    expect(wrapper.vm.$data.validConfirm).toBe(true)
  })

  it('shows validation errors when needed when submitting', async () => {
    await wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
    expect(wrapper.findComponent(DischargeConfirmSummary).vm.setShowErrors).toBe(true)
  })

  it('shows errors when folio is invalid', async () => {
    await wrapper.findComponent(FolioNumberSummary).vm.$emit('folioValid', false)
    await wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
    // turn show errors on when invalid
    expect(wrapper.vm.$data.showErrors).toBe(true)
  })

  it('processes submit button action', async () => {
    // Set up for valid discharge request
    await store.dispatch('setRegistrationNumber', '023001B')
    await store.dispatch('setFolioOrReferenceNumber', 'A-00000402')
    await store.dispatch('setRegistrationConfirmDebtorName', mockedDebtorNames[0])

    await wrapper.findComponent(DischargeConfirmSummary).vm.$emit('valid', true)
    await wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })
})
