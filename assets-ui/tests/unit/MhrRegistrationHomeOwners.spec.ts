import { nextTick } from 'vue'

import { HomeOwners, MhrRegistration } from '@/views'
import {
  AddEditHomeOwner,
  HomeOwnersTable,
  HomeOwnerGroups,
  TableGroupHeader,
  FractionalOwnership,
  HomeOwnerRoles
} from '@/components/mhrRegistration/HomeOwners'
import { SimpleHelpToggle } from '@/components/common'
import { mockedPerson, mockedOrganization, mockedExecutor, mockedOwner, mockedMhrRegistration } from './test-data'
import { createComponent, getTestId } from './utils'
import { MhrRegistrationHomeOwnerGroupIF, MhrRegistrationHomeOwnerIF } from '@/interfaces'
import { HomeTenancyTypes, RouteNames } from '@/enums'
import { MhrCorrectionStaff, MixedRolesErrors } from '@/resources'
import { useStore } from '../../src/store/store'
import { useNewMhrRegistration } from '@/composables/mhrRegistration'
import { defaultFlagSet } from '@/utils'
import { expect, it } from 'vitest'
import { axe } from 'vitest-axe'

const store = useStore()

describe('Home Owners', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(HomeOwners, { appReady: true })
    await nextTick()
  })
  afterEach(async () => {
    // reset store
    await store.setEmptyMhr(useNewMhrRegistration().initNewMhr())
  })

  // Helper functions

  const openAddPerson = async () => {
    await wrapper.find(getTestId('add-person-btn')).trigger('click')
    await nextTick()
    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeTruthy()
    expect(wrapper.findComponent(HomeOwnerGroups).exists()).toBeTruthy()
  }

  const openAddOrganization = async () => {
    await wrapper.find(getTestId('add-org-btn')).trigger('click')
    await nextTick()
    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeTruthy()
    expect(wrapper.findComponent(HomeOwnerGroups).exists()).toBeTruthy()
  }

  const clickCancelAddOwner = async () => {
    const addOwnerSection = wrapper.findComponent(AddEditHomeOwner)
    expect(addOwnerSection.exists).toBeTruthy()
    const cancelBtn = addOwnerSection.find(getTestId('cancel-btn'))
    expect(cancelBtn.exists()).toBeTruthy()
    await cancelBtn.trigger('click')
    await nextTick()
    expect(addOwnerSection.exists()).toBeFalsy()
  }

  const clickDoneAddOwner = async () => {
    const addOwnerSection = wrapper.findComponent(AddEditHomeOwner)
    const doneBtn = addOwnerSection.find(getTestId('done-btn'))
    expect(doneBtn.exists()).toBeTruthy()
    await addOwnerSection.vm.addHomeOwnerForm.validate()
    await doneBtn.trigger('click')

    setTimeout(async () => {
      expect(addOwnerSection.exists()).toBeFalsy() // Hidden by default
    }, 500)
  }

  // Tests

  it('should have no accessibility violations', async () => {
    // Run the axe-core accessibility check on the component's HTML
    const results = await axe(wrapper.html())
    // Use the custom vitest-axe matcher to check for violations
    expect(results).toHaveNoViolations()
  })

  it('renders Home Owners and its sub components', () => {
    expect(wrapper.exists()).toBeTruthy()
    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy() // Hidden by default
    expect(wrapper.findComponent(HomeOwnersTable).exists()).toBeTruthy()
    expect(wrapper.findComponent(SimpleHelpToggle).exists()).toBeTruthy()
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

  it('renders home owner (person and org) via store dispatch', async () => {
    const owners = [mockedPerson] as MhrRegistrationHomeOwnerIF[]
    const homeOwnerGroup = [{ groupId: 1, owners: owners }] as MhrRegistrationHomeOwnerGroupIF[]

    // add a person
    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroup)

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()

    let ownersTable = await wrapper.findComponent(HomeOwnersTable)

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

    // there should be no 'Added' badge shown, as the badge is only for MHR Transfers
    const addedBadge = ownersTable.find(getTestId('owner-added-badge'))
    expect(addedBadge.exists()).toBeFalsy()

    // add an organization
    homeOwnerGroup[0].owners.push(mockedOrganization)
    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroup)

    wrapper = await createComponent(HomeOwners)
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

  it('should edit home owner', async () => {
    const homeOwnerGroup = [
      { groupId: 1, owners: [mockedPerson, mockedOrganization] }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroup)

    let ownersTable = wrapper.findComponent(HomeOwnersTable)

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBe(false)
    expect(ownersTable.text()).not.toContain('Group 1')

    await ownersTable.find(getTestId('table-edit-btn')).trigger('click')
    await nextTick()

    const addOwnerSection = wrapper.findComponent(HomeOwnersTable).findComponent(AddEditHomeOwner)

    // edit owner should be open
    expect(addOwnerSection.exists()).toBeTruthy()

    // make updates to the owner
    await addOwnerSection.findInputByTestId('first-name').setValue('Jean-Claude')
    await addOwnerSection.findInputByTestId('middle-name').setValue('Van')
    await addOwnerSection.findInputByTestId('last-name').setValue('Damme')

    expect(store.getMhrRegistrationHomeOwnerGroups[0].owners.length).toBe(2)
    await clickDoneAddOwner()

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()

    ownersTable = wrapper.findComponent(HomeOwnersTable)

    // check for new values
    expect(ownersTable.exists()).toBeTruthy()
    expect(ownersTable.text()).toContain('Jean-Claude')
    expect(ownersTable.text()).toContain('Van')
    expect(ownersTable.text()).toContain('Damme')
  })

  it('should delete a home owner group', async () => {
    const homeOwnerGroups = [
      { groupId: 1, owners: [mockedPerson] },
      { groupId: 2, owners: [mockedOrganization] }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)

    // need to open Edit Owner section to set the showGroups flag
    await wrapper
      .findComponent(HomeOwnersTable)
      .find(getTestId('table-edit-btn'))
      .trigger('click')
    await nextTick()

    const AddEditHomeOwnerComp = wrapper.findComponent(AddEditHomeOwner)
    expect(AddEditHomeOwnerComp.exists()).toBeTruthy()
    AddEditHomeOwnerComp.vm.setShowGroups(true)
    await nextTick()

    await AddEditHomeOwnerComp
      .find(getTestId('cancel-btn'))
      .trigger('click')

    expect(AddEditHomeOwnerComp.exists()).toBeFalsy()

    const ownersTable = wrapper.findComponent(HomeOwnersTable)
    expect(ownersTable.findAllComponents(TableGroupHeader).length).toBe(2)
    expect(ownersTable.text()).toContain('Group 1')
    expect(ownersTable.text()).toContain('Group 2')

    // delete first group (person)
    const homeOwnersTableData = wrapper.findComponent(HomeOwnersTable)
    await homeOwnersTableData.vm.deleteGroup(1)

    // second group should become first
    expect(wrapper.findComponent(HomeOwnersTable).text()).toContain(mockedOrganization.organizationName)
    expect(wrapper.findComponent(HomeOwnersTable).text()).not.toContain(mockedPerson.individualName.first)
    expect(ownersTable.findAllComponents(TableGroupHeader).length).toBe(1)
  })

  it('should show fractional ownership', async () => {
    const homeOwnerGroup = [
      {
        groupId: 1,
        owners: [mockedPerson, mockedOrganization],
        interest: 'Undivided',
        interestNumerator: 123,
        interestDenominator: 432
      }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    // add a person
    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroup)

    wrapper.vm.setShowGroups(true)

    await wrapper
      .findComponent(HomeOwnersTable)
      .find(getTestId('table-edit-btn'))
      .trigger('click')

    const addOwnerSection = wrapper.findComponent(HomeOwnersTable).findComponent(AddEditHomeOwner)
    expect(addOwnerSection.exists()).toBeTruthy()

    // check for readonly fractional ownership
    const fractionalOwnershipSections = addOwnerSection.findComponent(FractionalOwnership)
    expect(fractionalOwnershipSections.exists()).toBeTruthy()
    const readonlyInterest = fractionalOwnershipSections.find(getTestId('readonly-interest-info'))
    expect(readonlyInterest.text()).toContain('Undivided 123/432')
    await clickDoneAddOwner()
  })

  it('should correctly display At Least One Owner check mark', async () => {
    await store.setMhrRegistrationHomeOwnerGroups([{ groupId: 1, owners: [mockedPerson], type: '' }])

    const registeredOwnerCheck = wrapper.find(getTestId('reg-owner-checkmark'))
    expect(registeredOwnerCheck.exists()).toBeTruthy()
    expect(registeredOwnerCheck.isVisible()).toBeTruthy()

    await store.setMhrRegistrationHomeOwnerGroups([])
    expect(
      wrapper
        .find(getTestId('reg-owner-checkmark'))
        .exists()
    ).toBeFalsy()
  })

  it('should have ability to clear the Group when only one Home Owner is in the table', async () => {
    // as per requirement, Clear Group selection button (X) should be available in...
    // ...Group dropdown when there is only one Owner and one Group in the table

    // Testing strategy:
    // 1. Add Owner and a Group
    // 2. Test that Group is displayed for the Owner
    // 3. Expand Edit Owner section and clear Group selection
    // 4. Test that Fractional Ownership is not displayed for the Owner
    // 5. Test that Group is not displayed for the Owner in the table

    const homeOwnerGroup = [
      {
        groupId: 1,
        owners: [mockedOrganization],
        interest: 'Undivided',
        interestNumerator: 123,
        interestDenominator: 432,
        type: 'SOLE'
      }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    wrapper.vm.setShowGroups(true)
    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroup)
    await nextTick()

    const homeOwnersData = wrapper.vm
    expect(homeOwnersData.getHomeOwners.length).toBe(1)
    expect(homeOwnersData.isGlobalEditingMode).toBe(false)

    await wrapper
      .findComponent(HomeOwnersTable)
      .find(getTestId('table-edit-btn'))
      .trigger('click')

    const addOwnerSection = wrapper.findComponent(AddEditHomeOwner)
    expect(addOwnerSection.exists()).toBeTruthy()

    const clearGroupButton = addOwnerSection
      .findComponent(HomeOwnerGroups)
      .find('.owner-groups-select')
      .find('.v-icon')

    expect(clearGroupButton.exists()).toBeTruthy()
    await clearGroupButton.trigger('click')

    expect(store.getMhrRegistrationHomeOwnerGroups[0].owners.length).toBe(1)
    expect(addOwnerSection.findComponent(FractionalOwnership).exists()).toBeFalsy()
    await clickDoneAddOwner()
    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBe(false)

    const ownersTable = wrapper.findComponent(HomeOwnersTable)
    expect(ownersTable.text()).toContain('Group 1')
    expect(ownersTable.text()).toContain('N/A')
    expect(ownersTable.text()).toContain(mockedOrganization.organizationName)
    expect(ownersTable.text()).toContain(mockedOrganization.phoneNumber)
  })

  it('should keep the Group shown after clearing dropdown but then clicking Cancel', async () => {
    const homeOwnerGroup = [
      {
        groupId: 1,
        owners: [mockedPerson],
        interest: 'Undivided',
        interestNumerator: 111,
        interestDenominator: 777,
        type: 'SOLE'
      }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroup)

    const homeOwnersData = wrapper.vm
    homeOwnersData.setShowGroups(true)
    expect(homeOwnersData.getHomeOwners.length).toBe(1)
    expect(homeOwnersData.isGlobalEditingMode).toBe(false)

    await wrapper
      .findComponent(HomeOwnersTable)
      .find(getTestId('table-edit-btn'))
      .trigger('click')

    const addOwnerSection = wrapper.findComponent(AddEditHomeOwner)

    const clearGroupButton = addOwnerSection
      .findComponent(HomeOwnerGroups)
      .find('.owner-groups-select')
      .find('.v-icon')

    await clearGroupButton.trigger('click')
    await clickCancelAddOwner()

    const ownersTable = wrapper.findComponent(HomeOwnersTable)
    expect(ownersTable.text()).toContain('Group 1')
    expect(ownersTable.text()).toContain(mockedPerson.individualName.first)
    expect(ownersTable.text()).toContain(mockedPerson.individualName.last)
    expect(ownersTable.text()).toContain(mockedPerson.phoneNumber)

    const groupHeader = ownersTable.findComponent(TableGroupHeader)
    groupHeader.vm.cancelOrProceed(true, '1')
  })

  it('should show correct error messages when deleting Owners from the Home Owners table', async () => {
    // Should show 'Group must contain at least one owner' when there are no Owners in a Group
    // Should show 'No owners added yet' when there are no Owners and no Groups
    const GROUP_ID = 1

    const homeOwnerGroup = [
      {
        groupId: GROUP_ID,
        owners: [mockedPerson],
        interest: 'Undivided',
        interestNumerator: 10,
        interestDenominator: 20
      }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroup)
    wrapper.vm.setShowGroups(true)
    await nextTick()

    const ownersTable = wrapper.findComponent(HomeOwnersTable)
    expect(ownersTable.text()).toContain('Group ' + GROUP_ID)
    expect(ownersTable.findAllComponents(TableGroupHeader).length).toBe(1) // only one Group exists
    expect(wrapper.vm.getHomeOwners.length).toBe(1) // only one Owner exists

    // Delete Owner and check for correct error message
    ownersTable.vm.remove({ ...mockedPerson, groupId: GROUP_ID })
    await nextTick()
    expect(ownersTable.text()).toContain('Group ' + GROUP_ID)
    expect(ownersTable.text()).toContain('10/20')
    expect(ownersTable.find(getTestId('no-owners-msg-group-0'))).toBeTruthy()
    expect(ownersTable.findAllComponents(TableGroupHeader).length).toBe(1) // only one Group exists

    // Delete Owners Group and check for correct error message
    const groupHeader = ownersTable.findComponent(TableGroupHeader)
    groupHeader.vm.cancelOrProceed(true, GROUP_ID)
    await nextTick()
    expect(ownersTable.text()).not.toContain('Group ' + GROUP_ID)
    expect(ownersTable.find(getTestId('no-data-msg'))).toBeTruthy()
    expect(ownersTable.findAllComponents(TableGroupHeader).length).toBe(0) // no Groups exists
    expect(wrapper.vm.getHomeOwners.length).toBe(0) // no Owners exists
  })

  it('should show correct Home Tenancy Type for MHR Registration', async () => {
    const homeOwnerGroup: MhrRegistrationHomeOwnerGroupIF[] = [{ groupId: 1, owners: [mockedPerson], type: '' }]

    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroup)
    wrapper.vm.setShowGroups(false)
    await nextTick()

    expect(store.getMhrRegistrationHomeOwners.length).toBe(1)
    expect(
      wrapper
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.SOLE)

    // Add a second Owner to the Group
    const updatedHomeOwnerGroup = [...homeOwnerGroup] // create a new array so the changes could be detected when setting the store
    updatedHomeOwnerGroup[0].owners.push(mockedOrganization)

    await store.setMhrRegistrationHomeOwnerGroups(updatedHomeOwnerGroup)
    await nextTick()
    expect(store.getMhrRegistrationHomeOwners.length).toBe(2)

    expect(
      wrapper
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.JOINT)

    // Enable Groups
    wrapper.vm.setShowGroups(true)
    await nextTick()

    expect(
      wrapper
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.COMMON)
  })

  it('should show Mixed Role error', async () => {
    const homeOwnerGroups: MhrRegistrationHomeOwnerGroupIF[] = [
      {
        groupId: 1,
        owners: [mockedOwner, mockedExecutor],
        type: ''
      }
    ]
    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)
    await nextTick()

    let homeOwners = wrapper
    const MixedRolesError = homeOwners.find(getTestId('mixed-owners-msg-group-1'))
    expect(MixedRolesError.exists()).toBeTruthy()
    expect(MixedRolesError.text()).toContain(MixedRolesErrors.hasMixedOwnerTypes)

    // add one more owner to the second group to trigger a new error message
    homeOwnerGroups.push({
      groupId: 2,
      owners: [mockedExecutor, mockedExecutor],
      type: ''
    } as MhrRegistrationHomeOwnerGroupIF)

    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroups)
    homeOwners = await createComponent(HomeOwners)

    expect(homeOwners.find(getTestId('mixed-owners-msg-group-1')).text()).toContain(MixedRolesErrors.hasMixedOwnerTypesInGroup)

    // Expect the error message to be shown for the first group only
    expect(homeOwners.find(getTestId('mixed-owners-msg-group-1')).exists()).toBeTruthy()
    expect(homeOwners.find(getTestId('mixed-owners-msg-group-2')).exists()).toBeFalsy()
  })

  it('should remove error message if no longer has mixed role', async () => {
    const homeOwnerGroups: MhrRegistrationHomeOwnerGroupIF[] = [
      {
        groupId: 1,
        owners: [mockedOwner, mockedExecutor],
        type: ''
      }
    ]
    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)
    wrapper = await createComponent(HomeOwners, { validateTransfer: true })
    await nextTick()
    // Verify Length
    expect(wrapper.vm.getHomeOwners.length).toBe(2)

    // Verify Error Messaging
    const MixedRolesError = await wrapper.find(getTestId('mixed-owners-msg-group-1'))
    expect(MixedRolesError.exists()).toBe(true)
    expect(wrapper.find('.border-error-left').exists()).toBe(true)

    await store.setMhrRegistrationHomeOwnerGroups([{ ...homeOwnerGroups[0], owners: [mockedOwner] }])
    await nextTick()

    expect(wrapper.vm.getHomeOwners.length).toBe(1)
    const MixedRolesErrorAfterUpdate = await wrapper.find(getTestId('mixed-owners-msg-group-1'))

    expect(MixedRolesErrorAfterUpdate.exists()).toBe(false)
    expect(wrapper.find('.border-error-left').exists()).toBe(false)
  })

  it('should have correct validations for mixed owners types in the table', async () => {
    let homeOwners = wrapper

    expect(homeOwners.vm.getHomeOwners.length).toBe(0)
    expect(homeOwners.exists()).toBeTruthy()

    const homeOwnerGroup: MhrRegistrationHomeOwnerGroupIF[] = [
      {
        groupId: 1,
        owners: [mockedOwner, mockedPerson],
        type: ''
      }
    ]
    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroup)
    await nextTick()

    homeOwners = await createComponent(HomeOwners, { validateTransfer: true })

    // should not have border or group errors
    expect(homeOwners.find('.border-error-left').exists()).toBeFalsy()
    expect(homeOwners.find(getTestId('mixed-owners-msg-group-1')).exists()).toBeFalsy()

    // add one more owner to the second group to trigger group validation
    const updatedHomeOwnerGroup = [...homeOwnerGroup]
    updatedHomeOwnerGroup[0].owners.push(mockedExecutor)

    expect(updatedHomeOwnerGroup[0].owners.length).toBe(3)

    await store.setMhrRegistrationHomeOwnerGroups(updatedHomeOwnerGroup)
    await nextTick()

    expect(homeOwners.vm.getHomeOwners.length).toBe(3)

    // should have border and group errors because of mixed owners
    expect(homeOwners.find('.border-error-left').exists()).toBeTruthy()
    const MixedRolesError = homeOwners.find(getTestId('mixed-owners-msg-group-1'))

    expect(MixedRolesError.exists()).toBeTruthy()

    expect(MixedRolesError.text()).toContain(MixedRolesErrors.hasMixedOwnerTypes)

    const updatedHomeOwnerGroup2 = [...updatedHomeOwnerGroup]
    updatedHomeOwnerGroup2[0].owners.pop()
    await store.setMhrRegistrationHomeOwnerGroups(updatedHomeOwnerGroup2)

    expect(homeOwners.vm.getHomeOwners.length).toBe(2)
    expect(wrapper.find('.border-error-left').exists()).toBeFalsy()
    expect(homeOwners.find(getTestId('mixed-owners-msg-group-1')).exists()).toBeFalsy()
  })

  it('should show and be enabled all Home Owner roles', async () => {
    openAddPerson()
    await nextTick()

    const HomeOwnerRolesComponent = wrapper.findComponent(HomeOwnerRoles)
    expect(HomeOwnerRolesComponent.exists()).toBeTruthy()
    const radioButtons = HomeOwnerRolesComponent.findAll('input[type="radio"]')
    expect(radioButtons).toHaveLength(4)

    radioButtons.forEach(radioButton => {
      expect(radioButton.getCurrentComponent().props.disabled).toBe(false)
    })
  })
})

describe('HomeOwner Corrections', () => {
  let wrapper
  const { initDraftOrCurrentMhr } = useNewMhrRegistration()

  beforeEach(async () => {
    defaultFlagSet['mhr-registration-enabled'] = true
    await store.setRegistrationType(MhrCorrectionStaff)
    await initDraftOrCurrentMhr(mockedMhrRegistration)
    wrapper = await createComponent(HomeOwners, { appReady: true }, RouteNames.HOME_OWNERS)
    await nextTick()
  })

  afterEach(async () => {
    // reset store
    await initDraftOrCurrentMhr(mockedMhrRegistration)
  })

  // Helper functions
  const openAddPerson = async () => {
    await wrapper.find(getTestId('add-person-btn')).trigger('click')
    await nextTick()
    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeTruthy()
    expect(wrapper.findComponent(HomeOwnerGroups).exists()).toBeTruthy()
  }

  const openAddOrganization = async () => {
    await wrapper.find(getTestId('add-org-btn')).trigger('click')
    await nextTick()
    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeTruthy()
    expect(wrapper.findComponent(HomeOwnerGroups).exists()).toBeTruthy()
  }

  const clickCancelAddOwner = async () => {
    const addOwnerSection = wrapper.findComponent(AddEditHomeOwner)
    expect(addOwnerSection.exists).toBeTruthy()
    const cancelBtn = addOwnerSection.find(getTestId('cancel-btn'))
    expect(cancelBtn.exists()).toBeTruthy()
    await cancelBtn.trigger('click')
    await nextTick()
    expect(addOwnerSection.exists()).toBeFalsy()
  }

  const clickDoneAddOwner = async () => {
    const addOwnerSection = wrapper.findComponent(AddEditHomeOwner)
    const doneBtn = addOwnerSection.find(getTestId('done-btn'))
    expect(doneBtn.exists()).toBeTruthy()
    await addOwnerSection.vm.addHomeOwnerForm.validate()
    await doneBtn.trigger('click')

    setTimeout(async () => {
      expect(addOwnerSection.exists()).toBeFalsy() // Hidden by default
    }, 500)
  }

  it('renders Home Owners and its sub components', () => {
    expect(wrapper.exists()).toBeTruthy()
    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy() // Hidden by default
    expect(wrapper.findComponent(HomeOwnersTable).exists()).toBeTruthy()
    expect(wrapper.findComponent(SimpleHelpToggle).exists()).toBeTruthy()
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

  it('renders home owner (person and org)', async () => {
    const homeOwnerGroup = mockedMhrRegistration.ownerGroups as MhrRegistrationHomeOwnerGroupIF[]
    const homeOwner = mockedMhrRegistration.ownerGroups[0].owners[0]
    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()

    let ownersTable = await wrapper.findComponent(HomeOwnersTable)

    // renders all fields
    expect(ownersTable.exists()).toBeTruthy()
    expect(ownersTable.text()).toContain(homeOwner.individualName.first)
    expect(ownersTable.text()).toContain(homeOwner.individualName.last)
    expect(ownersTable.text()).toContain(homeOwner.individualName.middle)
    expect(ownersTable.text()).toContain(homeOwner.address.street)
    expect(ownersTable.text()).toContain(homeOwner.address.city)
    expect(ownersTable.text()).toContain(homeOwner.address.region)
    expect(ownersTable.text()).toContain('Canada')
    expect(ownersTable.text()).toContain(homeOwner.address.postalCode)
    // there should be no grouping shown in the table because we didn't select a group during add
    expect(ownersTable.text()).toContain('Group 1')

    // there should not be Added badge for a baseline owner in Corrections
    const addedBadge = ownersTable.find(getTestId('owner-added-badge'))
    expect(addedBadge.exists()).toBeFalsy()

    // add an organization
    homeOwnerGroup[0].owners.push(mockedOrganization)
    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroup)

    wrapper = await createComponent(HomeOwners)
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
    expect(ownersTable.text()).toContain('Group 1')
  })

  it('should correct home owner', async () => {
    const homeOwnerGroup = [
      { groupId: 1, owners: [mockedPerson, mockedOrganization] }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroup)

    let ownersTable = wrapper.findComponent(HomeOwnersTable)

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBe(false)
    expect(ownersTable.text()).toContain('Group 1')

    await ownersTable.find(getTestId('table-edit-btn')).trigger('click')
    await nextTick()

    const addOwnerSection = wrapper.findComponent(HomeOwnersTable).findComponent(AddEditHomeOwner)

    // edit owner should be open
    expect(addOwnerSection.exists()).toBeTruthy()

    // make updates to the owner
    await addOwnerSection.findInputByTestId('first-name').setValue('Jean-Claude')
    await addOwnerSection.findInputByTestId('middle-name').setValue('Van')
    await addOwnerSection.findInputByTestId('last-name').setValue('Damme')

    expect(store.getMhrRegistrationHomeOwnerGroups[0].owners.length).toBe(2)
    await clickDoneAddOwner()

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()

    ownersTable = wrapper.findComponent(HomeOwnersTable)

    // check for new values
    expect(ownersTable.exists()).toBeTruthy()
    expect(ownersTable.text()).toContain('Jean-Claude')
    expect(ownersTable.text()).toContain('Van')
    expect(ownersTable.text()).toContain('Damme')
  })

  it('should delete a home owner group', async () => {
    const homeOwnerGroups = [
      { groupId: 1, owners: [mockedPerson] },
      { groupId: 2, owners: [mockedOrganization] }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)

    // need to open Edit Owner section to set the showGroups flag
    await wrapper
      .findComponent(HomeOwnersTable)
      .find(getTestId('table-edit-btn'))
      .trigger('click')
    await nextTick()

    const AddEditHomeOwnerComp = wrapper.findComponent(AddEditHomeOwner)
    expect(AddEditHomeOwnerComp.exists()).toBeTruthy()
    AddEditHomeOwnerComp.vm.setShowGroups(true)
    await nextTick()

    await AddEditHomeOwnerComp
      .find(getTestId('cancel-btn'))
      .trigger('click')

    expect(AddEditHomeOwnerComp.exists()).toBeFalsy()

    const ownersTable = wrapper.findComponent(HomeOwnersTable)
    expect(ownersTable.findAllComponents(TableGroupHeader).length).toBe(2)
    expect(ownersTable.text()).toContain('Group 1')
    expect(ownersTable.text()).toContain('Group 2')

    // delete first group (person)
    const homeOwnersTableData = wrapper.findComponent(HomeOwnersTable)
    await homeOwnersTableData.vm.deleteGroup(1)

    // second group should become first
    expect(wrapper.findComponent(HomeOwnersTable).text()).toContain(mockedOrganization.organizationName)
    expect(wrapper.findComponent(HomeOwnersTable).text()).not.toContain(mockedPerson.individualName.first)
    expect(ownersTable.findAllComponents(TableGroupHeader).length).toBe(1)
  })

  it('should hide fractional ownership on Home owner edit', async () => {
    const homeOwnerGroup = [
      {
        groupId: 1,
        owners: [mockedPerson, mockedOrganization],
        interest: 'Undivided',
        interestNumerator: 123,
        interestDenominator: 432
      }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    // add a person
    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroup)

    wrapper.vm.setShowGroups(true)

    await wrapper
      .findComponent(HomeOwnersTable)
      .find(getTestId('table-edit-btn'))
      .trigger('click')

    const addOwnerSection = wrapper.findComponent(HomeOwnersTable).findComponent(AddEditHomeOwner)
    expect(addOwnerSection.exists()).toBeTruthy()

    // verify no fractional ownership
    const fractionalOwnershipSections = addOwnerSection.findComponent(FractionalOwnership)
    expect(fractionalOwnershipSections.exists()).toBeFalsy()
    await clickDoneAddOwner()
  })

  it('should correctly display At Least One Owner check mark', async () => {
    await store.setMhrRegistrationHomeOwnerGroups([{ groupId: 1, owners: [mockedPerson], type: '' }])

    const registeredOwnerCheck = wrapper.find(getTestId('reg-owner-checkmark'))
    expect(registeredOwnerCheck.exists()).toBeTruthy()
    expect(registeredOwnerCheck.isVisible()).toBeTruthy()

    await store.setMhrRegistrationHomeOwnerGroups([])
    expect(
      wrapper
        .find(getTestId('reg-owner-checkmark'))
        .exists()
    ).toBeFalsy()
  })

  it('should show correct error messages when deleting Owners from the Home Owners table', async () => {
    const GROUP_ID = 1

    const homeOwnerGroup = [
      {
        groupId: GROUP_ID,
        owners: [mockedPerson],
        interest: 'Undivided',
        interestNumerator: 10,
        interestDenominator: 20
      }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroup)
    wrapper.vm.setShowGroups(true)
    await nextTick()

    const ownersTable = wrapper.findComponent(HomeOwnersTable)
    expect(ownersTable.text()).toContain('Group ' + GROUP_ID)
    expect(ownersTable.findAllComponents(TableGroupHeader).length).toBe(1) // only one Group exists
    expect(wrapper.vm.getHomeOwners.length).toBe(1) // only one Owner exists

    // Delete Owner and check for correct error message
    ownersTable.vm.remove({ ...mockedPerson, groupId: GROUP_ID })
    await nextTick()
    expect(ownersTable.text()).toContain('Group ' + GROUP_ID)
    expect(ownersTable.text()).toContain('10/20')
    expect(ownersTable.find(getTestId('no-owners-msg-group-0'))).toBeTruthy()
    expect(ownersTable.findAllComponents(TableGroupHeader).length).toBe(1) // only one Group exists

    // Delete Owners Group and check for correct error message
    const groupHeader = ownersTable.findComponent(TableGroupHeader)
    groupHeader.vm.cancelOrProceed(true, GROUP_ID)
    await nextTick()
    expect(ownersTable.text()).not.toContain('Group ' + GROUP_ID)
    expect(ownersTable.find(getTestId('no-data-msg'))).toBeTruthy()
    expect(ownersTable.findAllComponents(TableGroupHeader).length).toBe(0) // no Groups exists
    expect(wrapper.vm.getHomeOwners.length).toBe(0) // no Owners exists
  })

  it('should show correct Home Tenancy Type for MHR Registration', async () => {
    expect(store.getMhrRegistrationHomeOwners.length).toBe(4)
    expect(
      wrapper
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.COMMON)

    // Add a fifth Owner
    const updatedHomeOwnerGroup = [...mockedMhrRegistration.ownerGroups] // create a new array so the changes could be detected when setting the store
    updatedHomeOwnerGroup[0].owners.push(mockedOrganization)

    await store.setMhrRegistrationHomeOwnerGroups(updatedHomeOwnerGroup)
    await nextTick()
    expect(store.getMhrRegistrationHomeOwners.length).toBe(5)

    expect(
      wrapper
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.COMMON)

    // Enable Groups
    wrapper.vm.setShowGroups(true)
    await nextTick()

    expect(
      wrapper
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.COMMON)
  })

  it('should not show Mixed Role error', async () => {
    const homeOwnerGroups: MhrRegistrationHomeOwnerGroupIF[] = [
      {
        groupId: 1,
        owners: [mockedOwner, mockedExecutor],
        type: ''
      }
    ]
    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)
    await nextTick()

    let homeOwners = wrapper
    const MixedRolesError = homeOwners.find(getTestId('mixed-owners-msg-group-1'))
    expect(MixedRolesError.exists()).toBeFalsy()

    // add one more owner to the second group to trigger a new error message
    homeOwnerGroups.push({
      groupId: 2,
      owners: [mockedExecutor, mockedExecutor],
      type: ''
    } as MhrRegistrationHomeOwnerGroupIF)

    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroups)
    homeOwners = await createComponent(HomeOwners)

    expect(homeOwners.find(getTestId('mixed-owners-msg-group-1')).text()).toContain(MixedRolesErrors.hasMixedOwnerTypesInGroup)

    // Expect the error message to be shown for the first group only
    expect(homeOwners.find(getTestId('mixed-owners-msg-group-1')).exists()).toBeTruthy()
    expect(homeOwners.find(getTestId('mixed-owners-msg-group-2')).exists()).toBeFalsy()
  })

  it('should show and be enabled all Home Owner roles', async () => {
    openAddPerson()
    await nextTick()

    const HomeOwnerRolesComponent = wrapper.findComponent(HomeOwnerRoles)
    expect(HomeOwnerRolesComponent.exists()).toBeTruthy()
    const radioButtons = HomeOwnerRolesComponent.findAll('input[type="radio"]')
    expect(radioButtons).toHaveLength(4)

    radioButtons.forEach(radioButton => {
      expect(radioButton.getCurrentComponent().props.disabled).toBe(false)
    })
  })
})

