// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'

// Local Components
import { MhrReviewConfirm } from '@/views'
import { HomeLocationReview, HomeOwnersReview, SubmittingPartyReview, YourHomeReview } from '@/components/mhrRegistration/ReviewConfirm'
import { CertifyInformation } from '@/components/common'
import { HomeTenancyTypes, RouteNames } from '@/enums'
import mockRouter from './MockRouter'
import { mockedFractionalOwnership, mockedPerson } from './test-data/mock-mhr-registration'
import { MhrRegistrationHomeOwnerGroupIF, MhrRegistrationHomeOwnerIF } from '@/interfaces/mhr-registration-interfaces'
import { getTestId } from './utils'
import { HomeOwnersTable } from '@/components/mhrRegistration/HomeOwners'

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
    expect(wrapper.findComponent(HomeOwnersReview).exists()).toBe(true)
    expect(wrapper.findComponent(HomeLocationReview).exists()).toBe(true)
    expect(wrapper.findComponent(CertifyInformation).exists()).toBe(true)
  })

  it('verifies Authorization default values', async () => {
    wrapper = createComponent()
    expect(wrapper.vm.authorizationValid).toBe(false)
    expect(wrapper.vm.isValidatingApp).toBe(false)
  })

  it('prompts Authorization validation', async () => {
    wrapper = createComponent()

    // Verify defaults
    expect(wrapper.vm.authorizationValid).toBe(false)
    expect(wrapper.vm.isValidatingApp).toBe(false)

    // Update validation state
    reviewConfirmState.validateSteps = true
    reviewConfirmState.validateApp = true
    await Vue.nextTick()

    // Verify prompt
    expect(wrapper.vm.isValidatingApp).toBe(true)
  })

  it('should show correct Home Ownership section (without a Group)', async () => {
    wrapper = createComponent()

    const owners = [mockedPerson] as MhrRegistrationHomeOwnerIF[]
    const homeOwnerGroup = [{ groupId: 1, owners: owners }] as MhrRegistrationHomeOwnerGroupIF[]

    await store.dispatch('setMhrRegistrationHomeOwnerGroups', homeOwnerGroup)

    const HomeOwnerReview = wrapper.findComponent(HomeOwnersReview)

    expect(HomeOwnerReview.exists()).toBeTruthy()
    expect(HomeOwnerReview.findComponent(HomeOwnersTable).exists()).toBeTruthy()

    const unfinishedError = HomeOwnerReview.get('.error-text')
    expect(unfinishedError.isVisible()).toBeFalsy()

    const homeTenancyType = HomeOwnerReview.find(getTestId('home-tenancy-type'))
    expect(homeTenancyType.exists()).toBeTruthy()
    expect(homeTenancyType.text()).toContain(HomeTenancyTypes.SOLE)

    const totalOwnership = HomeOwnerReview.find(getTestId('total-ownership'))
    expect(totalOwnership.exists()).toBeFalsy()

    const homeOwnersTable = HomeOwnerReview.find('.home-owners-table')
    expect(homeOwnersTable.exists()).toBeTruthy()
    expect(homeOwnersTable.text()).not.toContain('Group 1')
    expect(homeOwnersTable.text()).toContain(mockedPerson.individualName.first)
    expect(homeOwnersTable.text()).toContain(mockedPerson.phoneNumber)
    expect(homeOwnersTable.text()).toContain(mockedPerson.phoneExtension)
    expect(homeOwnersTable.text()).toContain(mockedPerson.address.city)
    expect(homeOwnersTable.text()).not.toContain(HomeTenancyTypes.SOLE)
  })

  it('should show correct Home Ownership section (with a Group)', async () => {
    wrapper = createComponent()

    const owners = [mockedPerson] as MhrRegistrationHomeOwnerIF[]
    const homeOwnerGroup = [{ groupId: 1, owners: owners, ...mockedFractionalOwnership }] as MhrRegistrationHomeOwnerGroupIF[]

    await store.dispatch('setMhrRegistrationHomeOwnerGroups', homeOwnerGroup)

    const HomeOwnerReview = wrapper.findComponent(HomeOwnersReview)
    HomeOwnerReview.vm.$data.showGroups = true // set show groups so
    await Vue.nextTick()

    expect(HomeOwnerReview.exists()).toBeTruthy()
    expect(HomeOwnerReview.findComponent(HomeOwnersTable).exists()).toBeTruthy()

    const unfinishedError = HomeOwnerReview.get('.error-text')
    expect(unfinishedError.isVisible()).toBeTruthy()
    expect(unfinishedError.text()).toContain('unfinished')

    const homeTenancyType = HomeOwnerReview.find(getTestId('home-tenancy-type'))
    expect(homeTenancyType.exists()).toBeTruthy()
    expect(homeTenancyType.text()).toContain(HomeTenancyTypes.COMMON)

    const totalOwnership = HomeOwnerReview.find(getTestId('total-ownership'))
    expect(totalOwnership.exists()).toBeTruthy()
    expect(totalOwnership.text()).toContain(`${mockedFractionalOwnership.interestNumerator}/${mockedFractionalOwnership.interestDenominator}`)

    const homeOwnersTable = HomeOwnerReview.find('.home-owners-table')
    expect(homeOwnersTable.exists()).toBeTruthy()
    expect(homeOwnersTable.text()).toContain('Group 1')
    expect(homeOwnersTable.text()).toContain(mockedPerson.individualName.first)
    expect(homeOwnersTable.text()).toContain(mockedPerson.phoneNumber)
    expect(homeOwnersTable.text()).toContain(mockedPerson.phoneExtension)
    expect(homeOwnersTable.text()).toContain(mockedPerson.address.city)
    expect(homeOwnersTable.text()).toContain(HomeTenancyTypes.NA)
  })
})
