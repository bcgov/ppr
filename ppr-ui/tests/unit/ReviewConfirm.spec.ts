// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'

// Local Components
import { ButtonFooter, FolioNumberSummary, Stepper, StickyContainer, CertifyInformation } from '@/components/common'
import { Collateral } from '@/components/collateral'
import { Parties } from '@/components/parties'
import { RegistrationLengthTrustSummary } from '@/components/registration'
import { ReviewConfirm } from '@/views'
import { BaseDialog } from '@/components/dialogs'
// Local types/helpers
import { FeeSummaryTypes } from '@/composables/fees/enums'
import {
  RegistrationFlowType,
  RouteNames,
  StatementTypes,
  UIRegistrationTypes
} from '@/enums'
import { LengthTrustIF } from '@/interfaces'
import { RegistrationTypes } from '@/resources'
// unit test helpers/data
import mockRouter from './MockRouter'
import { mockedSelectSecurityAgreement, mockedGeneralCollateral1 } from './test-data'
import { getLastEvent } from './utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// Input field selectors / buttons
const header = '#registration-header'
const title: string = '.sub-header'
const titleInfo: string = '.sub-header-info'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  // Prevent the warning "[Vuetify] Unable to locate target [data-app]"
  document.body.setAttribute('data-app', 'true')
  localVue.use(VueRouter)
  const router = mockRouter.mock()
  router.push({ name: RouteNames.REVIEW_CONFIRM })

  return mount((ReviewConfirm as any), {
    localVue,
    propsData: {
      appReady: true,
      isJestRunning: true
    },
    router,
    store,
    vuetify
  })
}

describe('Review Confirm new registration component', () => {
  let wrapper: any
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')
  const currentAccount = {
    id: 'test_id'
  }
  sessionStorage.setItem('CURRENT_ACCOUNT', JSON.stringify(currentAccount))
  sessionStorage.setItem('AUTH_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/')

  beforeEach(async () => {
    await store.dispatch('setRegistrationType', null)
    await store.dispatch('setRegistrationFlowType', null)
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('redirects to dashboard when store is not set', () => {
    wrapper = createComponent()
    expect(wrapper.vm.$route.name).toBe(RouteNames.DASHBOARD)
  })

  it('renders Add Parties View with child components when store is set', async () => {
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement())
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.NEW)
    wrapper = createComponent()
    await flushPromises()
    expect(wrapper.vm.$route.name).toBe(RouteNames.REVIEW_CONFIRM)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)
    expect(wrapper.findComponent(ReviewConfirm).exists()).toBe(true)
    expect(wrapper.findComponent(Stepper).exists()).toBe(true)
    expect(wrapper.findComponent(BaseDialog).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowFeeSummary).toBe(true)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setFeeType).toBe(FeeSummaryTypes.NEW)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationLength).toEqual({
      lifeInfinite: false,
      lifeYears: 0
    })
    expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationType).toBe(
      UIRegistrationTypes.SECURITY_AGREEMENT
    )
    expect(wrapper.findComponent(StickyContainer).vm.$props.setShowButtons).toBe(false)
    expect(wrapper.findComponent(ButtonFooter).exists()).toBe(true)
    expect(wrapper.findComponent(ButtonFooter).vm.$props.currentStatementType).toBe(StatementTypes.FINANCING_STATEMENT)
    expect(wrapper.findComponent(ButtonFooter).vm.$props.currentStepName).toBe(RouteNames.REVIEW_CONFIRM)
    expect(wrapper.findComponent(RegistrationLengthTrustSummary).exists()).toBe(true)
    expect(wrapper.findComponent(Parties).exists()).toBe(true)
    expect(wrapper.findComponent(Parties).vm.$props.isSummary).toBe(true)
    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.findComponent(Collateral).vm.$props.isSummary).toBe(true)
    expect(wrapper.findComponent(FolioNumberSummary).exists()).toBe(true)
    expect(wrapper.findComponent(CertifyInformation).exists()).toBe(true)
    expect(wrapper.find(header).exists()).toBe(true)
    expect(wrapper.find(title).exists()).toBe(true)
    expect(wrapper.find(titleInfo).exists()).toBe(true)
  })

  it('updates fee summary with registration length changes', async () => {
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement())
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.NEW)
    wrapper = createComponent()
    await flushPromises()
    expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationLength).toEqual({
      lifeInfinite: false,
      lifeYears: 0
    })
    const newLengthTrust1: LengthTrustIF = {
      valid: true,
      trustIndenture: false,
      lifeInfinite: true,
      lifeYears: 0
    }
    await store.dispatch('setLengthTrust', newLengthTrust1)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationLength).toEqual({
      lifeInfinite: newLengthTrust1.lifeInfinite,
      lifeYears: newLengthTrust1.lifeYears
    })
    const newLengthTrust2: LengthTrustIF = {
      valid: true,
      trustIndenture: false,
      lifeInfinite: true,
      lifeYears: 0
    }
    await store.dispatch('setLengthTrust', newLengthTrust2)
    expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationLength).toEqual({
      lifeInfinite: newLengthTrust2.lifeInfinite,
      lifeYears: newLengthTrust2.lifeYears
    })
  })

  it('displays correct info based on registration type', async () => {
    jest.setTimeout(50000)
    for (let i = 0; i < RegistrationTypes.length; i++) {
      // skip dividers + other
      if (
        !RegistrationTypes[i].registrationTypeUI ||
        RegistrationTypes[i].registrationTypeUI === UIRegistrationTypes.OTHER
      ) {
        continue
      }
      await store.dispatch('setRegistrationType', RegistrationTypes[i])
      await store.dispatch('setRegistrationFlowType', RegistrationFlowType.NEW)
      wrapper = createComponent()
      await flushPromises()
      expect(wrapper.findComponent(StickyContainer).vm.$props.setRegistrationType).toBe(
        RegistrationTypes[i].registrationTypeUI
      )
      // header
      expect(wrapper.find(header).text()).toContain(RegistrationTypes[i].registrationTypeUI)
      // title
      expect(wrapper.find(title).text()).toContain('Review and Confirm')
      // message
      expect(wrapper.find(titleInfo).text()).toContain(
        'Review the information in your registration. If you need to change'
      )
      wrapper.destroy()
    }
  })

  it('show error message in Collateral Summary section when description is empty', async () => {
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement())
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.NEW)
    await store.dispatch('setAddCollateral', { generalCollateral: mockedGeneralCollateral1 })

    wrapper = createComponent()
    await flushPromises()

    expect(wrapper.vm.$route.name).toBe(RouteNames.REVIEW_CONFIRM)
    expect(wrapper.vm.appReady).toBe(true)
    expect(wrapper.vm.dataLoaded).toBe(true)

    expect(wrapper.findComponent(Collateral).exists()).toBe(true)
    expect(wrapper.findComponent(Collateral).findAll('.invalid-message').exists()).toBe(false)

    // Go back to Collateral step
    await wrapper.find('#reg-back-btn').trigger('click')
    expect(wrapper.vm.$route.name).toBe(RouteNames.ADD_COLLATERAL)

    // Delete text from General Collateral as leave just html styling tag (as per current behavior)
    await store.dispatch('setAddCollateral', {
      generalCollateral:
      {
        addedDateTime: '2021-09-16T05:56:20Z',
        description: '<p></p>'
      }
    }
    )

    // Go Next to Review page and check that Collateral sections has invalid message(s)
    await wrapper.find('#reg-next-btn').trigger('click')
    expect(wrapper.vm.stepName).toBe(RouteNames.REVIEW_CONFIRM)
    expect(wrapper.find(title).text()).toContain('Review and Confirm')
    expect(wrapper.findComponent(Collateral).findAll('.invalid-message').exists()).toBe(true)
  })

  it('emits error', async () => {
    await store.dispatch('setRegistrationType', mockedSelectSecurityAgreement)
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.NEW)
    wrapper = createComponent()
    await flushPromises()
    const error = { statusCode: 404 }
    expect(getLastEvent(wrapper, 'error')).not.toEqual(error)
    await wrapper.findComponent(ButtonFooter).vm.$emit('error', error)
    await flushPromises()
    expect(getLastEvent(wrapper, 'error')).toEqual(error)
  })
})
