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
  CertifyInformation,
  StickyContainer
} from '@/components/common'
import { BaseDialog } from '@/components/dialogs'
import { RegisteringPartyChange } from '@/components/parties/party'
// ppr enums/utils/etc.
import { RouteNames } from '@/enums'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { StateModelIF } from '@/interfaces'
import { axios } from '@/utils/axios-ppr'
// test mocks/data
import mockRouter from './MockRouter'
import { mockedDebtorNames, mockedDischargeResponse, mockedFinancingStatementAll, mockedPartyCodeSearchResults } from './test-data'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

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
    // store setup
    await store.dispatch('setRegistrationConfirmDebtorName', mockedDebtorNames[0])
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

  it('renders Confirm Registration View with child components', () => {
    expect(wrapper.findComponent(ConfirmDischarge).exists()).toBe(true)
    expect(wrapper.findComponent(CautionBox).exists()).toBe(true)
    expect(wrapper.findComponent(CautionBox).vm.setMsg).toContain(
      'provide the verification statement to all Secured Parties')
    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_DISCHARGE)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)
    const state = wrapper.vm.$store.state.stateModel as StateModelIF
    // check registering party
    expect(state.registration.parties.registeringParty).toBe(null)
    expect(wrapper.findComponent(RegisteringPartyChange).exists()).toBe(true)
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
    expect(wrapper.findComponent(StickyContainer).vm.$props.setSubmitBtn).toBe('Register Total Discharge')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setFeeType).toBe(FeeSummaryTypes.DISCHARGE)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setErrMsg).toBe('')
    // folio
    expect(wrapper.findComponent(FolioNumberSummary).exists()).toBe(true)
    // dialog
    expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)
    // certify
    expect(wrapper.findComponent(CertifyInformation).exists()).toBe(true)
  })

  it('processes back button action', async () => {
    await wrapper.findComponent(StickyContainer).vm.$emit('back', true)
    expect(wrapper.vm.$route.name).toBe(RouteNames.REVIEW_DISCHARGE)
  })

  it('processes cancel button action', async () => {
    // setup
    await wrapper.vm.$store.dispatch('setUnsavedChanges', true)
    // dialog doesn't start visible
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(false)
    // pressing cancel triggers dialog
    await wrapper.findComponent(StickyContainer).vm.$emit('cancel', true)
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(true)
    // if dialog emits proceed false it closes + stays on page
    await wrapper.findComponent(BaseDialog).vm.$emit('proceed', true)
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(false)
    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_DISCHARGE)
    // if dialog emits proceed true it goes to dashboard
    await wrapper.findComponent(StickyContainer).vm.$emit('cancel', true)
    await wrapper.findComponent(BaseDialog).vm.$emit('proceed', false)
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(false)
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })

  it('updates validity from checkboxes', async () => {
    expect(wrapper.vm.$data.validConfirm).toBe(false)
    await wrapper.findComponent(DischargeConfirmSummary).vm.$emit('valid', true)
    expect(wrapper.vm.$data.validConfirm).toBe(true)
  })

  it('updates validity from certify', async () => {
    expect(wrapper.vm.$data.validCertify).toBe(false)
    await wrapper.findComponent(CertifyInformation).vm.$emit('certifyValid', true)
    expect(wrapper.vm.$data.validCertify).toBe(true)
  })

  it('shows validation errors when needed when submitting', async () => {
    await wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
    expect(wrapper.findComponent(DischargeConfirmSummary).vm.setShowErrors).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setErrMsg).toBe('< Please complete required information')
    // msgs go away when validation changes
    await wrapper.findComponent(DischargeConfirmSummary).vm.$emit('valid', true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setErrMsg).toBe('')
  })

  it('shows errors when folio is invalid', async () => {
    await wrapper.findComponent(FolioNumberSummary).vm.$emit('folioValid', false)
    // need to wait 2 secs so throttle is done
    setTimeout(async () => {
      await wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
      // turn show errors on when invalid
      expect(wrapper.vm.$data.showErrors).toBe(true)
    }, 2000)
  })

  it('processes submit button action', async () => {
    // Set up for valid discharge request
    await store.dispatch('setRegistrationNumber', '023001B')
    await store.dispatch('setFolioOrReferenceNumber', 'A-00000402')
    const state = wrapper.vm.$store.state.stateModel as StateModelIF
    const parties = state.registration.parties
    parties.registeringParty = mockedPartyCodeSearchResults[0]
    await store.dispatch('setAddSecuredPartiesAndDebtors', parties)

    await wrapper.findComponent(DischargeConfirmSummary).vm.$emit('valid', true)
    await wrapper.findComponent(CertifyInformation).vm.$emit('certifyValid', true)
    // need to wait 2 secs so throttle is done
    setTimeout(async () => {
      await wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
      await flushPromises()
      expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
      // new dishcarge registration is in store regTableData
      expect(wrapper.vm.$store.state.stateModel.regTableData.addedReg).toBe(mockedDischargeResponse.dischargeRegistrationNumber)
      expect(wrapper.vm.$store.state.stateModel.regTableData.addedRegParent).toBe(mockedDischargeResponse.baseRegistrationNumber)
    }, 2000)
  })
})
