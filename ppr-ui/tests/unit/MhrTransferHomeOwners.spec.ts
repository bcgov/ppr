import { nextTick } from 'vue'
import { useStore } from '../../src/store/store'

import { HomeOwners } from '@/views'
import {
  AddEditHomeOwner,
  HomeOwnersTable,
  HomeOwnerGroups,
  TableGroupHeader,
  HomeOwnerRoles,
  PreviousHomeOwners
} from '@/components/mhrRegistration/HomeOwners'
import { InfoChip, InputFieldDatePicker, SimpleHelpToggle } from '@/components/common'
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
  mockedAdministrator,
  mockedRemovedAdministrator,
  mockedConfidentialUnitNote,
  mockedUnitNotes5,
  mockedUnitNotes3
} from './test-data'
import { createComponent, getTestId } from './utils'
import {
  MhrRegistrationHomeOwnerGroupIF,
  MhrRegistrationHomeOwnerIF,
  TransferTypeSelectIF
} from '@/interfaces'
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
import { useNewMhrRegistration } from '@/composables'

const store = useStore()

describe('Home Owners', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(HomeOwners, { appReady: true, isMhrTransfer: true })

    await store.setMhrTransferType({
      divider: false,
      disabled: false,
      selectDisabled: false,
      transferType: ApiTransferTypes.SALE_OR_GIFT,
      textLabel: UITransferTypes.SALE_OR_GIFT,
      group: 1
    } as TransferTypeSelectIF)
  })
  afterEach(() => {
    store.setEmptyMhr(useNewMhrRegistration().initNewMhr())
  })

  // Helper functions

  const openAddPerson = async () => {
    const homeOwnersSection = wrapper
    await homeOwnersSection.find(getTestId('add-person-btn')).trigger('click')
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
    expect(wrapper.findComponent(PreviousHomeOwners).exists()).toBeFalsy()
  })

  it('renders Add Edit Home Owner and its sub components', async () => {
    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBe(false) // Hidden by default
    await openAddPerson()
    await nextTick()
    await nextTick()
    await clickCancelAddOwner()
    await nextTick()
    await nextTick()
    await openAddOrganization()
    await nextTick()
    await nextTick()
    await clickCancelAddOwner()
  })

  it('displays CURRENT owners (Persons and Orgs)', async () => {
    const homeOwnerGroup = [{ groupId: 1, owners: [mockedPerson] }] as MhrRegistrationHomeOwnerGroupIF[]

    // add a person
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)
    wrapper = await createComponent(HomeOwners, { appReady: true, isMhrTransfer: true })

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
    const updatedHomeOwnerGroup = [...homeOwnerGroup]
    updatedHomeOwnerGroup[0].owners.push(mockedOrganization)
    await store.setMhrTransferHomeOwnerGroups(updatedHomeOwnerGroup)
    await nextTick()

    expect(store.getMhrTransferHomeOwnerGroups.at(0).owners.length).toBe(2)

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()

    ownersTable = await wrapper.findComponent(HomeOwnersTable)

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
    const homeOwnerGroup = [{ groupId: 1, owners: [mockedAddedPerson, mockedAddedOrganization], type: '' }]

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
    const homeOwnerGroup = [{ groupId: 1, owners: [mockedRemovedPerson, mockedRemovedOrganization], type: '' }]

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
    const homeOwnerGroups: MhrRegistrationHomeOwnerGroupIF[] = [
      {
        groupId: 1,
        interest: 'Undivided',
        interestNumerator: 2,
        interestDenominator: 4,
        owners: [mockedPerson],
        type: ''
      },
      {
        groupId: 2,
        interest: 'Undivided',
        action: ActionTypes.REMOVED,
        interestNumerator: 2,
        interestDenominator: 4,
        owners: [mockedOrganization],
        type: ''
      }
    ]

    // add a person
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroups)

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()
    // check current Owners and Groups
    wrapper.vm.setShowGroups(true)
    await nextTick()

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
    expect(ownersTable.text()).not.toContain('Group 2')
    expect(ownersTable.text()).toContain('Previous Owner Group')

    // there should be 'DELETED' badges shown for the Deleted Group
    expect(ownersTable.findAllComponents(TableGroupHeader).at(1)
      .findComponent(InfoChip).text()).toContain(ActionTypes.REMOVED)

    wrapper.vm.setShowGroups(false)
  })

  it('should display a CHANGED a home owner group', async () => {
    const homeOwnerGroups: MhrRegistrationHomeOwnerGroupIF[] = [
      {
        groupId: 1,
        interest: 'Undivided',
        interestNumerator: 2,
        interestDenominator: 4,
        owners: [mockedPerson],
        type: ''
      },
      {
        groupId: 2,
        interest: 'Undivided',
        action: ActionTypes.CHANGED,
        interestNumerator: 3,
        interestDenominator: 4,
        owners: [mockedOrganization],
        type: ''
      }
    ]

    // add a person
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroups)

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()
    // check current Owners and Groups
    wrapper.vm.setShowGroups(true)
    await nextTick()

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

    const homeOwners = wrapper
    expect(homeOwners.find(getTestId('table-delete-btn')).exists()).toBeTruthy()
    await homeOwners.find(getTestId('table-delete-btn')).trigger('click')
    await nextTick()

    const allDeletedBadges = homeOwners.findAll(getTestId('DELETED-badge'))
    expect(allDeletedBadges.length).toBe(1)

    expect(homeOwners.find(getTestId('invalid-group-msg')).exists()).toBeFalsy()
    expect(homeOwners.find(getTestId('no-data-msg')).exists()).toBeFalsy()

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

  it('TRANS SALE GIFT: only one role (Owner) should be active when adding/editing an owner', async () => {
    const homeOwnerGroup: MhrRegistrationHomeOwnerGroupIF[] = [{ groupId: 1, owners: [mockedPerson], type: '' }]

    await store.setMhrTransferCurrentHomeOwnerGroups(homeOwnerGroup)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()
    openAddPerson()
    await nextTick()
    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeTruthy()

    const HomeOwnerRolesComponent = wrapper.findComponent(AddEditHomeOwner).findComponent(HomeOwnerRoles)
    const radioButtons = HomeOwnerRolesComponent.findAll('input[type="radio"]')
    expect(radioButtons).toHaveLength(4)

    // role 'Owner' should be enabled while others disabled
    expect(radioButtons.at(0).attributes('disabled')).toBe(undefined)
    expect(radioButtons.at(1).attributes('disabled')).toBeDefined()
    expect(radioButtons.at(2).attributes('disabled')).toBeDefined()
    expect(radioButtons.at(3).attributes('disabled')).toBeDefined()
  })

  it('TRANS SALE GIFT: should show error when some Exec, Admin or Trustees are not deleted', async () => {
    const homeOwnerGroup: MhrRegistrationHomeOwnerGroupIF[] = [
      { groupId: 1, owners: [mockedExecutor, mockedAdministrator], type: '' }
    ]

    await store.setMhrTransferCurrentHomeOwnerGroups(homeOwnerGroup)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    const homeOwnersTable = wrapper.findComponent(HomeOwnersTable)

    // should not be any errors
    expect(homeOwnersTable.find(getTestId('invalid-group-msg')).exists()).toBeFalsy()
    // should show all Delete buttons in the table
    const allDeleteButtons = homeOwnersTable.findAll(getTestId('table-delete-btn'))
    expect(allDeleteButtons).toHaveLength(homeOwnerGroup[0].owners.length) // should be two Delete buttons

    // delete first owner which is Executor
    allDeleteButtons.at(0).trigger('click')
    await nextTick()

    expect(homeOwnersTable.find(getTestId('invalid-group-msg')).exists()).toBeTruthy()
    expect(homeOwnersTable.find(getTestId('invalid-group-msg')).text())
      .toContain(transfersErrors.eatOwnersMustBeDeleted)

    expect(homeOwnersTable.findAll('.border-error-left')).toHaveLength(0)
    wrapper = await createComponent(HomeOwners, { appReady: true, isMhrTransfer: true, validateTransfer: true } )
    // should be three border errors, for: error message itself, owner 1 and owner 2
    expect(wrapper.findAll('.border-error-left')).toHaveLength(3)
  })

  it('TRANS SALE GIFT + Unit Note: renders Home Owners table buttons when Confidential Note filed', async () => {
    const homeOwnerGroup: MhrRegistrationHomeOwnerGroupIF[] = [
      { groupId: 1, owners: [mockedPerson, mockedPerson2], type: '' }
    ]

    await store.setMhrTransferCurrentHomeOwnerGroups(homeOwnerGroup)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)
    await store.setMhrUnitNotes([mockedConfidentialUnitNote, ...mockedUnitNotes3, ...mockedUnitNotes5])

    await selectTransferType(ApiTransferTypes.SALE_OR_GIFT)

    const ownersTable = wrapper.findComponent(HomeOwnersTable)

    const deleteOwnerButtons = ownersTable.findAll(getTestId('table-delete-btn'))
    expect(deleteOwnerButtons).toHaveLength(2)

    await deleteOwnerButtons.at(0).trigger('click')
    await deleteOwnerButtons.at(1).trigger('click')
    await nextTick()

    const removedBadges = ownersTable.findAll(getTestId('DELETED-badge'))
    expect(removedBadges).toHaveLength(2)

    await selectTransferType(null)

    expect(ownersTable.findAll(getTestId('table-delete-btn'))).toHaveLength(0)
  })

  it('TRANS SALE: should not show errors for owners types (Individual & Business) in the table', async () => {
    const homeOwnerGroup: MhrRegistrationHomeOwnerGroupIF[] = [
      { groupId: 1, owners: [mockedPerson, mockedPerson2, mockedOrganization], type: '' }
    ]

    await store.setMhrTransferCurrentHomeOwnerGroups(homeOwnerGroup)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)
    await selectTransferType(ApiTransferTypes.SALE_OR_GIFT)

    let homeOwners = wrapper

    // make sure there are no errors
    expect(homeOwners.find(getTestId('invalid-group-msg')).exists()).toBeFalsy()
    expect(homeOwners.find(getTestId('no-data-msg')).exists()).toBeFalsy()
    expect(homeOwners.find(getTestId('structure-change-required')).exists()).toBeFalsy()
    expect(homeOwners.find('border-error-left').exists()).toBeFalsy()

    // make sure validation is not triggered yet
    expect(homeOwners.vm.validateTransfer).toBe(false)
    homeOwners = await createComponent(HomeOwners, { appReady: true, isMhrTransfer: true, validateTransfer: true } )
    // await nextTick()

    // make sure page validation is triggered
    expect(homeOwners.vm.validateTransfer).toBe(true)

    // table errors are showing
    expect(homeOwners.find(getTestId('structure-change-required')).exists()).toBeTruthy()
    expect(homeOwners.find('#home-owner-table-card.border-error-left').exists()).toBeTruthy()

    // home owner row errors are not showing
    expect(homeOwners.find(getTestId('invalid-group-msg')).exists()).toBeFalsy()
    expect(homeOwners.find('.owner-name.border-error-left').exists()).toBeFalsy()
  })

  it('TRANS SALE: validations for mixed owners roles (Exec, Admin, Trustee) in the table', async () => {
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
          } as MhrRegistrationHomeOwnerIF
        ],
        type: ''
      }
    ]
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    const homeOwners = wrapper
    const groupError = homeOwners.find(getTestId('invalid-group-msg'))

    expect(groupError.text()).toContain(MixedRolesErrors.hasMixedOwnerTypes)

    // add one more owner to the second group to trigger a new error message
    const updatedHomeOwnerGroup = [...homeOwnerGroup] // make copy to help with reactivity
    updatedHomeOwnerGroup.push({
      groupId: 2,
      owners: [mockedPerson],
      type: ''
    } as MhrRegistrationHomeOwnerGroupIF)

    await store.setMhrTransferHomeOwnerGroups(updatedHomeOwnerGroup)

    expect(groupError.text()).toContain(MixedRolesErrors.hasMixedOwnerTypesInGroup)

    // change transfer type and check for removed basic owners
    await selectTransferType(ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL)
    const updatedHomeOwnerGroup2 = [...updatedHomeOwnerGroup]
    updatedHomeOwnerGroup2.pop()
    await store.setMhrTransferHomeOwnerGroups(updatedHomeOwnerGroup2)

    expect(wrapper.vm.getHomeOwners.length).toBe(2)
    expect(homeOwners.find(getTestId('invalid-group-msg')).text()).toContain(transfersErrors.ownersMustBeDeceased)

    // change transfer type and check for removed basic owners again
    await selectTransferType(ApiTransferTypes.TO_EXECUTOR_UNDER_25K_WILL)
    await store.setMhrTransferHomeOwnerGroups([...updatedHomeOwnerGroup2])

    expect(homeOwners.find(getTestId('invalid-group-msg')).text()).toContain(transfersErrors.ownersMustBeDeceased)
  })

  it('TRANS SALE: validations for under allocated group ownership interest', async () => {
    // under allocated groups
    const homeOwnerGroups: MhrRegistrationHomeOwnerGroupIF[] = [
      {
        groupId: 1,
        interest: 'Undivided',
        interestNumerator: 1,
        interestDenominator: 4,
        owners: [mockedPerson],
        type: ''
      },
      {
        groupId: 2,
        interest: 'Undivided',
        interestNumerator: 2,
        interestDenominator: 4,
        owners: [mockedPerson2],
        type: ''
      }
    ]

    await store.setMhrTransferCurrentHomeOwnerGroups(homeOwnerGroups)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroups)

    await selectTransferType(ApiTransferTypes.SALE_OR_GIFT)
    wrapper.vm.setShowGroups(true)
    await nextTick()

    let homeOwners = wrapper

    // check ownership allocation info has error and error is showing
    const ownershipAllocation = homeOwners.find(getTestId('ownership-allocation'))
    expect(ownershipAllocation.exists()).toBeTruthy()
    expect(ownershipAllocation.text()).toContain('3/4')
    expect(ownershipAllocation.text()).toContain('Total ownership interest is under allocated')
    // table error should not show because page validation is not triggered (Review and Confirm button was not clicked)
    expect(homeOwners.find('#home-owner-table-card.border-error-left').exists()).toBe(false)

    // trigger page validation
    homeOwners = await createComponent(HomeOwners, { appReady: true, isMhrTransfer: true, validateTransfer: true } )
    expect(homeOwners.find('#home-owner-table-card.border-error-left').exists()).toBe(true)

    // update group to be fully allocated
    const updatedHomeOwnerGroup = [...homeOwnerGroups]
    updatedHomeOwnerGroup[0].interestNumerator = 2

    await store.setMhrTransferCurrentHomeOwnerGroups(updatedHomeOwnerGroup)
    await store.setMhrTransferHomeOwnerGroups(updatedHomeOwnerGroup)
    await store.setUnsavedChanges(true)

    // check ownership allocation info is fully allocated and error not showing
    expect(homeOwners.find(getTestId('ownership-allocation')).text()).toContain('Fully Allocated')
    expect(homeOwners.find('#home-owner-table-card.border-error-left').exists()).toBe(false)
  })

  it('TRANS SALE: validations when group has all owners deleted', async () => {
    const homeOwnerGroup: MhrRegistrationHomeOwnerGroupIF[] = [
      {
        groupId: 1,
        interest: 'Undivided',
        interestNumerator: 4,
        interestDenominator: 4,
        owners: [mockedRemovedPerson, mockedRemovedOrganization],
        type: ''
      }
    ]

    await store.setMhrTransferCurrentHomeOwnerGroups(homeOwnerGroup)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)
    const homeOwners = await createComponent(HomeOwners, { isMhrTransfer: true, validateTransfer: true })
    homeOwners.vm.setShowGroups(true)
    await nextTick()

    // check ownership allocation info has no errors
    expect(homeOwners.find(getTestId('ownership-allocation')).text()).toContain('Fully Allocated')

    // does not have table error
    expect(homeOwners.find('#home-owner-table-card.border-error-left').exists()).toBe(false)

    expect(homeOwners.find(getTestId('invalid-group-msg')).text())
      .toBe('Group must contain at least one owner.')

    expect(homeOwners.findAll(getTestId('DELETED-badge'))).toHaveLength(2)

    // has border errors for the group (rows: header, error, owner one, owner two)
    expect(homeOwners.find('.group-header-slot.border-error-left').exists()).toBeTruthy()
    expect(homeOwners.find(getTestId('invalid-group-msg')).classes('border-error-left')).toBeTruthy()
    expect(homeOwners.find(getTestId('owner-info-10')).find('.owner-name').classes('border-error-left')).toBeTruthy()
    expect(homeOwners.find(getTestId('owner-info-20')).find('.owner-name').classes('border-error-left')).toBeTruthy()
  })

  it('TRANS SALE GIFT: should not show group error for Added and Deleted groups', async () => {
    const homeOwnerGroups: MhrRegistrationHomeOwnerGroupIF[] = [
      {
        groupId: 1,
        interest: 'Undivided',
        owners: [mockedPerson],
        type: '',
        action: ActionTypes.REMOVED
      },
      {
        groupId: 2,
        interest: 'Undivided',
        interestNumerator: 1,
        interestDenominator: 2,
        owners: [mockedPerson2, mockedOrganization],
        type: ''
      },
      {
        groupId: 3,
        interest: 'Undivided',
        interestNumerator: 1,
        interestDenominator: 2,
        owners: [mockedAddedPerson],
        type: '',
        action: ActionTypes.ADDED
      }
    ]

    await store.setMhrTransferCurrentHomeOwnerGroups(homeOwnerGroups)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroups)
    await nextTick()

    await selectTransferType(ApiTransferTypes.SALE_OR_GIFT)
    const wrapper = await createComponent(HomeOwners, { isMhrTransfer: true, validateTransfer: true })
    wrapper.vm.setShowGroups(true)
    await nextTick()

    expect(wrapper.find(getTestId('ownership-allocation')).text()).toContain('Fully Allocated')
    expect(wrapper.findAllComponents(TableGroupHeader)).toHaveLength(3)
    expect(wrapper.findAll('.border-error-left')).toHaveLength(0)
    expect(wrapper.findAll(getTestId('ADDED-badge'))).toHaveLength(2) // group 3 and owner badges
    expect(wrapper.findAll(getTestId('DELETED-badge'))).toHaveLength(1) // group 1 badge
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
      supportingDocuments.findInputByTestId('supporting-doc-option-one').element
    )
    // check that Grant of Probate radio button option is selected by default
    expect(radioButtonGrantOfProbate.checked).toBe(true)

    const radioButtonDeathCert = <HTMLInputElement>(
      supportingDocuments.findInputByTestId('supporting-doc-option-two')).element

    // check disabled state of Death Certificate radio button
    expect(radioButtonDeathCert.disabled).toBeDefined()

    await wrapper.find(getTestId('add-person-btn'))?.trigger('click')
    await nextTick()

    const addEditHomeOwner = wrapper.findComponent(AddEditHomeOwner)
    expect(addEditHomeOwner.find('#executor-option').exists()).toBeTruthy()

    // check that Executor radio button option is selected by default
    const executorRadioButton = <HTMLInputElement>(addEditHomeOwner.find('#executor-option')).element
    expect(executorRadioButton.checked).toBeTruthy()

    // check that suffix field value is pre-populated with the name of deleted person
    const suffix = addEditHomeOwner.find(getTestId('suffix')).find('input').element as HTMLInputElement
    const { first, middle, last } = mockedPerson.individualName
    expect(suffix.value).toBe(`Executor of the will of ${first} ${middle} ${last}, deceased`)
  })

  it('TRANS WILL: displays correct tenancy type in Executor scenarios', async () => {
    // setup transfer type to test
    const TRANSFER_TYPE = ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL

    let homeOwnerGroup = [{ groupId: 1, owners: [mockedPerson], type: '' }]
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    const ownersTable = wrapper.findComponent(HomeOwnersTable)

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
    const updatedHomeOwnerGroup = [...homeOwnerGroup]
    updatedHomeOwnerGroup[0].owners.push(mockedExecutor)
    await store.setMhrTransferHomeOwnerGroups(updatedHomeOwnerGroup)

    // Tenancy type should be N/A due to mix of Executor and living owner
    expect(wrapper.vm.getHomeOwners.length).toBe(2)
    expect(
      wrapper
        .findComponent(HomeOwners)
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.NA)

    // reset owners
    const updatedHomeOwnerGroup2 = [{ groupId: 1, owners: [mockedPerson], type: '' }]
    await store.setMhrTransferHomeOwnerGroups(updatedHomeOwnerGroup2)

    // delete original owner
    await ownersTable.find(getTestId('table-delete-btn')).trigger('click')

    // Tenancy type should be N/A with no living owners
    expect(wrapper.vm.getHomeOwners.length).toBe(1)
    expect(
      wrapper
        .findComponent(HomeOwners)
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.NA)

    // add executor
    const updatedHomeOwnerGroup3 = [...updatedHomeOwnerGroup2]
    updatedHomeOwnerGroup3[0].owners.push(mockedExecutor)
    await store.setMhrTransferHomeOwnerGroups(updatedHomeOwnerGroup3)

    // Tenancy type should be SOLE
    expect(wrapper.vm.getHomeOwners.length).toBe(2)
    expect(
      wrapper
        .findComponent(HomeOwners)
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.SOLE)

    // add another executor
    const updatedHomeOwnerGroup4 = [...updatedHomeOwnerGroup3]
    updatedHomeOwnerGroup4[0].owners.push(mockedExecutor)
    await store.setMhrTransferHomeOwnerGroups(updatedHomeOwnerGroup4)

    // Tenancy type should be N/A due to multiple Executors
    expect(wrapper.vm.getHomeOwners.length).toBe(3)
    expect(
      wrapper
        .findComponent(HomeOwners)
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.NA)
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
    expect(homeOwners.find(getTestId('invalid-group-msg')).text()).toContain(transfersErrors.mustContainOneExecutor)

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
      .toContain(transfersErrors.ownersMustBeDeceased)

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

    wrapper.vm.setShowGroups(true)
    const homeOwners = wrapper
    const allDeleteButtons = homeOwners.findAll(getTestId('table-delete-btn'))
    expect(allDeleteButtons.length).toBe(3)
    allDeleteButtons.at(0).trigger('click')
    await nextTick()

    expect(homeOwners.find(getTestId('invalid-group-msg')).exists()).toBeTruthy()
    expect(homeOwners.find(getTestId('invalid-group-msg')).text())
      .toContain(transfersErrors.allOwnersHaveDeathCerts[TRANSFER_TYPE])

    await homeOwners.find(getTestId('add-person-btn')).trigger('click')
    await nextTick()

    // check error message under the Add a Person button
    expect(homeOwners.find(getTestId('transfer-table-error')).exists()).toBeTruthy()
    expect(homeOwners.find(getTestId('transfer-table-error')).text())
      .toContain(transfersErrors.noSupportingDocSelected[TRANSFER_TYPE])

    const supportingDocuments = wrapper.findComponent(SupportingDocuments)

    expect(supportingDocuments.text()).not.toContain(transferSupportingDocuments[TRANSFER_TYPE].optionOne.note)

    // click on Grant of Probate with Will radio button in SupportingDocuments component
    supportingDocuments.findInputByTestId('supporting-doc-option-one').setValue(true)
    await nextTick()

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
      .toContain(transfersErrors.ownersMustBeDeceased)

    // delete the second owner from the first group
    allDeleteButtons.at(1).trigger('click')
    await nextTick()

    // because two owners are deleted, we can see two SupportingDocuments components
    const allSupportingDocuments = wrapper.findAllComponents(SupportingDocuments)
    expect(allSupportingDocuments.length).toBe(2)

    expect(homeOwners.findAllComponents(DeathCertificate).length).toBe(0)

    // click on both Death Certificates radio buttons to trigger another error message
    allSupportingDocuments.at(0).findInputByTestId('supporting-doc-option-two').setValue(true)
    await nextTick()
    allSupportingDocuments.at(1).findInputByTestId('supporting-doc-option-two').setValue(true)
    await nextTick()

    expect(homeOwners.findAllComponents(DeathCertificate).length).toBe(2)

    expect(homeOwners.find(getTestId('invalid-group-msg')).text())
      .toContain(transfersErrors.allOwnersHaveDeathCerts[TRANSFER_TYPE])

    // click back on Grant of Probate with Will radio button for first owner
    allSupportingDocuments.at(0).findInputByTestId('supporting-doc-option-one').setValue(true)
    await nextTick()

    expect(homeOwners.findAllComponents(DeathCertificate).length).toBe(1)

    // input data in DeathCertificate component to remove the error message
    const deathCertificateComponent = wrapper.findComponent(DeathCertificate)
    deathCertificateComponent.findInputByTestId('death-certificate-number').setValue('1')
    await nextTick()
    deathCertificateComponent.findComponent(InputFieldDatePicker).vm.$emit('emitDate', '2020-10-10')
    await nextTick()
    deathCertificateComponent.find(getTestId('has-certificate-checkbox')).setChecked()
    await nextTick()
    await nextTick()

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

    const homeOwnerGroupTwoExecutors: MhrRegistrationHomeOwnerGroupIF[] = [
      {
        groupId: 1,
        owners: [mockedExecutor, mockedExecutor],
        type: ''
      }
    ]

    await store.setMhrTransferCurrentHomeOwnerGroups(homeOwnerGroupTwoExecutors)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroupTwoExecutors)
    await selectTransferType(ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL)

    const homeOwners = wrapper.findComponent(HomeOwners)
    expect(homeOwners.findComponent(PreviousHomeOwners).exists()).toBeFalsy()
    await homeOwners.find(getTestId('table-delete-btn')).trigger('click')
    // error should not be shown when removing one out of two Executors in the group
    expect(homeOwners.find(getTestId('invalid-group-msg')).exists()).toBeFalsy()

    const homeOwnerGroup: MhrRegistrationHomeOwnerGroupIF[] = [
      {
        groupId: 1,
        owners: [mockedExecutor],
        type: ''
      }
    ]
    await store.setMhrTransferCurrentHomeOwnerGroups(homeOwnerGroup)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)
    wrapper.vm.setShowGroups(false)
    await homeOwners.find(getTestId('table-delete-btn')).trigger('click')

    expect(homeOwners.find(getTestId('invalid-group-msg')).exists()).toBeTruthy()
    expect(homeOwners.find(getTestId('invalid-group-msg')).text())
      .toContain(transfersErrors.mustContainOneExecutor)

    await homeOwners.find(getTestId('add-person-btn')).trigger('click')
    const addOwnerSection = homeOwners.findComponent(AddEditHomeOwner)
    expect(addOwnerSection.exists()).toBeTruthy()
    // check that additional name (suffix) is pre-filled
    const suffix = addOwnerSection.find(getTestId('suffix')).find('input').element as HTMLInputElement
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

    const homeOwnerGroupTwoAdministrators: MhrRegistrationHomeOwnerGroupIF[] = [
      {
        groupId: 1,
        owners: [mockedAdministrator, mockedAdministrator],
        type: ''
      }
    ]

    await store.setMhrTransferCurrentHomeOwnerGroups(homeOwnerGroupTwoAdministrators)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroupTwoAdministrators)
    await selectTransferType(TRANSFER_TYPE)

    const homeOwners = wrapper.findComponent(HomeOwners)
    await homeOwners.find(getTestId('table-delete-btn')).trigger('click')
    // error should not be shown when removing one out of two Administrator in the group
    expect(homeOwners.find(getTestId('invalid-group-msg')).exists()).toBeFalsy()

    const homeOwnerGroup: MhrRegistrationHomeOwnerGroupIF[] = [{ groupId: 1, owners: [mockedPerson], type: '' }]

    await store.setMhrTransferCurrentHomeOwnerGroups(homeOwnerGroup)
    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroup)

    await selectTransferType(TRANSFER_TYPE)

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

    expect(groupError.text()).toContain(MixedRolesErrors.hasMixedOwnerTypesInGroup)
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
    wrapper.vm.setShowGroups(false)

    const homeOwners = wrapper.findComponent(HomeOwners)
    await homeOwners.find(getTestId('table-delete-btn')).trigger('click')
    await nextTick()

    expect(homeOwners.find(getTestId('invalid-group-msg')).exists()).toBeTruthy()
    expect(homeOwners.find(getTestId('invalid-group-msg')).text())
      .toContain(transfersErrors.mustContainOneAdmin)

    await homeOwners.find(getTestId('add-person-btn')).trigger('click')
    const addEditHomeOwner = homeOwners.findComponent(AddEditHomeOwner)
    expect(addEditHomeOwner.exists()).toBeTruthy()
    // check that suffix/description field value is pre-populated with the name of deleted person
    const suffix = addEditHomeOwner.find(getTestId('suffix')).find('input').element as HTMLInputElement
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

  it('TRANS TO EXEC and ADMIN: validate removing Execs and adding Admins', async () => {
    // reset transfer type
    await selectTransferType(null)

    await selectTransferType(ApiTransferTypes.TO_EXECUTOR_PROBATE_WILL)

    await store.setMhrTransferHomeOwnerGroups([
      {
        groupId: 1,
        owners: [mockedExecutor, mockedExecutor, mockedAddedExecutor],
        type: ''
      }
    ])
    let homeOwners = wrapper.findComponent(HomeOwners)
    expect(homeOwners.findAll('.owner-info').length).toBe(3)
    // For Will Transfers, adding new Executor should show not show any errors
    expect(homeOwners.find(getTestId('invalid-group-msg')).exists()).toBeFalsy()
    expect(homeOwners.findAll('.border-error-left').length).toBe(0)

    await store.setMhrTransferHomeOwnerGroups([
      {
        groupId: 1,
        owners: [mockedRemovedAdministrator, mockedRemovedAdministrator],
        type: ''
      }
    ])

    homeOwners = wrapper.findComponent(HomeOwners)
    expect(homeOwners.findAll('.owner-info').length).toBe(2)
    // For Will Transfers, removing all owners should show error that Executors must be added
    expect(homeOwners.find(getTestId('invalid-group-msg')).text()).toBe(transfersErrors.mustContainOneExecutor)
    expect(homeOwners.findAll('.border-error-left').length).toBe(0)

    // For Admin Transfers, removing all owners show error that Admins must be added
    await selectTransferType(ApiTransferTypes.TO_ADMIN_NO_WILL)
    expect(homeOwners.find(getTestId('invalid-group-msg')).text()).toBe(transfersErrors.mustContainOneAdmin)
  })
})
