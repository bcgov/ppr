// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'

// Local Components
import { MhrReviewConfirm } from '@/views'
import { HomeLocationReview, HomeOwnersReview,
  SubmittingPartyReview, YourHomeReview } from '@/components/mhrRegistration/ReviewConfirm'
import { AccountInfo, Attention, CautionBox, CertifyInformation,
  ContactUsToggle, FolioOrReferenceNumber, FormField } from '@/components/common'
import { HomeTenancyTypes, ProductCode, RouteNames, HomeCertificationOptions } from '@/enums'
import mockRouter from './MockRouter'
import { mockedFractionalOwnership, mockedPerson } from './test-data/mock-mhr-registration'
import { MhrRegistrationHomeOwnerGroupIF, MhrRegistrationHomeOwnerIF } from '@/interfaces/mhr-registration-interfaces'
import { getTestId } from './utils'
import { HomeOwnersTable } from '@/components/mhrRegistration/HomeOwners'
import { MhrRegistrationType } from '@/resources'
import { mockedAccountInfo, mockedManufacturerAuthRoles } from './test-data'
import { defaultFlagSet } from '@/utils'
import { StaffPayment } from '@bcrs-shared-components/staff-payment'
import { HomeSections } from '@/components/mhrRegistration'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

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
  let wrapper: Wrapper<any>
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')
  const currentAccount = {
    id: 'test_id'
  }
  sessionStorage.setItem('CURRENT_ACCOUNT', JSON.stringify(currentAccount))
  sessionStorage.setItem('AUTH_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/')
  const reviewConfirmState = store.getMhrRegistrationValidationModel.reviewConfirmValid

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

    // Should not exists for staff registration
    expect(wrapper.findComponent(Attention).exists()).toBe(false)
    expect(wrapper.findComponent(CautionBox).exists()).toBe(false)
    expect(wrapper.findComponent(ContactUsToggle).exists()).toBe(false)
    expect(wrapper.findComponent(FolioOrReferenceNumber).exists()).toBe(false)
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
    await nextTick()

    // Verify prompt
    expect(wrapper.vm.isValidatingApp).toBe(true)
  })

  it('should show correct Home Ownership section (without a Group)', async () => {
    wrapper = createComponent()

    const owners = [mockedPerson] as MhrRegistrationHomeOwnerIF[]
    const homeOwnerGroup = [{ groupId: 1, owners: owners }] as MhrRegistrationHomeOwnerGroupIF[]

    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroup)

    const HomeOwnerReview = wrapper.findComponent(HomeOwnersReview)

    expect(HomeOwnerReview.exists()).toBeTruthy()
    expect(HomeOwnerReview.findComponent(HomeOwnersTable).exists()).toBeTruthy()

    expect(HomeOwnerReview.find('.error-text').isVisible()).toBeFalsy()

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
    wrapper.vm.setShowGroups(true)

    const owners = [mockedPerson] as MhrRegistrationHomeOwnerIF[]
    // eslint-disable-next-line max-len
    const homeOwnerGroup = [{ groupId: 1, owners: owners, ...mockedFractionalOwnership }] as MhrRegistrationHomeOwnerGroupIF[]
    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroup)
    await nextTick()

    const HomeOwnerReview = wrapper.findComponent(HomeOwnersReview)
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
    // eslint-disable-next-line max-len
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

  it('does not show portions of yourHomeReview and SubmittingPartyReview if no data was entered', async () => {
    wrapper = createComponent()
    const yourHomeReview = wrapper.findComponent(YourHomeReview)
    expect(yourHomeReview.exists()).toBeTruthy()
    expect(yourHomeReview.findComponent(HomeSections).exists()).toBe(false)
    await store.setMhrHomeDescription({ key: 'manufacturer', value: 'test' })
    expect(yourHomeReview.findComponent(HomeSections).exists()).toBe(true)

    const submittingPartyReview = wrapper.findComponent(SubmittingPartyReview)
    expect(submittingPartyReview.exists()).toBeTruthy()
    expect(submittingPartyReview.find('#review-submitting-party-section').exists()).toBe(false)
    await store.setMhrSubmittingParty({ key: 'phoneNumber', value: '123' })
    expect(submittingPartyReview.find('#review-submitting-party-section').exists()).toBe(true)
  })
})

describe('Mhr Manufacturer Registration Review and Confirm', () => {
  let wrapper: Wrapper<any>
  const currentAccount = {
    id: 'test_id'
  }
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')
  sessionStorage.setItem('CURRENT_ACCOUNT', JSON.stringify(currentAccount))
  sessionStorage.setItem('AUTH_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/')

  beforeAll(async () => {
    defaultFlagSet['mhr-registration-enabled'] = true
    await store.setAuthRoles(mockedManufacturerAuthRoles)
    await store.setRegistrationType(MhrRegistrationType)
    await store.setUserProductSubscriptionsCodes([ProductCode.MHR, ProductCode.MANUFACTURER])
  })

  beforeEach(async () => {
    wrapper = createComponent()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  afterAll(async () => {
    defaultFlagSet['mhr-registration-enabled'] = false
    await store.setAuthRoles([])
    await store.setRegistrationType(null)
  })

  it('renders and displays the Mhr Registration View', async () => {
    wrapper.vm.accountInfo = mockedAccountInfo
    await nextTick()
    expect(wrapper.findComponent(MhrReviewConfirm).exists()).toBe(true)
    expect(wrapper.findComponent(YourHomeReview).exists()).toBe(true)
    expect(wrapper.findComponent(HomeOwnersReview).exists()).toBe(true)
    expect(wrapper.findComponent(HomeLocationReview).exists()).toBe(true)
    expect(wrapper.findComponent(CertifyInformation).exists()).toBe(true)
    expect(wrapper.findComponent(AccountInfo).exists()).toBe(true)
    expect(wrapper.findComponent(Attention).exists()).toBe(true)
    expect(wrapper.findComponent(FolioOrReferenceNumber).exists()).toBe(true)
    expect(wrapper.findComponent(ContactUsToggle).exists()).toBe(true)
    expect(wrapper.findComponent(CautionBox).exists()).toBe(true)

    // Should not exist for manufacturer registration
    expect(wrapper.findComponent(StaffPayment).exists()).toBe(false)
  })

  it('correctly set attention and folio', async () => {
    store.setMhrAttentionReference('TEST 123')
    store.setFolioOrReferenceNumber('TEST 245')
    wrapper = createComponent()
    await nextTick()
    const attention = wrapper.findComponent(Attention)
    const folio = wrapper.findComponent(FolioOrReferenceNumber)
    expect((attention.findComponent(FormField) as Wrapper<any>).vm.inputModel).toBe('TEST 123')
    expect((folio.findComponent(FormField) as Wrapper<any>).vm.inputModel).toBe('TEST 245')
  })

  it('incorrect behavior if no certification checkbox is checked', async () => {
    const yourHomeReview = wrapper.findComponent(YourHomeReview)
    expect(yourHomeReview.exists()).toBeTruthy()
    await store.setMhrHomeDescription({key: 'hasNoCertification', value: true})
    expect(yourHomeReview.find(getTestId('home-certification-header-1')).text()).toBe('Home Certification')
    expect(yourHomeReview
      .find(getTestId('home-certification-content-1'))
      .text()).toBe('There is no certification available for this home.')
  })

  it('incorrect behavior in home certification - CSA number', async () => {
    const yourHomeReview = wrapper.findComponent(YourHomeReview)
    expect(yourHomeReview.exists()).toBeTruthy()
    await store.setMhrHomeDescription({key: 'hasNoCertification', value: false})
    await nextTick()

    await store.setMhrHomeDescription({key: 'certificationOption', value: HomeCertificationOptions.CSA})
    await nextTick()
    expect(yourHomeReview.find(getTestId('home-certification-header-1-csa')).text()).toBe('CSA Number')
    expect(yourHomeReview.find(getTestId('home-certification-content-1-csa')).text()).toBe('(Not Entered)')
    expect(yourHomeReview.find(getTestId('home-certification-header-2-csa')).text()).toBe('CSA Standard')
    expect(yourHomeReview.find(getTestId('home-certification-content-2-csa')).text()).toBe('(Not Entered)')

    await store.setMhrHomeDescription({key: 'csaNumber', value: '32123'})
    await nextTick()
    expect(yourHomeReview.find(getTestId('home-certification-header-1-csa')).text()).toBe('CSA Number')
    expect(yourHomeReview.find(getTestId('home-certification-content-1-csa')).text()).toBe('32123')
    expect(yourHomeReview.find(getTestId('home-certification-header-2-csa')).text()).toBe('CSA Standard')
    expect(yourHomeReview.find(getTestId('home-certification-content-2-csa')).text()).toBe('(Not Entered)')

    await store.setMhrHomeDescription({key: 'csaStandard', value: 'A277'})
    await nextTick()
    expect(yourHomeReview.find(getTestId('home-certification-header-1-csa')).text()).toBe('CSA Number')
    expect(yourHomeReview.find(getTestId('home-certification-content-1-csa')).text()).toBe('32123')
    expect(yourHomeReview.find(getTestId('home-certification-header-2-csa')).text()).toBe('CSA Standard')
    expect(yourHomeReview.find(getTestId('home-certification-content-2-csa')).text()).toBe('A277')
  })

  it('incorrect behavior in home certification - Engineer Inspection', async () => {
    const yourHomeReview = wrapper.findComponent(YourHomeReview)
    expect(yourHomeReview.exists()).toBeTruthy()
    await store.setMhrHomeDescription({key: 'certificationOption', 
                                       value: HomeCertificationOptions.ENGINEER_INSPECTION})
    await nextTick()
    expect(yourHomeReview.find(getTestId('home-certification-header-1-eng')).text()).toBe('Engineer\'s Name')
    expect(yourHomeReview.find(getTestId('home-certification-content-1-eng')).text()).toBe('(Not Entered)')
    expect(yourHomeReview.find(getTestId('home-certification-header-2-eng')).text()).toBe('Date of Engineer\'s Report')
    expect(yourHomeReview.find(getTestId('home-certification-content-2-eng')).text()).toBe('(Not Entered)')

    await store.setMhrHomeDescription({key: 'engineerName', value: 'John Doe'})
    await nextTick()
    expect(yourHomeReview.find(getTestId('home-certification-header-1-eng')).text()).toBe('Engineer\'s Name')
    expect(yourHomeReview.find(getTestId('home-certification-content-1-eng')).text()).toBe('John Doe')
    expect(yourHomeReview.find(getTestId('home-certification-header-2-eng')).text()).toBe('Date of Engineer\'s Report')
    expect(yourHomeReview.find(getTestId('home-certification-content-2-eng')).text()).toBe('(Not Entered)')

    await store.setMhrHomeDescription({key: 'engineerDate', value: '2023-10-10'})
    await nextTick()
    expect(yourHomeReview.find(getTestId('home-certification-header-1-eng')).text()).toBe('Engineer\'s Name')
    expect(yourHomeReview.find(getTestId('home-certification-content-1-eng')).text()).toBe('John Doe')
    expect(yourHomeReview.find(getTestId('home-certification-header-2-eng')).text()).toBe('Date of Engineer\'s Report')
    expect(yourHomeReview.find(getTestId('home-certification-content-2-eng')).text()).toBe('October 10, 2023')
  })
})
