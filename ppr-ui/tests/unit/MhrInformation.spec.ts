// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import VueRouter from 'vue-router'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'

// local components
import { HomeOwners, MhrInformation } from '@/views'
import { AccountInfo, StickyContainer, CertifyInformation } from '@/components/common'
import { DatePicker } from '@bcrs-shared-components/date-picker'
import mockRouter from './MockRouter'
import { HomeTenancyTypes, RouteNames } from '@/enums'
import { HomeOwnersTable } from '@/components/mhrRegistration/HomeOwners'
import { getTestId } from './utils'
import {
  mockedAddedPerson,
  mockedRemovedPerson,
  mockedOrganization,
  mockedPerson,
  mockMhrTransferCurrentHomeOwner,
  mockedRegisteringParty1,
  mockedAccountInfo
} from './test-data'
import { CertifyIF, MhrRegistrationHomeOwnerGroupIF, MhrRegistrationHomeOwnerIF } from '@/interfaces'
import { nextTick } from '@vue/composition-api'
import { TransferDetails, TransferDetailsReview } from '@/components/mhrTransfers'

import { toDisplayPhone } from '@/utils'

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
  localVue.use(VueRouter)
  const router = mockRouter.mock()
  router.push({
    name: RouteNames.MHR_INFORMATION
  })

  document.body.setAttribute('data-app', 'true')
  return mount(MhrInformation, {
    localVue,
    store,
    propsData: {
      appReady: true,
      isMhrTransfer: true
    },
    vuetify,
    router
  })
}

const TRANSFER_DECLARED_VALUE = '123'
const TRANSFER_CONSIDERATION = `$${TRANSFER_DECLARED_VALUE}.00`

// TODO: Remove after API updates to include the ID for Owners
function addIDsForOwners (ownersGroups): Array<any> {
  // Create an ID to each individual owner for UI Tracking
  ownersGroups.forEach(ownerGroup => {
    for (const [index, owner] of ownerGroup.owners.entries()) {
      owner.ownerId = ownerGroup.groupId + (index + 1)
    }
  })

  return ownersGroups
}

async function setupCurrentHomeOwners (): Promise<void> {
  await store.dispatch('setMhrTransferCurrentHomeOwnerGroups', [mockMhrTransferCurrentHomeOwner])
  // TODO: Remove after API updates to include the ID for Owners
  const homeOwnerWithIdsArray = addIDsForOwners([mockMhrTransferCurrentHomeOwner])
  await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerWithIdsArray)
}

async function setupCurrentMultipleHomeOwnersGroups (): Promise<void> {
  // setup two groups so they can be shown in the table
  const currentHomeOwnersGroups = [
    mockMhrTransferCurrentHomeOwner,
    {
      ...mockMhrTransferCurrentHomeOwner,
      groupId: 2
    }
  ]

  await store.dispatch('setMhrTransferCurrentHomeOwnerGroups', currentHomeOwnersGroups)
  // TODO: Remove after API updates to include the ID for Owners
  const homeOwnerWithIdsArray = addIDsForOwners(currentHomeOwnersGroups)
  await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerWithIdsArray)
}

async function triggerUnsavedChange (): Promise<void> {
  // set unsaved changes to make Transfer Details visible
  await store.dispatch('setUnsavedChanges', true)
  await Vue.nextTick()
}

// For future use when Transfer Details will be required to go to Review
async function enterTransferDetailsFields (transferDetailsWrapper: Wrapper<any, Element>): Promise<void> {
  transferDetailsWrapper.find(getTestId('declared-value')).setValue(TRANSFER_DECLARED_VALUE)
  transferDetailsWrapper.find(getTestId('declared-value')).trigger('blur')
  transferDetailsWrapper.findComponent(DatePicker).vm.$emit('emitDate', { date: '2020-10-10' })
  await Vue.nextTick()
}

describe('Mhr Information', () => {
  let wrapper: Wrapper<any>
  const currentAccount = {
    id: 'test_id'
  }
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')
  sessionStorage.setItem('CURRENT_ACCOUNT', JSON.stringify(currentAccount))
  sessionStorage.setItem('AUTH_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/')

  const LEGAL_NAME = 'TEST NAME'

  beforeEach(async () => {
    await store.dispatch('setCertifyInformation', {
      valid: false,
      certified: false,
      legalName: LEGAL_NAME,
      registeringParty: mockedRegisteringParty1
    } as CertifyIF)
    wrapper = createComponent()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders and displays the Mhr Information View', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.$data.dataLoaded = true
    await Vue.nextTick()

    expect(wrapper.props().isMhrTransfer).toBe(true)
    expect(wrapper.vm.$data.getMhrTransferCurrentHomeOwners.length).toBe(1)
    expect(wrapper.vm.$data.getMhrTransferHomeOwners.length).toBe(1)

    expect(wrapper.findComponent(MhrInformation).exists()).toBe(true)
    expect(wrapper.find('#mhr-information-header').text()).toContain('Manufactured Home Information')

    expect(wrapper.findComponent(HomeOwners).exists()).toBeTruthy()
    const homeOwnersTable = wrapper.findComponent(HomeOwnersTable)
    expect(homeOwnersTable.exists()).toBeTruthy()
    expect(homeOwnersTable.text()).toContain(mockMhrTransferCurrentHomeOwner.owners[0].organizationName)
    expect(homeOwnersTable.text()).toContain(mockMhrTransferCurrentHomeOwner.owners[0].address.city)
  })

  it('renders and displays the correct sub components', async () => {
    // Sticky container w/ Fee Summary
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
  })

  it('should render Added badge after Owner is added to the table', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.$data.dataLoaded = true
    await Vue.nextTick()

    const mhrInformationComponent = wrapper.findComponent(MhrInformation)
    expect(mhrInformationComponent.exists()).toBeTruthy()
    wrapper.vm.$data.dataLoaded = true
    await nextTick()

    expect(mhrInformationComponent.findComponent(HomeOwnersTable).exists()).toBeTruthy()

    // same IF for Transfer and Registration
    const owners = [mockedAddedPerson, mockedRemovedPerson] as MhrRegistrationHomeOwnerIF[]
    const homeOwnerGroup = [
      mockMhrTransferCurrentHomeOwner,
      { groupId: 1, owners: owners }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerGroup)

    const ownersTable = mhrInformationComponent.findComponent(HomeOwners).findComponent(HomeOwnersTable)

    const newlyAddedOwner = ownersTable.find(getTestId(`owner-info-${mockedPerson.ownerId}`))
    expect(newlyAddedOwner.text()).toContain(mockedPerson.individualName.first)
    expect(newlyAddedOwner.text()).toContain(mockedPerson.individualName.last)

    const addedBadge = newlyAddedOwner.find(getTestId('owner-added-badge'))
    expect(addedBadge.isVisible()).toBeTruthy()

    const removedBadge = ownersTable.find(getTestId('owner-removed-badge'))
    expect(removedBadge.isVisible()).toBeTruthy()
  })

  it('should show correct Home Tenancy Type for MHR Transfers', async () => {
    await store.dispatch('setMhrTransferHomeOwnerGroups', [{
      ...mockMhrTransferCurrentHomeOwner,
      interestNumerator: null,
      interestDenominator: null
    }])

    wrapper.vm.$data.dataLoaded = true
    await Vue.nextTick()

    const homeOwnerGroup = [{ groupId: 1, owners: [mockedPerson] }]

    expect(wrapper.findComponent(HomeOwners).vm.$data.getHomeOwners.length).toBe(1)
    expect(
      wrapper
        .findComponent(HomeOwners)
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.SOLE)

    // Add a second Owner to the existing group
    homeOwnerGroup[0].owners.push(mockedOrganization)

    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerGroup)
    await Vue.nextTick()

    expect(wrapper.findComponent(HomeOwners).vm.$data.getHomeOwners.length).toBe(2)
    expect(
      wrapper
        .findComponent(HomeOwners)
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.JOINT)

    // Enable Groups
    homeOwnerGroup.push({ groupId: 2, owners: [mockedPerson] })
    await Vue.nextTick()

    expect(
      wrapper
        .findComponent(HomeOwners)
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.COMMON)
  })

  it('should correctly show current and newly added Owner Groups', async () => {
    setupCurrentMultipleHomeOwnersGroups()
    wrapper.vm.$data.dataLoaded = true
    await Vue.nextTick()

    // check current Owners and Groups
    wrapper.findComponent(HomeOwners).vm.$data.setShowGroups(true)
    await Vue.nextTick()

    expect(wrapper.findComponent(HomeOwners).vm.$data.getMhrTransferCurrentHomeOwners.length).toBe(2)
    expect(store.getters.getMhrTransferHomeOwnerGroups.length).toBe(2)

    const homeOwnersTable = wrapper.findComponent(HomeOwners).findComponent(HomeOwnersTable)

    const currentOwnerGroupHeader = homeOwnersTable.find(
      `#mhr-home-edit-owners-group-${mockMhrTransferCurrentHomeOwner.groupId}`
    )
    expect(currentOwnerGroupHeader.text()).toContain(`Group ${mockMhrTransferCurrentHomeOwner.groupId}`)
    expect(currentOwnerGroupHeader.text()).toContain('Owners: 1')

    expect(homeOwnersTable.findAll('.owner-info').length).toBe(2)
    const currentOwnerInfo = homeOwnersTable.findAll('.owner-info').at(0)

    expect(currentOwnerInfo.text()).toContain(mockMhrTransferCurrentHomeOwner.owners[0].organizationName)
    expect(currentOwnerInfo.text()).toContain(mockMhrTransferCurrentHomeOwner.owners[0].address.city)

    // Get current Groups
    const homeOwnerGroups = store.getters.getMhrTransferHomeOwnerGroups as MhrRegistrationHomeOwnerGroupIF[]

    // Add a second Group
    const NEW_GROUP_ID = 3
    const newHomeOwnerGroup = { groupId: NEW_GROUP_ID, owners: [mockedPerson] } as MhrRegistrationHomeOwnerGroupIF
    homeOwnerGroups.push(newHomeOwnerGroup)
    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerGroups)
    await Vue.nextTick()

    // Check that new Groups and Owner info are added to the table
    expect(store.getters.getMhrTransferHomeOwnerGroups.length).toBe(3)
    expect(homeOwnersTable.findAll('.owner-info').length).toBe(3)

    const newOwnerGroupHeader = homeOwnersTable.find(`#mhr-home-edit-owners-group-${NEW_GROUP_ID}`)
    expect(newOwnerGroupHeader.text()).toContain(`Group ${NEW_GROUP_ID}`)

    const newOwnerInfo = homeOwnersTable.findAll('.owner-info').at(2)
    expect(newOwnerInfo.text()).toContain(mockedPerson.individualName.first)
    expect(newOwnerInfo.text()).toContain(mockedPerson.address.city)
  })

  // TRANSFER DETAILS COMPONENT TESTS

  it('should render Transfer Details component', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.$data.dataLoaded = true
    await Vue.nextTick()

    expect(wrapper.props().isMhrTransfer).toBe(true)
    expect(wrapper.vm.$data.getMhrTransferCurrentHomeOwners.length).toBe(1)
    expect(wrapper.vm.$data.getMhrTransferHomeOwners.length).toBe(1)

    expect(wrapper.findComponent(MhrInformation).findComponent(TransferDetails).exists()).toBeFalsy()
    expect(wrapper.findComponent(MhrInformation).findComponent(HomeOwnersTable).exists()).toBeTruthy()

    // Add some owners so Transfer Details will display
    const owners = [mockedAddedPerson, mockedRemovedPerson] as MhrRegistrationHomeOwnerIF[] // same IF for Transfer and Registration
    const homeOwnerGroup = [
      mockMhrTransferCurrentHomeOwner,
      { groupId: 1, owners: owners }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerGroup)

    expect(wrapper.findComponent(MhrInformation).exists()).toBe(true)

    const mhrTransferDetailsComponent = wrapper.findComponent(MhrInformation).findComponent(TransferDetails)
    expect(mhrTransferDetailsComponent.exists()).toBeTruthy()

    // Check for component's fields
    expect(mhrTransferDetailsComponent.find(getTestId('declared-value')).exists()).toBeTruthy()
    expect(mhrTransferDetailsComponent.find(getTestId('consideration')).exists()).toBeTruthy()
    expect(mhrTransferDetailsComponent.find(getTestId('transfer-date')).exists()).toBeTruthy()
    expect(mhrTransferDetailsComponent.find(getTestId('lease-own-checkbox')).exists()).toBeTruthy()

    mhrTransferDetailsComponent.find(getTestId('declared-value')).setValue(123)
    mhrTransferDetailsComponent.find(getTestId('declared-value')).trigger('blur')
    await Vue.nextTick()

    // Check that error/warning is shown for Declared Value less than 500
    expect(mhrTransferDetailsComponent.find('.v-messages__message').isVisible()).toBeTruthy()
    await Vue.nextTick()

    // Check that Consideration displayed Declared Value on blur
    expect(mhrTransferDetailsComponent.vm.$data.consideration).toBe('$123.00')
  })

  it('should render Attention or Reference Number section on Review screen', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.$data.dataLoaded = true
    await Vue.nextTick()

    expect(wrapper.find('#transfer-ref-num-section').exists()).toBeFalsy()

    // go to Review screen
    await triggerUnsavedChange()
    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await Vue.nextTick()

    expect(wrapper.find('#transfer-ref-num-section').exists()).toBeTruthy()
    expect(wrapper.find(getTestId('attn-ref-number-card')).classes('border-error-left')).toBeFalsy()

    expect(wrapper.find(getTestId('attn-ref-number-field')).exists()).toBeTruthy()

    // trigger error in Attn Ref Num field (40+ chars)
    wrapper.find(getTestId('attn-ref-number-field')).setValue('5'.repeat(45))
    expect(wrapper.vm.$data.attentionReference).toBe('5'.repeat(45))
    await Vue.nextTick()
    await Vue.nextTick()

    expect(wrapper.find(getTestId('attn-ref-number-card')).classes('border-error-left')).toBeTruthy()
    expect(
      wrapper
        .find(getTestId('attn-ref-number-card'))
        .find('.v-input')
        .classes('error--text')
    ).toBeTruthy()
    expect(
      wrapper
        .find(getTestId('attn-ref-number-card'))
        .find('.v-text-field__details .v-messages__message')
        .exists()
    ).toBeTruthy()

    // reset Attention Reference Number validation (to not affect other tests)
    wrapper.vm.$data.isRefNumValid = true
  })

  it('should render Authorization component on review', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.$data.dataLoaded = true
    await Vue.nextTick()

    expect(wrapper.props().isMhrTransfer).toBe(true)
    expect(wrapper.vm.$data.getMhrTransferCurrentHomeOwners.length).toBe(1)
    expect(wrapper.vm.$data.getMhrTransferHomeOwners.length).toBe(1)
    expect(wrapper.findComponent(MhrInformation).exists()).toBe(true)

    // Enter review mode
    await triggerUnsavedChange()
    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await Vue.nextTick()

    // Check if Authorization renders in review mode
    expect(
      wrapper
        .findComponent(MhrInformation)
        .findComponent(CertifyInformation)
        .exists()
    ).toBe(true)

    // Check for component's attributes
    const authorizationComponent = wrapper.findComponent(MhrInformation).findComponent(CertifyInformation)
    expect(authorizationComponent.find('#certify-summary').exists()).toBeTruthy()
    expect(authorizationComponent.find('#certify-information').exists()).toBeTruthy()
    expect(authorizationComponent.find('#checkbox-certified').exists()).toBeTruthy()
    expect(authorizationComponent.text()).toContain(mockedRegisteringParty1.address.city)
    expect(authorizationComponent.text()).toContain(mockedRegisteringParty1.address.street)
    expect(authorizationComponent.text()).toContain(mockedRegisteringParty1.address.postalCode)
  })

  it('should render Submitting Party component on the Review screen', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.$data.dataLoaded = true
    await Vue.nextTick()

    expect(wrapper.find('#account-info').exists()).toBeFalsy()

    // set Account Info in local state
    wrapper.vm.$data.accountInfo = mockedAccountInfo

    await triggerUnsavedChange()
    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await Vue.nextTick()

    expect(wrapper.find('#account-info').exists()).toBeTruthy()
    expect(wrapper.find(getTestId('submitting-party-tooltip')).exists()).toBeTruthy()

    const accountInfoTable = wrapper.findComponent(AccountInfo).find(getTestId('account-info-table'))
    expect(accountInfoTable.exists()).toBeTruthy()

    const accountInfoText = accountInfoTable.text()
    expect(accountInfoText).toContain(mockedAccountInfo.name)
    expect(accountInfoText).toContain(toDisplayPhone(mockedAccountInfo.accountAdmin.phone))
    expect(accountInfoText).toContain(mockedAccountInfo.accountAdmin.email)
    expect(accountInfoText).toContain('Ext ' + mockedAccountInfo.accountAdmin.phoneExtension)
    expect(accountInfoText).toContain(mockedAccountInfo.mailingAddress.city)
    expect(accountInfoText).toContain(mockedAccountInfo.mailingAddress.street)
    expect(accountInfoText).toContain(mockedAccountInfo.mailingAddress.postalCode)
  })

  it('should render TransferDetailsReview on Review screen', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.$data.dataLoaded = true
    await Vue.nextTick()

    // Should hide transfer details if no changes made
    expect(wrapper.findComponent(MhrInformation).findComponent(TransferDetails).exists()).toBeFalsy()

    // Add some owners so Transfer Details will display
    const owners = [mockedAddedPerson, mockedRemovedPerson] as MhrRegistrationHomeOwnerIF[]
    const homeOwnerGroup = [
      mockMhrTransferCurrentHomeOwner,
      { groupId: 1, owners: owners }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerGroup)

    // Should show transfer details once changes made
    expect(wrapper.findComponent(MhrInformation).findComponent(TransferDetails).exists()).toBeTruthy()

    // set some test values for transfer details fields
    const mhrTransferDetailsComponent = wrapper.findComponent(MhrInformation).findComponent(TransferDetails)
    mhrTransferDetailsComponent.find(getTestId('declared-value')).setValue(TRANSFER_DECLARED_VALUE)
    mhrTransferDetailsComponent.find(getTestId('declared-value')).trigger('blur')
    await Vue.nextTick()
    mhrTransferDetailsComponent.find(getTestId('lease-own-checkbox')).setChecked()
    await Vue.nextTick()

    expect(wrapper.findComponent(TransferDetailsReview).exists()).toBeFalsy()

    // go to Review screen
    await triggerUnsavedChange()
    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await Vue.nextTick()
    await Vue.nextTick()

    // renders TransferDetailsReview
    expect(wrapper.findComponent(TransferDetailsReview).exists()).toBeTruthy()
    const mhrTransferDetailsReviewComponent = wrapper.findComponent(TransferDetailsReview)

    // displaying correct declared value
    expect(mhrTransferDetailsReviewComponent.find('#declared-value-display').exists()).toBeTruthy()
    const currentDeclaredValue = mhrTransferDetailsReviewComponent.find('#declared-value-display')
    expect(currentDeclaredValue.text()).toBe(`$${TRANSFER_DECLARED_VALUE}.00`)

    // autofilled consideration and displaying correct consideration value
    expect(mhrTransferDetailsReviewComponent.find('#consideration-display').exists()).toBeTruthy()
    const currentConsideration = mhrTransferDetailsReviewComponent.find('#consideration-display')
    expect(currentConsideration.text()).toBe(TRANSFER_CONSIDERATION)

    // displaying lease land row when checked
    expect(mhrTransferDetailsReviewComponent.find('#lease-land-display').exists()).toBeTruthy()
  })

  it('should render yellow message bar on the Review screen', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.$data.dataLoaded = true
    await Vue.nextTick()

    // doesn't exist on manufactured home page
    expect(wrapper.find('#yellow-message-bar').exists()).toBeFalsy()

    // trigger review
    await triggerUnsavedChange()
    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await Vue.nextTick()

    // exists on review page
    expect(wrapper.find('#yellow-message-bar').exists()).toBeTruthy()

    // trigger back button
    wrapper.find('#btn-stacked-back').trigger('click')
    await Vue.nextTick()

    // message is removed once out of review screen
    expect(wrapper.find('#yellow-message-bar').exists()).toBeFalsy()
  })

  it('should render Confirm Completion component on the Review screen', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.$data.dataLoaded = true
    await Vue.nextTick()

    expect(wrapper.find('#transfer-confirm-section').exists()).toBeFalsy()

    await triggerUnsavedChange()
    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await Vue.nextTick()

    expect(wrapper.find('#transfer-confirm-section').exists()).toBeTruthy()

    const confirmCompletionCard = wrapper.find(getTestId('confirm-completion-card'))
    expect(confirmCompletionCard.exists()).toBeTruthy()
    expect(confirmCompletionCard.classes('border-error-left')).toBeFalsy()
    expect(confirmCompletionCard.find(getTestId('confirm-completion-checkbox')).exists()).toBeTruthy()
    expect(confirmCompletionCard.find('.confirm-checkbox').text()).toContain(LEGAL_NAME)
  })

  it('should render read only home owners on the Review screen', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.$data.dataLoaded = true
    await Vue.nextTick()

    // TODO: check that removed owners are not displayed in review
    const owners = [mockedRemovedPerson] as MhrRegistrationHomeOwnerIF[] // same IF for Transfer and Registration
    const homeOwnerGroup = [
      mockMhrTransferCurrentHomeOwner,
      { groupId: 1, owners: owners }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerGroup)
    expect(wrapper.findComponent(HomeOwners).findComponent(HomeOwnersTable).exists()).toBeTruthy()
    const ownersTable = wrapper.findComponent(HomeOwners).findComponent(HomeOwnersTable)

    // check owners are in table
    expect(ownersTable.props().homeOwners.length).toBe(2)

    // review table doesn't exist yet
    expect(wrapper.find('#owners-review').exists()).toBeFalsy()

    await triggerUnsavedChange()
    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await Vue.nextTick()

    // review table renders
    const homeOwnerReadOnly = wrapper.find('#owners-review')
    expect(homeOwnerReadOnly.exists()).toBeTruthy()

    // values remain in table
    expect(wrapper.findComponent(HomeOwners).props().isReadonlyTable).toBeTruthy()
    expect(ownersTable.props().homeOwners.length).toBe(2)
  })

  it('should validate and show components errors on Review screen', async () => {
    setupCurrentHomeOwners()
    wrapper.vm.$data.dataLoaded = true
    await Vue.nextTick()

    const feeSummaryContainer = wrapper.find(getTestId('fee-summary'))
    expect(feeSummaryContainer.find('.err-msg').exists()).toBeFalsy()

    await triggerUnsavedChange()
    await enterTransferDetailsFields(wrapper.findComponent(TransferDetails))

    await wrapper.find('#btn-stacked-submit').trigger('click')
    await Vue.nextTick()

    expect(wrapper.find('#mhr-information-header').text()).toContain('Review and Confirm')
    expect(feeSummaryContainer.find('.err-msg').exists()).toBeFalsy()
    expect(wrapper.findAll('.border-error-left').length).toBe(0)
    wrapper.find(getTestId('attn-ref-number-field')).setValue('5'.repeat(45))
    await Vue.nextTick()

    wrapper.find('#btn-stacked-submit').trigger('click')
    await Vue.nextTick()
    await Vue.nextTick()

    // should show 3 errors for Ref Num, Confirm and Auth components
    expect(feeSummaryContainer.find('.err-msg').exists()).toBeTruthy()
    expect(wrapper.findAll('.border-error-left').length).toBe(3)
  })
})
