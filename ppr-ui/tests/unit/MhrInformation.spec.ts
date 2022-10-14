// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import VueRouter from 'vue-router'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'

// local components
import { HomeOwners, MhrInformation } from '@/views'
import { StickyContainer } from '@/components/common'
import mockRouter from './MockRouter'
import { RouteNames } from '@/enums'
import { HomeOwnersTable } from '@/components/mhrRegistration/HomeOwners'
import { getTestId } from './utils'
import { mockedOrganization, mockedPerson, mockMhrTransferCurrentHomeOwner } from './test-data'
import { MhrRegistrationHomeOwnerGroupIF, MhrRegistrationHomeOwnerIF } from '@/interfaces'
import { nextTick } from '@vue/composition-api'
import { TransferDetails } from '@/components/mhrTransfers'

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

// TODO: Remove after API updates to include the ID for Owners
function addIDsForOwners(ownersGroups): Array<any> {
  // Create an ID to each individual owner for UI Tracking
  ownersGroups.forEach(ownerGroup => {
    for (const [index, owner] of ownerGroup.owners.entries()) {
      owner.id = ownerGroup.groupId + (index + 1)
    }
  })

  return ownersGroups
}

describe('Mhr Information', () => {
  let wrapper: Wrapper<any>
  const currentAccount = {
    id: 'test_id'
  }
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')
  sessionStorage.setItem('CURRENT_ACCOUNT', JSON.stringify(currentAccount))
  sessionStorage.setItem('AUTH_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/')

  beforeEach(async () => {
    wrapper = createComponent()
    await store.dispatch('setMhrTransferCurrentHomeOwnerGroups', [mockMhrTransferCurrentHomeOwner])
    // TODO: Remove after API updates to include the ID for Owners
    const homeOwnerWithIdsArray = addIDsForOwners([mockMhrTransferCurrentHomeOwner])
    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerWithIdsArray)
    wrapper.vm.$data.dataLoaded = true

    expect(wrapper.props().isMhrTransfer).toBe(true)
    expect(wrapper.vm.$data.getMhrTransferCurrentHomeOwners.length).toBe(1)
    expect(wrapper.vm.$data.getMhrTransferHomeOwners.length).toBe(1)
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders and displays the Mhr Information View', async () => {
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
    const mhrInformationComponent = wrapper.findComponent(MhrInformation)
    expect(mhrInformationComponent.exists()).toBeTruthy()
    wrapper.vm.$data.dataLoaded = true
    await nextTick()

    expect(mhrInformationComponent.findComponent(HomeOwnersTable).exists()).toBeTruthy()

    const owners = [mockedPerson] as MhrRegistrationHomeOwnerIF[] // same IF for Transfer and Registration
    const homeOwnerGroup = [
      mockMhrTransferCurrentHomeOwner,
      { groupId: '2', owners: owners }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerGroup)

    const ownersTable = mhrInformationComponent.findComponent(HomeOwners).findComponent(HomeOwnersTable)

    const newlyAddedOwner = ownersTable.find(getTestId(`owner-info-${mockedPerson.id}`))
    expect(newlyAddedOwner.text()).toContain(mockedPerson.individualName.first)
    expect(newlyAddedOwner.text()).toContain(mockedPerson.individualName.last)

    const addedBadge = newlyAddedOwner.find(getTestId('owner-added-badge'))
    expect(addedBadge.isVisible()).toBeTruthy()
  })

  it('should render Transfer Details component', async () => {
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
})
