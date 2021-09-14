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
import { ButtonsStacked, FolioNumberSummary } from '@/components/common'
import { RegistrationLengthTrust } from '@/components/registration'
import { FeeSummary } from '@/composables/fees'

// Other
import mockRouter from './MockRouter'
import { mockedNewRegStep1, mockedSelectSecurityAgreement } from './test-data'
import { RouteNames } from '@/enums'
import { DraftIF, LengthTrustIF, StateModelIF } from '@/interfaces'
import flushPromises from 'flush-promises'
import { RegisteringPartySummary } from '@/components/parties/summaries'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Input field selectors / buttons
const cancelBtn: string = '#reg-cancel-btn'
const saveBtn: string = '#reg-save-btn'
const expiryDate: string = '#new-expiry'

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
    expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
    expect(wrapper.findComponent(ButtonsStacked).exists()).toBe(true)
    expect(wrapper.findComponent(FolioNumberSummary).exists()).toBe(true)
    // check registering party
    expect(state.registration.parties.registeringParty).toBe(mockedFinancingStatementAll.registeringParty)
    expect(wrapper.findComponent(RegisteringPartySummary).exists()).toBe(true)
    expect(wrapper.findComponent(RegistrationLengthTrust).exists()).toBe(true)
    

  })

  it('allows cancel to previous page', () => {
    expect(wrapper.findComponent(ConfirmRenewal).exists()).toBe(true)
      wrapper.find(ButtonsStacked).vm.$emit('back', true)
      expect(wrapper.vm.$route.name).toBe(RouteNames.RENEW_REGISTRATION)
   })

  it('allows submit of renewal', async () => {
    // Set up for valid discharge request
    await store.dispatch('setRegistrationNumber', '023001B')
    await store.dispatch('setFolioOrReferenceNumber', 'A-00000402')
    await store.dispatch('setRegistrationConfirmDebtorName', mockedDebtorNames[0])

    await wrapper.findComponent(ButtonsStacked).vm.$emit('submit', true)
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
   })

})

