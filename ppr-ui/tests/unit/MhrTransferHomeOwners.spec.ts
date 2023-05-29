import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

import { HomeOwners } from '@/views'
import {
  AddEditHomeOwner,
  HomeOwnersTable,
  HomeOwnerGroups,
  TableGroupHeader
} from '@/components/mhrRegistration/HomeOwners'
import { InfoChip, SharedDatePicker, SimpleHelpToggle } from '@/components/common'
import {
  mockedExecutor,
  mockedPerson,
  mockedOrganization,
  mockedAddedPerson,
  mockedAddedOrganization,
  mockedRemovedPerson,
  mockedRemovedOrganization,
  mockMhrTransferCurrentHomeOwnerGroup,
  mockedPerson2,
  mockedAddedExecutor,
  mockedAddedAdministrator,
  mockedAdministrator
} from './test-data'
import { getTestId } from './utils'
import { MhrRegistrationHomeOwnerGroupIF, MhrRegistrationHomeOwnerIF, TransferTypeSelectIF } from '@/interfaces'
import {
  ActionTypes,
  ApiHomeTenancyTypes,
  ApiTransferTypes,
  HomeOwnerPartyTypes,
  HomeTenancyTypes,
  UITransferTypes
} from '@/enums'
import { DeathCertificate, SupportingDocuments } from '@/components/mhrTransfers'
import { transferSupportingDocuments, transfersErrors, MixedRolesErrors } from '@/resources'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)

  document.body.setAttribute('data-app', 'true')
  return mount((HomeOwners as any), {
    localVue,
    propsData: {
      appReady: true,
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

    await store.setMhrTransferType({
      transferType: ApiTransferTypes.SALE_OR_GIFT,
      textLabel: UITransferTypes.SALE_OR_GIFT
    })
  })
  afterEach(() => {
    wrapper.destroy()
  })

  // Helper functions

  const openAddPerson = async () => {
    const homeOwnersSection = wrapper
    await homeOwnersSection.find(getTestId('add-person-btn'))?.trigger('click')
    await nextTick()
    expect(homeOwnersSection.findComponent(AddEditHomeOwner).exists()).toBeTruthy()
    expect(homeOwnersSection.findComponent(HomeOwnerGroups).exists()).toBeTruthy()
  }

  const openAddOrganization = async () => {
    const homeOwnersSection = wrapper
    await homeOwnersSection.find(getTestId('add-org-btn'))?.trigger('click')
    await nextTick()
    expect(homeOwnersSection.findComponent(AddEditHomeOwner).exists()).toBeTruthy()
    expect(homeOwnersSection.findComponent(HomeOwnerGroups).exists()).toBeTruthy()
  }

  const clickCancelAddOwner = async () => {
    const homeOwnersSection = wrapper
    const addOwnerSection = homeOwnersSection.findComponent(AddEditHomeOwner)
    expect(addOwnerSection.exists).toBeTruthy()
    const cancelBtn = addOwnerSection.find(getTestId('cancel-btn'))
    expect(cancelBtn.exists()).toBeTruthy()
    await cancelBtn.trigger('click')
    await nextTick()
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
    await store.setMhrTransferType({ transferType: transferType } as TransferTypeSelectIF)
    await nextTick()
  }

  // Tests

  it('renders Home Owners and its sub components', () => {
    expect(wrapper.exists()).toBeTruthy()
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
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()

    let ownersTable = wrapper.findComponent(HomeOwnersTable)

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
    const addedBadge = ownersTable.find(getTestId('ADDED-badge'))
    expect(addedBadge.exists()).toBeFalsy()

    // add an organization
    homeOwnerGroup[0].owners.push(mockedOrganization)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()

    ownersTable = wrapper.findComponent(HomeOwnersTable)

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
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()

    let ownersTable = wrapper.findComponent(HomeOwnersTable)

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

    ownersTable = wrapper.findComponent(HomeOwnersTable)

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
    const addedBadges = ownersTable.findAll(getTestId('ADDED-badge'))
    expect(addedBadges.at(0).exists()).toBe(true)
    expect(addedBadges.at(1).exists()).toBe(true)
  })

  it('displays badge for REMOVED owners (Persons and Orgs)', async () => {
    const homeOwnerGroup = [{ groupId: 1, owners: [mockedRemovedPerson, mockedRemovedOrganization] }]

    // add a person
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()

    let ownersTable = wrapper.findComponent(HomeOwnersTable)

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

    ownersTable = wrapper.findComponent(HomeOwnersTable)

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

    // there should be 'DELETED' badges shown for each of the Deleted Owners
    const removedBadges = ownersTable.findAll(getTestId('DELETED-badge'))
    expect(removedBadges.at(0).exists()).toBe(true)
    expect(removedBadges.at(1).exists()).toBe(true)
  })

  it('should display a DELETED home owner group', async () => {
    const homeOwnerGroups = [
      {
        groupId: 1,
        interest: 'Undivided',
        interestNumerator: 2,
        interestDenominator: 4,
        owners: [mockedPerson]
      },
      {
        groupId: 2,
        interest: 'Undivided',
        action: 'REMOVED',
        interestNumerator: 2,
        interestDenominator: 4,
        owners: [mockedOrganization]
      }
    ]

    // add a person
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroups)

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()
    // check current Owners and Groups
    wrapper.vm.setShowGroups(true)
    await Vue.nextTick()

    const ownersTable = wrapper.findComponent(HomeOwnersTable)

    // renders all fields
    expect(ownersTable.exists()).toBe(true)
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
    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()

    // Verify Headers
    expect(ownersTable.findAllComponents(TableGroupHeader).length).toBe(2)
    expect(ownersTable.text()).toContain('Group 1')
    expect(ownersTable.text()).toContain('Group 2')

    // there should be 'DELETED' badges shown for the Deleted Group
    expect(ownersTable.findAllComponents(TableGroupHeader).at(1)
      .findComponent(InfoChip).text()).toContain('REMOVED')

    wrapper.vm.setShowGroups(false)
  })

  it('should display a CHANGED a home owner group', async () => {
    const homeOwnerGroups = [
      {
        groupId: 1,
        interest: 'Undivided',
        interestNumerator: 2,
        interestDenominator: 4,
        owners: [mockedPerson]
      },
      {
        groupId: 2,
        interest: 'Undivided',
        action: 'CHANGED',
        interestNumerator: 3,
        interestDenominator: 4,
        owners: [mockedOrganization]
      }
    ]

    // add a person
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroups)

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()
    // check current Owners and Groups
    wrapper.vm.setShowGroups(true)
    await Vue.nextTick()

    const ownersTable = wrapper.findComponent(HomeOwnersTable)

    // Verify Headers
    expect(ownersTable.findAllComponents(TableGroupHeader).length).toBe(2)
    expect(ownersTable.text()).toContain('Group 1')
    expect(ownersTable.text()).toContain('Group 2')

    // there should be 'CHANGED' badges shown for the Changed Group
    expect(ownersTable.findAllComponents(TableGroupHeader).at(1)
      .findComponent(InfoChip).text()).toContain('CHANGED')

    wrapper.vm.setShowGroups(false)
  })

  it('TRANS SALE GIFT: validations with sole Owner in one group', async () => {
    // reset transfer type
    await selectTransferType(null)

    const TRANSFER_TYPE = ApiTransferTypes.SALE_OR_GIFT

    const homeOwnerGroup: MhrRegistrationHomeOwnerGroupIF[] = [{ groupId: 1, owners: [mockedPerson], type: '' }]

    await store.setMhrTransferCurrentHomeOwnerGroups(homeOwnerGroup)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    await selectTransferType(TRANSFER_TYPE)

    const homeOwners: Wrapper<any> = wrapper
    expect(homeOwners.find(getTestId('table-delete-btn')).exists()).toBeTruthy()
    await homeOwners.find(getTestId('table-delete-btn')).trigger('click')
    await Vue.nextTick()

    const allDeletedBadges = homeOwners.findAll(getTestId('DELETED-badge'))
    expect(allDeletedBadges.length).toBe(1)

    expect(homeOwners.find(getTestId('invalid-group-msg')).exists()).toBeFalsy()
    expect(homeOwners.find(getTestId('no-data-msg')).exists()).toBeTruthy()
    expect(homeOwners.find(getTestId('no-data-msg')).text()).toContain('No owners added yet.')

    const deletedOwner: MhrRegistrationHomeOwnerIF =
      homeOwners.vm.getMhrTransferHomeOwnerGroups[0].owners[0]

    const addedOwner: MhrRegistrationHomeOwnerIF = {
      ...mockedAddedPerson,
      ownerId: 11,
      groupId: 1
    }

    await store.setMhrTransferHomeOwnerGroups(
      [{ groupId: 1, owners: [deletedOwner, addedOwner] }] as MhrRegistrationHomeOwnerGroupIF[])

    // check number of owners and that all errors are cleared
    expect(homeOwners.vm.getHomeOwners.length).toBe(2)
    expect(homeOwners.text()).not.toContain('Group 1')
    expect(homeOwners.find(getTestId('invalid-group-msg')).exists()).toBeFalsy()
    expect(homeOwners.find(getTestId('no-data-msg')).exists()).toBeFalsy()
  })

  it('TRANS WILL: display Supporting Document component for deleted sole Owner and add Executor', async () => {
    // reset transfer type
    await selectTransferType(null)

    // setup transfer type to test
    const TRANSFER_TYPE = ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL

    const homeOwnerGroup: MhrRegistrationHomeOwnerGroupIF[] = [{ groupId: 1, owners: [mockedPerson], type: '' }]

    await store.setMhrTransferCurrentHomeOwnerGroups(homeOwnerGroup)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()

    const homeOwners = wrapper

    // Add Person button should not be visible
    expect(homeOwners.find(getTestId('add-person-btn')).exists()).toBeFalsy()

    await selectTransferType(TRANSFER_TYPE)

    expect(homeOwners.find(getTestId('transfer-table-error')).exists()).toBeFalsy()

    expect(homeOwners.vm.getMhrTransferCurrentHomeOwnerGroups[0].owners.length ===
      homeOwnerGroup.length).toBeTruthy()
    expect(homeOwners.vm.getHomeOwners[0].individualName.first ===
      homeOwnerGroup[0].owners[0].individualName.first).toBeTruthy()

    expect(homeOwners.find(getTestId('table-delete-btn')).exists()).toBeTruthy()
    // delete the sole owner
    await homeOwners.find(getTestId('table-delete-btn')).trigger('click')

    const deceasedBadge = homeOwners.find(getTestId('DECEASED-badge'))
    expect(deceasedBadge.exists()).toBeTruthy()
    expect(deceasedBadge.text()).toContain('DECEASED')

    const supportingDocuments = wrapper.findComponent(SupportingDocuments)
    expect(supportingDocuments.isVisible()).toBeTruthy()

    expect(supportingDocuments.text()).toContain(transferSupportingDocuments[TRANSFER_TYPE].optionOne.text)
    expect(supportingDocuments.text()).toContain(transferSupportingDocuments[TRANSFER_TYPE].optionTwo.text)

    const radioButtonGrantOfProbate = <HTMLInputElement>(
      supportingDocuments.find(getTestId('supporting-doc-option-one')).element
    )
    // check that Grant of Probate radio button option is selected by default
    expect(radioButtonGrantOfProbate.checked).toBeTruthy()

    const radioButtonDeathCert = <HTMLInputElement>(
      supportingDocuments.find(getTestId('supporting-doc-option-two'))).element

    // check disabled state of Death Certificate radio button
    expect(radioButtonDeathCert.disabled).toBeTruthy()

    await wrapper.find(getTestId('add-person-btn'))?.trigger('click')
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

  it('TRANS WILL: displays correct tenancy type in Executor scenarios', async () => {
    // setup transfer type to test
    const TRANSFER_TYPE = ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL

    let homeOwnerGroup = [{ groupId: 1, owners: [mockedPerson] }]
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    const homeOwnersTable = wrapper.findComponent(HomeOwnersTable)

    await selectTransferType(TRANSFER_TYPE)

    // Tenancy type should be SOLE before changes made
    expect(wrapper.vm.getHomeOwners.length).toBe(1)
    expect(
      wrapper
        .findComponent(HomeOwners)
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.SOLE)

    // add executor
    homeOwnerGroup[0].owners.push(mockedExecutor)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    // Tenancy type should be N/A due to mix of Executor and living owner
    expect(wrapper.vm.getHomeOwners.length).toBe(2)
    expect(
      wrapper
        .findComponent(HomeOwners)
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.NA)

    // reset owners
    homeOwnerGroup = [{ groupId: 1, owners: [mockedPerson] }]
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    // delete original owner
    await homeOwnersTable.find(getTestId('table-delete-btn')).trigger('click')

    // Tenancy type should be N/A with no living owners
    expect(wrapper.vm.getHomeOwners.length).toBe(1)
    expect(
      wrapper
        .findComponent(HomeOwners)
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.NA)

    // add executor
    homeOwnerGroup[0].owners.push(mockedExecutor)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    // Tenancy type should be SOLE
    expect(wrapper.vm.getHomeOwners.length).toBe(2)
    expect(
      wrapper
        .findComponent(HomeOwners)
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.SOLE)

    // add another executor
    homeOwnerGroup[0].owners.push(mockedExecutor)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    // Tenancy type should be N/A due to multiple Executors
    expect(wrapper.vm.getHomeOwners.length).toBe(3)
    expect(
      wrapper
        .findComponent(HomeOwners)
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.NA)
  })

  it('TRANS Sale or Gift: validations for mixed owners types in the table', async () => {
    // reset transfer type
    await selectTransferType(null)

    await selectTransferType(ApiTransferTypes.SALE_OR_GIFT)

    const homeOwnerGroup: MhrRegistrationHomeOwnerGroupIF[] = [
      {
        groupId: 1,
        owners: [
          {
            ...mockedExecutor,
            id: '1',
            partyType: HomeOwnerPartyTypes.EXECUTOR
          } as MhrRegistrationHomeOwnerIF,
        {
          ...mockedPerson,
          id: '2',
          partyType: HomeOwnerPartyTypes.OWNER_IND,
          action: ActionTypes.ADDED
        } as MhrRegistrationHomeOwnerIF],
        type: ''
      }
    ]
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    const homeOwners = wrapper
    const groupError = homeOwners.find(getTestId('invalid-group-msg'))

    expect(groupError.text()).toContain(MixedRolesErrors.hasMixedOwnerTypes)

    // add one more owner to the second group to trigger a new error message
    homeOwnerGroup.push({
      groupId: 2,
      owners: [mockedPerson],
      type: ''
    } as MhrRegistrationHomeOwnerGroupIF)

    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    expect(groupError.text()).toContain(MixedRolesErrors.hasMixedOwnerTypesInGroup)
  })

  it('TRANS WILL: validations with sole Owner in one group', async () => {
    // reset transfer type
    await selectTransferType(null)

    const TRANSFER_TYPE = ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL
    const homeOwnerGroup: MhrRegistrationHomeOwnerGroupIF[] = [{ groupId: 1, owners: [mockedPerson], type: '' }]

    await store.setMhrTransferCurrentHomeOwnerGroups(homeOwnerGroup)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    await selectTransferType(TRANSFER_TYPE)

    const homeOwners = wrapper

    const invalidGroupMsg = homeOwners.find(getTestId('invalid-group-msg'))
    expect(invalidGroupMsg.exists()).toBeFalsy()

    await homeOwners.find(getTestId('table-delete-btn')).trigger('click')

    // group error message should be displayed
    expect(homeOwners.find(getTestId('invalid-group-msg')).exists()).toBeTruthy()
    expect(homeOwners.find(getTestId('invalid-group-msg')).text()).toContain('Must contain at least one executor.')

    const deletedOwner: MhrRegistrationHomeOwnerIF =
      homeOwners.vm.getMhrTransferHomeOwnerGroups[0].owners[0]

    const addedExecutor: MhrRegistrationHomeOwnerIF = {
      ...mockedAddedPerson,
      ownerId: 11,
      groupId: 1,
      partyType: HomeOwnerPartyTypes.EXECUTOR,
      type: ApiHomeTenancyTypes.SOLE
    }

    // add an executor to the group
    await store.setMhrTransferHomeOwnerGroups(
      [{ groupId: 1, owners: [deletedOwner, addedExecutor] }] as MhrRegistrationHomeOwnerGroupIF[])

    // make sure current owner group is not altered
    expect(homeOwners.vm.getMhrTransferCurrentHomeOwnerGroups[0].owners.length).toBe(1)

    const homeOwnersData = homeOwners.vm.getHomeOwners
    expect(homeOwnersData.length).toBe(2)

    // make sure all owners are in the same group, that is not shown for Sole Owner tenancy type
    expect(homeOwnersData.every((owner: MhrRegistrationHomeOwnerGroupIF) => owner.groupId === 1)).toBeTruthy()
    expect(homeOwners.text()).not.toContain('Group 1')

    // group error message should not be displayed
    expect(homeOwners.find(getTestId('invalid-group-msg')).exists()).toBeFalsy()

    // undo delete to trigger another error message
    await homeOwners.find(getTestId('table-undo-btn')).trigger('click')

    expect(homeOwners.find(getTestId('invalid-group-msg')).text())
      .toContain('All owners must be deceased.')

    await homeOwners.find(getTestId('table-delete-btn')).trigger('click')

    // at the end no error message should be displayed
    expect(homeOwners.find(getTestId('invalid-group-msg')).exists()).toBeFalsy()
  })

  it('TRANS WILL: validations with multiple Owners in multiple groups', async () => {
    // reset transfer type
    await selectTransferType(null)

    const TRANSFER_TYPE = ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL
    const homeOwnerGroup: MhrRegistrationHomeOwnerGroupIF[] = mockMhrTransferCurrentHomeOwnerGroup

    await store.setMhrTransferCurrentHomeOwnerGroups(homeOwnerGroup)
    // reset group ids as this is how it is implemented in the app
    await store.setMhrTransferHomeOwnerGroups([
      { groupId: 1, ...homeOwnerGroup[0] },
      { groupId: 2, ...homeOwnerGroup[1] }
    ])

    await selectTransferType(TRANSFER_TYPE)

    const homeOwners = wrapper
    const allDeleteButtons = homeOwners.findAll(getTestId('table-delete-btn'))
    expect(allDeleteButtons.length).toBe(3)
    allDeleteButtons.at(0).trigger('click')
    await Vue.nextTick()

    expect(homeOwners.find(getTestId('invalid-group-msg')).exists()).toBeTruthy()
    expect(homeOwners.find(getTestId('invalid-group-msg')).text())
      .toContain(transfersErrors.allOwnersHaveDeathCerts[TRANSFER_TYPE])

    await homeOwners.find(getTestId('add-person-btn')).trigger('click')
    await Vue.nextTick()

    // check error message under the Add a Person button
    expect(homeOwners.find(getTestId('transfer-table-error')).exists()).toBeTruthy()
    expect(homeOwners.find(getTestId('transfer-table-error')).text())
      .toContain(transfersErrors.noSupportingDocSelected[TRANSFER_TYPE])

    const supportingDocuments = wrapper.findComponent(SupportingDocuments)

    expect(supportingDocuments.text()).not.toContain(transferSupportingDocuments[TRANSFER_TYPE].optionOne.note)

    // click on Grant of Probate with Will radio button in SupportingDocuments component
    await supportingDocuments.find(getTestId('supporting-doc-option-one')).trigger('click')

    expect(supportingDocuments.text()).toContain(transferSupportingDocuments[TRANSFER_TYPE].optionOne.note)

    // error message under the Add a Person button should not be displayed
    expect(homeOwners.find(getTestId('transfer-table-error')).exists()).toBeFalsy()

    const deletedOwnerGroup: MhrRegistrationHomeOwnerGroupIF = homeOwners.vm.getMhrTransferHomeOwnerGroups[0]

    const addedExecutor: MhrRegistrationHomeOwnerIF = {
      ...mockedAddedPerson,
      ownerId: 11,
      groupId: 1,
      partyType: HomeOwnerPartyTypes.EXECUTOR,
      type: ApiHomeTenancyTypes.SOLE
    }

    const updatedGroup: MhrRegistrationHomeOwnerGroupIF[] = [
      // add executor to the first group
      { groupId: 1, owners: [...deletedOwnerGroup.owners, addedExecutor], type: deletedOwnerGroup.type },
      // second group is not altered
      { groupId: 2, ...homeOwnerGroup[1] }
    ]

    await store.setMhrTransferHomeOwnerGroups(updatedGroup)

    // make sure current owner group is not altered
    expect(homeOwners.vm.getMhrTransferCurrentHomeOwnerGroups[0].owners.length).toBe(2)
    expect(homeOwners.vm.getMhrTransferCurrentHomeOwnerGroups[1].owners.length).toBe(1)

    expect(homeOwners.vm.getMhrTransferHomeOwnerGroups[0].owners.length).toBe(3)
    expect(homeOwners.vm.getMhrTransferHomeOwnerGroups[1].owners.length).toBe(1)

    // since we did not delete the second owner from the group one, the error message should be displayed
    expect(homeOwners.find(getTestId('invalid-group-msg')).text())
      .toContain('All owners must be deceased.')

    // delete the second owner from the first group
    allDeleteButtons.at(1).trigger('click')
    await Vue.nextTick()

    // because two owners are deleted, we can see two SupportingDocuments components
    const allSupportingDocuments = wrapper.findAllComponents(SupportingDocuments)
    expect(allSupportingDocuments.length).toBe(2)

    expect(homeOwners.findAllComponents(DeathCertificate).length).toBe(0)

    // click on both Death Certificates radio buttons to trigger another error message
    allSupportingDocuments.at(0).find(getTestId('supporting-doc-option-two')).trigger('click')
    await Vue.nextTick()
    allSupportingDocuments.at(1).find(getTestId('supporting-doc-option-two')).trigger('click')
    await Vue.nextTick()

    expect(homeOwners.findAllComponents(DeathCertificate).length).toBe(2)

    expect(homeOwners.find(getTestId('invalid-group-msg')).text())
      .toContain('One of the deceased owners must have a Grant of Probate with Will.')

    // click back on Grant of Probate with Will radio button for first owner
    allSupportingDocuments.at(0).find(getTestId('supporting-doc-option-one')).trigger('click')
    await Vue.nextTick()

    expect(homeOwners.findAllComponents(DeathCertificate).length).toBe(1)

    // input data in DeathCertificate component to remove the error message
    const deathCertificateComponent = wrapper.findComponent(DeathCertificate)
    deathCertificateComponent.find(getTestId('death-certificate-number')).setValue('1')
    await Vue.nextTick()
    deathCertificateComponent.findComponent(SharedDatePicker).vm.$emit('emitDate', '2020-10-10')
    await Vue.nextTick()
    deathCertificateComponent.find(getTestId('has-certificate-checkbox')).setChecked()
    await Vue.nextTick()
    await Vue.nextTick()

    // after all owners are deleted, the error message should not be displayed
    expect(homeOwners.find(getTestId('invalid-group-msg')).exists()).toBeFalsy()

    // do few more other checks
    expect(homeOwners.find(getTestId('transfer-table-error')).exists()).toBeFalsy()
    expect(homeOwners.findAll(getTestId('DECEASED-badge')).length).toBe(2)
    expect(homeOwners.findAll(getTestId('ADDED-badge')).length).toBe(1)
  })

  it('TRANS WILL: remove existing Executor and add a new one', async () => {
    // reset transfer type
    await selectTransferType(null)

    const TRANSFER_TYPE = ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL
    const homeOwnerGroup: MhrRegistrationHomeOwnerGroupIF[] = [
      {
        groupId: 1,
        owners: [mockedExecutor],
        type: ''
      }
    ]
    await store.setMhrTransferCurrentHomeOwnerGroups(homeOwnerGroup)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)
    await selectTransferType(TRANSFER_TYPE)

    const homeOwners: Wrapper<any> = wrapper.findComponent(HomeOwners)
    await homeOwners.find(getTestId('table-delete-btn')).trigger('click')

    expect(homeOwners.find(getTestId('invalid-group-msg')).exists()).toBeTruthy()
    expect(homeOwners.find(getTestId('invalid-group-msg')).text())
      .toContain(transfersErrors.mustContainOneExecutor)

    const infoChip: Wrapper<any> = homeOwners.findComponent(InfoChip)
    infoChip.vm.action = 'DELETED'

    await homeOwners.find(getTestId('add-person-btn')).trigger('click')
    const addOwnerSection = homeOwners.findComponent(AddEditHomeOwner)
    expect(addOwnerSection.exists()).toBeTruthy()
    // check that additional name (suffix) is pre-filled
    const suffix = <HTMLInputElement>(addOwnerSection.find(getTestId('suffix'))).element
    expect(suffix.value).toBe(mockedExecutor.description)
    // close Add a Person to add via store (instead of filling out the form)
    await addOwnerSection.find(getTestId('cancel-btn')).trigger('click')

    // add a new Executor via store, preserving first deleted Executor
    await store.setMhrTransferHomeOwnerGroups([
      {
        groupId: 1,
        owners: [
          { ...mockedExecutor, action: ActionTypes.REMOVED },
          { ...mockedAddedExecutor, suffix: mockedExecutor.suffix }
        ],
        type: ''
      }
    ])

    // should have two Executors in the table
    const owners: MhrRegistrationHomeOwnerIF[] = homeOwners.vm.getMhrTransferHomeOwnerGroups[0].owners
    expect(owners.length).toBe(2)
    // both Executors should have the same suffix, because it was pre-filled
    expect(owners[0].suffix).toBe(mockedExecutor.suffix)
    expect(owners[1].suffix).toBe(mockedExecutor.suffix)

    const allBadges = homeOwners.findAllComponents(InfoChip)
    expect(allBadges.length).toBe(2) // Added and Deleted badges
    expect(allBadges.at(0).text()).toContain('DELETED')
    expect(allBadges.at(1).text()).toContain('ADDED')

    expect(homeOwners.find(getTestId('invalid-group-msg')).exists()).toBeFalsy()

    const addedExecutor = homeOwners.find(getTestId('owner-info-' + mockedAddedExecutor.ownerId))
    expect(addedExecutor.exists()).toBeTruthy()
    // check that additional name (suffix) of the deleted Executor is displayed for the new Executor
    expect(addedExecutor.text()).toContain(mockedExecutor.description)
  })

  it('TRANS Affidavit: validations with different error messages', async () => {
    // reset transfer type
    await selectTransferType(null)

    // setup transfer type to test
    const TRANSFER_TYPE = ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL

    const homeOwnerGroup: MhrRegistrationHomeOwnerGroupIF[] = [
      { groupId: 1, owners: [mockedPerson, mockedPerson2], type: '' },
      { groupId: 2, owners: [mockedPerson], type: '' }
    ]

    await selectTransferType(TRANSFER_TYPE)
    await store.setMhrTransferCurrentHomeOwnerGroups(homeOwnerGroup)

    // One Owner is Deceased, no Executor added
    await store.setMhrTransferHomeOwnerGroups([
      { groupId: 1, owners: [mockedPerson, { ...mockedPerson2, action: ActionTypes.REMOVED }], type: '' },
      { groupId: 2, owners: [mockedPerson], type: '' }
    ])
    await nextTick()
    await nextTick()

    const groupError = wrapper.find(getTestId('invalid-group-msg'))
    expect(groupError.text()).toContain(transfersErrors.allOwnersHaveDeathCerts[TRANSFER_TYPE])

    // All Owners are Deceased, no Executor added
    await store.setMhrTransferHomeOwnerGroups([
      {
        groupId: 1,
        owners: [
          { ...mockedPerson, action: ActionTypes.REMOVED },
          { ...mockedPerson2, action: ActionTypes.REMOVED }],
        type: ''
      },
      { groupId: 2, owners: [mockedPerson], type: '' }
    ])

    expect(groupError.text()).toContain(transfersErrors.allOwnersHaveDeathCerts[TRANSFER_TYPE])

    // No Owners removed, one Executor added
    await store.setMhrTransferHomeOwnerGroups([
      { groupId: 1, owners: [mockedPerson, mockedPerson2, mockedAddedExecutor], type: '' },
      { groupId: 2, owners: [mockedPerson], type: '' }
    ])

    expect(groupError.text()).toContain(transfersErrors.ownersMustBeDeceased)
  })

  it('TRANS ADMIN No Will: display Supporting Document component for deleted Owner', async () => {
    // reset transfer type
    await selectTransferType(null)
    const TRANSFER_TYPE = ApiTransferTypes.TO_ADMIN_NO_WILL

    const homeOwnerGroup: MhrRegistrationHomeOwnerGroupIF[] = [{ groupId: 1, owners: [mockedPerson], type: '' }]

    await store.setMhrTransferCurrentHomeOwnerGroups(homeOwnerGroup)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    await selectTransferType(TRANSFER_TYPE)

    const homeOwners = wrapper
    // delete the sole owner
    await homeOwners.find(getTestId('table-delete-btn')).trigger('click')

    const supportingDocuments = wrapper.findComponent(SupportingDocuments)
    expect(supportingDocuments.isVisible()).toBeTruthy()

    expect(supportingDocuments.text()).toContain(transferSupportingDocuments[TRANSFER_TYPE].optionOne.text)
    expect(supportingDocuments.text()).toContain(transferSupportingDocuments[TRANSFER_TYPE].optionTwo.text)

    await supportingDocuments.find(getTestId('supporting-doc-option-one')).trigger('click')
    expect(supportingDocuments.text()).toContain(transferSupportingDocuments[TRANSFER_TYPE].optionOne.note)
  })

  it('TRANS ADMIN No Will: validations with different error messages', async () => {
    // reset transfer type
    await selectTransferType(null)

    // setup transfer type to test
    const TRANSFER_TYPE = ApiTransferTypes.TO_ADMIN_NO_WILL

    const homeOwnerGroup: MhrRegistrationHomeOwnerGroupIF[] = [
      { groupId: 1, owners: [mockedPerson, mockedPerson2], type: '' },
      { groupId: 2, owners: [mockedPerson], type: '' }
    ]

    await selectTransferType(TRANSFER_TYPE)
    await store.setMhrTransferCurrentHomeOwnerGroups(homeOwnerGroup)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    const homeOwners = wrapper
    expect(homeOwners.find(getTestId('invalid-group-msg')).exists()).toBeFalsy()

    // One Owner is Deceased, no Administrator added
    await store.setMhrTransferHomeOwnerGroups([
      { groupId: 1, owners: [mockedPerson, { ...mockedPerson2, action: ActionTypes.REMOVED }], type: '' },
      { groupId: 2, owners: [mockedPerson], type: '' }
    ])

    const groupError = homeOwners.find(getTestId('invalid-group-msg'))

    expect(groupError.text()).toContain(transfersErrors.allOwnersHaveDeathCerts[TRANSFER_TYPE])

    // All Owners are Deceased, no Administrator added
    await store.setMhrTransferHomeOwnerGroups([
      {
        groupId: 1,
        owners: [
          { ...mockedPerson, action: ActionTypes.REMOVED },
          { ...mockedPerson2, action: ActionTypes.REMOVED }],
        type: ''
      },
      { groupId: 2, owners: [mockedPerson], type: '' }
    ])

    expect(groupError.text()).toContain(transfersErrors.allOwnersHaveDeathCerts[TRANSFER_TYPE])

    // No Owners removed, one Administrator added
    await store.setMhrTransferHomeOwnerGroups([
      { groupId: 1, owners: [mockedPerson, mockedPerson2, mockedAddedAdministrator], type: '' },
      { groupId: 2, owners: [mockedPerson], type: '' }
    ])

    expect(groupError.text()).toContain(transfersErrors.ownersMustBeDeceased)
  })

  it('TRANS ADMIN No Will: remove existing Administrator and add a new one', async () => {
    // reset transfer type
    await selectTransferType(null)

    const TRANSFER_TYPE = ApiTransferTypes.TO_ADMIN_NO_WILL
    const homeOwnerGroup: MhrRegistrationHomeOwnerGroupIF[] = [
      {
        groupId: 1,
        owners: [mockedAdministrator],
        type: ''
      }
    ]
    await store.setMhrTransferCurrentHomeOwnerGroups(homeOwnerGroup)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)
    await selectTransferType(TRANSFER_TYPE)

    const homeOwners = wrapper.findComponent(HomeOwners)
    await homeOwners.find(getTestId('table-delete-btn')).trigger('click')
    await Vue.nextTick()

    expect(homeOwners.find(getTestId('invalid-group-msg')).exists()).toBeTruthy()
    expect(homeOwners.find(getTestId('invalid-group-msg')).text())
      .toContain(transfersErrors.mustContainOneAdmin)

    await homeOwners.find(getTestId('add-person-btn')).trigger('click')
    const addEditHomeOwner = homeOwners.findComponent(AddEditHomeOwner)
    expect(addEditHomeOwner.exists()).toBeTruthy()
    // check that suffix field value is pre-populated with the name of deleted person
    const suffix = <HTMLInputElement>(addEditHomeOwner.find(getTestId('suffix'))).element
    expect(suffix.value).toBe(mockedAdministrator.description)

    // expect(addEditHomeOwner.text()).toContain(mockedAdministrator.suffix)
    // close Add a Person to add via store (instead of filling out the form)
    await addEditHomeOwner.find(getTestId('cancel-btn')).trigger('click')

    // add a new Executor via store, preserving first deleted Executor
    await store.setMhrTransferHomeOwnerGroups([
      {
        groupId: 1,
        owners: [
          { ...mockedAdministrator, action: ActionTypes.REMOVED },
          { ...mockedAddedAdministrator, suffix: mockedAdministrator.suffix }
        ],
        type: ''
      }
    ])

    const allBadges = homeOwners.findAllComponents(InfoChip)
    expect(allBadges.length).toBe(2) // Added and Deleted badges
    expect(allBadges.at(0).text()).toContain('DELETED')
    expect(allBadges.at(1).text()).toContain('ADDED')
    expect(homeOwners.find(getTestId('invalid-group-msg')).exists()).toBeFalsy()

    const addedAdministrator = homeOwners.find(getTestId('owner-info-' + mockedAdministrator.ownerId))
    expect(addedAdministrator.exists()).toBeTruthy()
    // check that additional name (suffix) of the deleted Administrator is displayed for the new Administrator
    expect(addedAdministrator.text()).toContain(mockedAdministrator.description)
  })
})
