// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { shallowMount, createLocalVue } from '@vue/test-utils'
import sinon from 'sinon'
import { axios } from '@/utils/axios-ppr'
import { mockedFinancingStatementAll, mockedDebtorNames, mockedRenewalResponse } from './test-data'

// Components
import { ConfirmRenewal } from '@/views'
import { FolioNumberSummary, StickyContainer, CertifyInformation } from '@/components/common'
import { BaseDialog } from '@/components/dialogs'
import { RegistrationLengthTrustSummary } from '@/components/registration'

// Other
import mockRouter from './MockRouter'
import { RouteNames } from '@/enums'
import { StateModelIF } from '@/interfaces'
import flushPromises from 'flush-promises'
import { RegisteringPartySummary } from '@/components/parties/summaries'
import { FeeSummaryTypes } from '@/composables/fees/enums'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

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
    await store.dispatch('setRegistrationConfirmDebtorName', mockedDebtorNames[0])
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
    wrapper = shallowMount(ConfirmRenewal, { localVue, store, router, vuetify })
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
    const state = wrapper.vm.$store.state.stateModel as StateModelIF

    expect(wrapper.findComponent(ConfirmRenewal).exists()).toBe(true)
    expect(wrapper.findComponent(FolioNumberSummary).exists()).toBe(true)
    // check registering party
    expect(state.registration.parties.registeringParty).toBe(mockedFinancingStatementAll.registeringParty)
    expect(wrapper.findComponent(RegisteringPartySummary).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationLengthTrustSummary).exists()).toBe(true)
    // check fee summary + buttons
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowFeeSummary).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setBackBtn).toBe('Back')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setCancelBtn).toBe('Cancel')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setSubmitBtn).toBe('Submit Renewal')
    expect(wrapper.findComponent(StickyContainer).vm.$props.setFeeType).toBe(FeeSummaryTypes.RENEW)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setErrMsg).toBe('')
    // dialog
    expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)
    // certify
    expect(wrapper.findComponent(CertifyInformation).exists()).toBe(true)
  })

  it('allows back to previous page', async () => {
    expect(wrapper.findComponent(ConfirmRenewal).exists()).toBe(true)
    await wrapper.findComponent(StickyContainer).vm.$emit('back', true)
    expect(wrapper.vm.$route.name).toBe(RouteNames.RENEW_REGISTRATION)
  })

  it('processes cancel button action', async () => {
    // dialog doesn't start visible
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(false)
    // pressing cancel triggers dialog
    await wrapper.findComponent(StickyContainer).vm.$emit('cancel', true)
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(true)
    // if dialog emits proceed false it closes + stays on page
    await wrapper.findComponent(BaseDialog).vm.$emit('proceed', false)
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(false)
    expect(wrapper.vm.$route.name).toBe(RouteNames.CONFIRM_RENEWAL)
    // if dialog emits proceed true it goes to dashboard
    await wrapper.findComponent(StickyContainer).vm.$emit('cancel', true)
    await wrapper.findComponent(BaseDialog).vm.$emit('proceed', true)
    expect(wrapper.findComponent(BaseDialog).vm.$props.setDisplay).toBe(false)
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })

  it('allows submit of renewal', async () => {
    // Set up for valid discharge request
    await store.dispatch('setRegistrationNumber', '023001B')
    await store.dispatch('setFolioOrReferenceNumber', 'A-00000402')
    await store.dispatch('setRegistrationConfirmDebtorName', mockedDebtorNames[0])

    
    await wrapper.findComponent(CertifyInformation).vm.$emit('certifyValid', true)
    await Vue.nextTick()
    await wrapper.findComponent(StickyContainer).vm.$emit('submit', true)
    await Vue.nextTick()
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })
})
