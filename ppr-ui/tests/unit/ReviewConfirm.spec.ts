// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { shallowMount, createLocalVue } from '@vue/test-utils'

// Components
import { ReviewConfirm } from '@/views'
import { ButtonFooter, Stepper, FolioNumberSummary, StickyContainer } from '@/components/common'
import { RegistrationLengthTrustSummary } from '@/components/registration'
import { Collateral } from '@/components/collateral'
import { Parties } from '@/components/parties'

// Other
import mockRouter from './MockRouter'
import { mockedLengthTrust1, mockedSelectSecurityAgreement } from './test-data'
import { RouteNames } from '@/enums'
import { DraftIF, LengthTrustIF } from '@/interfaces'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Input field selectors / buttons
const cancelBtn: string = '#reg-cancel-btn'
const saveBtn: string = '#reg-save-btn'
const saveResumeBtn: string = '#reg-save-resume-btn'
const backBtn: string = '#reg-back-btn'
const nextBtn: string = '#reg-next-btn'
const registrationLengthTrust: string = '#registration-length-trust'
const errorLinkLengthTrust: string = '#router-link-length-trust'

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('ReviewConfirm new registration component', () => {
  let wrapper: any
  const { assign } = window.location

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any

    // create a Local Vue and install router on it
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    await router.push({ name: RouteNames.REVIEW_CONFIRM })
    wrapper = shallowMount(ReviewConfirm, { localVue, store, router, vuetify })
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
  })

  it('renders Review Confirm View with child components', () => {
    expect(wrapper.findComponent(ReviewConfirm).exists()).toBe(true)
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowFeeSummary).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(false)
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    expect(wrapper.findComponent(FolioNumberSummary).exists()).toBe(true)
  })
})

describe('ReviewConfirm step 1 tests', () => {
  let wrapper: any
  const { assign } = window.location

  beforeEach(async () => {
    // reset the store data
    await store.dispatch('resetNewRegistration')
    const resetDraft:DraftIF = {
      type: '',
      financingStatement: null,
      createDateTime: null,
      lastUpdateDateTime: null
    }
    await store.dispatch('setDraft', resetDraft)
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement)

    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any

    // create a Local Vue and install router on it
    const localVue = createLocalVue()
    localVue.use(VueRouter)
    const router = mockRouter.mock()
    await router.push({ name: 'review-confirm' })
    wrapper = shallowMount(ReviewConfirm, { localVue, store, router, vuetify })
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
  })

  it('Review Confirm View with invalid step 1', async () => {
    const lengthTrust:LengthTrustIF = JSON.parse(JSON.stringify(mockedLengthTrust1))
    await wrapper.vm.$store.dispatch('setLengthTrust', lengthTrust)
    expect(wrapper.findComponent(ReviewConfirm).exists()).toBe(true)
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowFeeSummary).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(false)
    expect(wrapper.findComponent(RegistrationLengthTrustSummary).exists()).toBe(true)
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.findComponent(Parties).exists()).toBe(true)
    // expect(wrapper.findComponent(RegistrationLengthTrust).isSummary).toBe(true)
    // expect(wrapper.findComponent(RegistrationLengthTrust).showErrorSummary).toBe(true)
    // expect(wrapper.findComponent(RegistrationLengthTrust).lengthSummary).toBe('Not entered')
    // expect(wrapper.findComponent(RegistrationLengthTrust).trustIndentureSummary).toBe('No')
  })

  it('Review Confirm View with valid step 1', async () => {
    const lengthTrust:LengthTrustIF = JSON.parse(JSON.stringify(mockedLengthTrust1))
    lengthTrust.valid = true
    lengthTrust.lifeInfinite = false
    lengthTrust.lifeYears = 3
    lengthTrust.trustIndenture = true
    await wrapper.vm.$store.dispatch('setLengthTrust', lengthTrust)
    expect(wrapper.findComponent(ReviewConfirm).exists()).toBe(true)
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowFeeSummary).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(false)
    expect(wrapper.findComponent(RegistrationLengthTrustSummary).exists()).toBe(true)
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.findComponent(Parties).exists()).toBe(true)
    // expect(wrapper.findComponent(RegistrationLengthTrust).isSummary).toBe(true)
    // expect(wrapper.findComponent(RegistrationLengthTrust).showErrorSummary).toBe(false)
    // expect(wrapper.findComponent(RegistrationLengthTrust).lengthSummary).toBe('3')
    // expect(wrapper.findComponent(RegistrationLengthTrust).trustIndentureSummary).toBe('Yes')
  })
})
