import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

import { HomeOwners } from '@/views'
import { AddEditHomeOwner, HomeOwnersTable, HomeOwnerGroups } from '@/components/mhrRegistration/HomeOwners'
import { SimpleHelpToggle } from '@/components/common'
import {
  mockedExecutor,
  mockedPerson,
  mockedOrganization,
  mockedAddedPerson,
  mockedAddedOrganization,
  mockedRemovedPerson,
  mockedRemovedOrganization
} from './test-data'
import { getTestId } from './utils'
import { MhrRegistrationHomeOwnerGroupIF } from '@/interfaces'
import { ApiTransferTypes, UITransferTypes, HomeTenancyTypes } from '@/enums'
import { SupportingDocuments, TransferType } from '@/components/mhrTransfers'
import { transferSupportingDocuments } from '@/resources'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)

  document.body.setAttribute('data-app', 'true')
  return mount(HomeOwners, {
    localVue,
    propsData: {
      isMhrTransfer: true
    },
    store,
    vuetify
  })
}

// Error message class selector
const ERROR_MSG = '.error--text .v-messages__message'

describe('Home Owners', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent()

    await store.dispatch('setMhrTransferType', {
      transferType: ApiTransferTypes.SALE_OR_GIFT,
      textLabel: UITransferTypes.SALE_OR_GIFT
    })
  })
  afterEach(() => {
    wrapper.destroy()
  })

  // Helper functions

  const openAddPerson = async () => {
    const homeOwnersSection = wrapper.findComponent(HomeOwners)
    await homeOwnersSection.find(getTestId('add-person-btn'))?.trigger('click')
    await Vue.nextTick()
    expect(homeOwnersSection.findComponent(AddEditHomeOwner).exists()).toBeTruthy()
    expect(homeOwnersSection.findComponent(HomeOwnerGroups).exists()).toBeTruthy()
  }

  const openAddOrganization = async () => {
    const homeOwnersSection = wrapper.findComponent(HomeOwners)
    await homeOwnersSection.find(getTestId('add-org-btn'))?.trigger('click')
    await Vue.nextTick()
    expect(homeOwnersSection.findComponent(AddEditHomeOwner).exists()).toBeTruthy()
    expect(homeOwnersSection.findComponent(HomeOwnerGroups).exists()).toBeTruthy()
  }

  const clickCancelAddOwner = async () => {
    const homeOwnersSection = wrapper.findComponent(HomeOwners)
    const addOwnerSection = homeOwnersSection.findComponent(AddEditHomeOwner)
    expect(addOwnerSection.exists).toBeTruthy()
    const cancelBtn = addOwnerSection.find(getTestId('cancel-btn'))
    expect(cancelBtn.exists()).toBeTruthy()
    await cancelBtn.trigger('click')
    await Vue.nextTick()
    expect(homeOwnersSection.findComponent(AddEditHomeOwner).exists()).toBeFalsy()
  }

  const clickDoneAddOwner = async () => {
    const addOwnerSection = wrapper.findComponent(AddEditHomeOwner)
    const doneBtn = addOwnerSection.find(getTestId('done-btn'))
    expect(doneBtn.exists()).toBeTruthy()

    await doneBtn.trigger('click')
    // should not be any errors
    // expect(addOwnerSection.findAll(ERROR_MSG).length).toBe(0)
    setTimeout(async () => {
      expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy() // Hidden by default
    }, 500)
  }

  const selectTransferType = async (transferType: ApiTransferTypes) => {
    await store.dispatch('setMhrTransferType', { transferType: transferType })
    await Vue.nextTick()
  }

  // Tests

  it('renders Home Owners and its sub components', () => {
    expect(wrapper.findComponent(HomeOwners).exists()).toBeTruthy()
    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy() // Hidden by default
    expect(wrapper.findComponent(HomeOwnersTable).exists()).toBeTruthy()
    expect(wrapper.findComponent(SimpleHelpToggle).exists()).toBeFalsy() // Verify it doesn't render in Transfers
  })

  it('renders Add Edit Home Owner and its sub components', async () => {
    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBe(false) // Hidden by default
    openAddPerson()
    await Vue.nextTick()
    await Vue.nextTick()
    clickCancelAddOwner()
    await Vue.nextTick()
    await Vue.nextTick()
    openAddOrganization()
    await Vue.nextTick()
    await Vue.nextTick()
    clickCancelAddOwner()
  })

  it('displays CURRENT owners (Persons and Orgs)', async () => {
    const homeOwnerGroup = [{ groupId: 1, owners: [mockedPerson] }] as MhrRegistrationHomeOwnerGroupIF[]

    // add a person
    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerGroup)

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()

    let ownersTable = wrapper.findComponent(HomeOwners).findComponent(HomeOwnersTable)

    // renders all fields

    expect(ownersTable.exists()).toBeTruthy()
    expect(ownersTable.text()).toContain(mockedPerson.individualName.first)
    expect(ownersTable.text()).toContain(mockedPerson.individualName.last)
    expect(ownersTable.text()).toContain(mockedPerson.individualName.middle)
    expect(ownersTable.text()).toContain(mockedPerson.suffix)
    expect(ownersTable.text()).toContain(mockedPerson.address.street)
    expect(ownersTable.text()).toContain(mockedPerson.address.streetAdditional)
    expect(ownersTable.text()).toContain(mockedPerson.address.city)
    expect(ownersTable.text()).toContain(mockedPerson.address.region)
    expect(ownersTable.text()).toContain('Canada')
    expect(ownersTable.text()).toContain(mockedPerson.address.postalCode)
    // there should be no grouping shown in the table because we didn't select a group during add
    expect(ownersTable.text()).not.toContain('Group 1')

    // there should be no 'Added' badge shown for the Current Owners
    const addedBadge = ownersTable.find(getTestId('owner-added-badge'))
    expect(addedBadge.exists()).toBeFalsy()

    // add an organization
    homeOwnerGroup[0].owners.push(mockedOrganization)
    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerGroup)

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()

    ownersTable = wrapper.findComponent(HomeOwners).findComponent(HomeOwnersTable)

    // renders all fields
    expect(ownersTable.exists()).toBeTruthy()
    expect(ownersTable.text()).toContain(mockedOrganization.organizationName)
    expect(ownersTable.text()).toContain(mockedOrganization.suffix)
    expect(ownersTable.text()).toContain(mockedOrganization.address.street)
    expect(ownersTable.text()).toContain(mockedOrganization.address.streetAdditional)
    expect(ownersTable.text()).toContain(mockedOrganization.address.city)
    expect(ownersTable.text()).toContain(mockedOrganization.address.region)
    expect(ownersTable.text()).toContain('Canada')
    expect(ownersTable.text()).toContain(mockedOrganization.address.postalCode)
    // there should be no grouping shown in the table because we didn't select a group during add
    expect(ownersTable.text()).not.toContain('Group 1')
  })

  it('displays badge for ADDED owners (Persons and Orgs)', async () => {
    const homeOwnerGroup = [{ groupId: 1, owners: [mockedAddedPerson, mockedAddedOrganization] }]

    // add a person
    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerGroup)

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()

    let ownersTable = wrapper.findComponent(HomeOwners).findComponent(HomeOwnersTable)

    // renders all fields

    expect(ownersTable.exists()).toBeTruthy()
    expect(ownersTable.text()).toContain(mockedPerson.individualName.first)
    expect(ownersTable.text()).toContain(mockedPerson.individualName.last)
    expect(ownersTable.text()).toContain(mockedPerson.individualName.middle)
    expect(ownersTable.text()).toContain(mockedPerson.suffix)
    expect(ownersTable.text()).toContain(mockedPerson.address.street)
    expect(ownersTable.text()).toContain(mockedPerson.address.streetAdditional)
    expect(ownersTable.text()).toContain(mockedPerson.address.city)
    expect(ownersTable.text()).toContain(mockedPerson.address.region)
    expect(ownersTable.text()).toContain('Canada')
    expect(ownersTable.text()).toContain(mockedPerson.address.postalCode)
    // there should be no grouping shown in the table because we didn't select a group during add
    expect(ownersTable.text()).not.toContain('Group 1')

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()

    ownersTable = wrapper.findComponent(HomeOwners).findComponent(HomeOwnersTable)

    // renders all fields
    expect(ownersTable.exists()).toBeTruthy()
    expect(ownersTable.text()).toContain(mockedOrganization.organizationName)
    expect(ownersTable.text()).toContain(mockedOrganization.suffix)
    expect(ownersTable.text()).toContain(mockedOrganization.address.street)
    expect(ownersTable.text()).toContain(mockedOrganization.address.streetAdditional)
    expect(ownersTable.text()).toContain(mockedOrganization.address.city)
    expect(ownersTable.text()).toContain(mockedOrganization.address.region)
    expect(ownersTable.text()).toContain('Canada')
    expect(ownersTable.text()).toContain(mockedOrganization.address.postalCode)
    // there should be no grouping shown in the table because we didn't select a group during add
    expect(ownersTable.text()).not.toContain('Group 1')

    // there should be 'Added' badges shown for each of the Added Owners
    const addedBadges = ownersTable.findAll(getTestId('owner-added-badge'))
    expect(addedBadges.at(0).exists()).toBe(true)
    expect(addedBadges.at(1).exists()).toBe(true)
  })

  it('displays badge for REMOVED owners (Persons and Orgs)', async () => {
    const homeOwnerGroup = [{ groupId: 1, owners: [mockedRemovedPerson, mockedRemovedOrganization] }]

    // add a person
    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerGroup)

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()

    let ownersTable = wrapper.findComponent(HomeOwners).findComponent(HomeOwnersTable)

    // renders all fields

    expect(ownersTable.exists()).toBeTruthy()
    expect(ownersTable.text()).toContain(mockedPerson.individualName.first)
    expect(ownersTable.text()).toContain(mockedPerson.individualName.last)
    expect(ownersTable.text()).toContain(mockedPerson.individualName.middle)
    expect(ownersTable.text()).toContain(mockedPerson.suffix)
    expect(ownersTable.text()).toContain(mockedPerson.address.street)
    expect(ownersTable.text()).toContain(mockedPerson.address.streetAdditional)
    expect(ownersTable.text()).toContain(mockedPerson.address.city)
    expect(ownersTable.text()).toContain(mockedPerson.address.region)
    expect(ownersTable.text()).toContain('Canada')
    expect(ownersTable.text()).toContain(mockedPerson.address.postalCode)
    // there should be no grouping shown in the table because we didn't select a group during add
    expect(ownersTable.text()).not.toContain('Group 1')

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()

    ownersTable = wrapper.findComponent(HomeOwners).findComponent(HomeOwnersTable)

    // renders all fields
    expect(ownersTable.exists()).toBeTruthy()
    expect(ownersTable.text()).toContain(mockedOrganization.organizationName)
    expect(ownersTable.text()).toContain(mockedOrganization.suffix)
    expect(ownersTable.text()).toContain(mockedOrganization.address.street)
    expect(ownersTable.text()).toContain(mockedOrganization.address.streetAdditional)
    expect(ownersTable.text()).toContain(mockedOrganization.address.city)
    expect(ownersTable.text()).toContain(mockedOrganization.address.region)
    expect(ownersTable.text()).toContain('Canada')
    expect(ownersTable.text()).toContain(mockedOrganization.address.postalCode)
    // there should be no grouping shown in the table because we didn't select a group during add
    expect(ownersTable.text()).not.toContain('Group 1')

    // there should be 'Added' badges shown for each of the Added Owners
    const removedBadges = ownersTable.findAll(getTestId('owner-removed-badge'))
    expect(removedBadges.at(0).exists()).toBe(true)
    expect(removedBadges.at(1).exists()).toBe(true)
  })

  it('TRANS WILL Flow: display Supporting Document component for deleted sole Owner and add Executor', async () => {
    // setup transfer type to test
    const TRANSFER_TYPE = ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL

    const homeOwnerGroup = [{ groupId: 1, owners: [mockedPerson] }]
    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerGroup)

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()

    const homeOwnersTable = wrapper.findComponent(HomeOwnersTable)
    // Add Person button should not be visible
    expect(homeOwnersTable.find(getTestId('add-person-btn')).exists()).toBeFalsy()

    await selectTransferType(TRANSFER_TYPE)

    // Add Person button and error should not exist
    expect(homeOwnersTable.find(getTestId('add-person-btn')).exists()).toBeFalsy()
    expect(homeOwnersTable.find(getTestId('transfer-table-error')).exists()).toBeFalsy()

    // delete the sole owner
    await homeOwnersTable.find(getTestId('table-delete-btn')).trigger('click')

    const deceasedBadge = homeOwnersTable.find(getTestId('owner-removed-badge'))
    expect(deceasedBadge.exists()).toBeTruthy()
    expect(deceasedBadge.text()).toContain('DECEASED')

    const supportingDocumentsComponent = wrapper.findComponent(SupportingDocuments)
    expect(supportingDocumentsComponent.isVisible()).toBeTruthy()

    expect(supportingDocumentsComponent.text()).toContain(transferSupportingDocuments[TRANSFER_TYPE].optionOne.text)
    expect(supportingDocumentsComponent.text()).toContain(transferSupportingDocuments[TRANSFER_TYPE].optionTwo.text)

    const radioButtonGrantOfProbate = <HTMLInputElement>(
      supportingDocumentsComponent.find(getTestId('supporting-doc-option-one')).element
    )
    // check that Grant of Probate radio button option is selected by default
    expect(radioButtonGrantOfProbate.checked).toBeTruthy()

    const radioButtonDeathCert = <HTMLInputElement>(
      supportingDocumentsComponent.find(getTestId('supporting-doc-option-two'))).element

    // check disabled state of Death Certificate radio button
    expect(radioButtonDeathCert.disabled).toBeTruthy()

    await wrapper.findComponent(HomeOwners).find(getTestId('add-person-btn'))?.trigger('click')
    await Vue.nextTick()

    const addEditHomeOwner = wrapper.findComponent(AddEditHomeOwner)
    expect(addEditHomeOwner.find('#executor-option').exists()).toBeTruthy()

    // check that Executor radio button option is selected by default
    const executorRadioButton = <HTMLInputElement>(addEditHomeOwner.find('#executor-option')).element
    expect(executorRadioButton.checked).toBeTruthy()

    // check that suffix field value is pre-populated with the name of deleted person
    const suffix = <HTMLInputElement>(addEditHomeOwner.find(getTestId('suffix'))).element
    const { first, middle, last } = mockedPerson.individualName
    expect(suffix.value).toBe(`Executor of the will of ${first} ${middle} ${last}`)
  })

  it('TRANS WILL Flow: displays correct tenancy type in Executor scenarios', async () => {
    // setup transfer type to test
    const TRANSFER_TYPE = ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL

    let homeOwnerGroup = [{ groupId: 1, owners: [mockedPerson] }]
    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerGroup)

    const homeOwnersTable = wrapper.findComponent(HomeOwnersTable)

    await selectTransferType(TRANSFER_TYPE)

    // Tenancy type should be SOLE before changes made
    expect(wrapper.findComponent(HomeOwners).vm.$data.getHomeOwners.length).toBe(1)
    expect(
      wrapper
        .findComponent(HomeOwners)
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.SOLE)

    // add executor
    homeOwnerGroup[0].owners.push(mockedExecutor)
    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerGroup)

    // Tenancy type should be N/A due to mix of Executor and living owner
    expect(wrapper.findComponent(HomeOwners).vm.$data.getHomeOwners.length).toBe(2)
    expect(
      wrapper
        .findComponent(HomeOwners)
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.NA)

    // reset owners
    homeOwnerGroup = [{ groupId: 1, owners: [mockedPerson] }]
    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerGroup)

    // delete original owner
    await homeOwnersTable.find(getTestId('table-delete-btn')).trigger('click')

    // Tenancy type should be N/A with no living owners
    expect(wrapper.findComponent(HomeOwners).vm.$data.getHomeOwners.length).toBe(1)
    expect(
      wrapper
        .findComponent(HomeOwners)
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.NA)

    // add executor
    homeOwnerGroup[0].owners.push(mockedExecutor)
    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerGroup)

    // Tenancy type should be SOLE
    expect(wrapper.findComponent(HomeOwners).vm.$data.getHomeOwners.length).toBe(2)
    expect(
      wrapper
        .findComponent(HomeOwners)
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.SOLE)

    // add another executor
    homeOwnerGroup[0].owners.push(mockedExecutor)
    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerGroup)

    // Tenancy type should be N/A due to multiple Executors
    expect(wrapper.findComponent(HomeOwners).vm.$data.getHomeOwners.length).toBe(3)
    expect(
      wrapper
        .findComponent(HomeOwners)
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.NA)
  })
})
