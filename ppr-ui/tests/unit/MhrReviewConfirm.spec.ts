// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'

// Local Components
import { MhrReviewConfirm } from '@/views'
import { HomeLocationReview, SubmittingPartyReview, YourHomeReview } from '@/components/mhrRegistration/ReviewConfirm'
import { CertifyInformation } from '@/components/common'
import { RouteNames } from '@/enums'
import mockRouter from './MockRouter'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  localVue.use(VueRouter)
  const router = mockRouter.mock()
  router.push({ name: RouteNames.MHR_REVIEW_CONFIRM })

  return mount(MhrReviewConfirm, {
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

describe('Mhr Review Confirm registration', () => {
  let wrapper: any
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')
  const currentAccount = {
    id: 'test_id'
  }
  sessionStorage.setItem('CURRENT_ACCOUNT', JSON.stringify(currentAccount))
  sessionStorage.setItem('AUTH_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/')
  const reviewConfirmState = store.state.stateModel.mhrValidationState.reviewConfirmValid

  afterEach(() => {
    wrapper.destroy()
  })

  it('mounts with the correct components', () => {
    wrapper = createComponent()
    expect(wrapper.findComponent(MhrReviewConfirm).exists()).toBe(true)
    expect(wrapper.findComponent(YourHomeReview).exists()).toBe(true)
    expect(wrapper.findComponent(SubmittingPartyReview).exists()).toBe(true)
    expect(wrapper.findComponent(HomeLocationReview).exists()).toBe(true)
    expect(wrapper.findComponent(CertifyInformation).exists()).toBe(true)
  })

  it('verifies Authorization default values', async () => {
    wrapper = createComponent()
    expect(wrapper.vm.authorizationValid).toBe(false)
    expect(wrapper.vm.validateReview).toBe(false)
  })

  it('prompts Authorization validation', async () => {
    wrapper = createComponent()

    // Verify defaults
    expect(wrapper.vm.authorizationValid).toBe(false)
    expect(wrapper.vm.validateReview).toBe(false)

    // Update validation state
    reviewConfirmState.validateSteps = true
    reviewConfirmState.validateApp = true
    await Vue.nextTick()

    // Verify prompt
    expect(wrapper.vm.validateReview).toBe(true)
  })
})
