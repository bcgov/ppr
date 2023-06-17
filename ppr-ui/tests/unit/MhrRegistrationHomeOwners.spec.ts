import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

import { HomeOwners } from '@/views'
import {
  AddEditHomeOwner,
  HomeOwnersTable,
  HomeOwnerGroups,
  TableGroupHeader,
  FractionalOwnership
} from '@/components/mhrRegistration/HomeOwners'
import { SimpleHelpToggle } from '@/components/common'
import { mockedPerson, mockedOrganization, mockedExecutor, mockedOwner } from './test-data'
import { getTestId } from './utils'
import { MhrRegistrationHomeOwnerGroupIF, MhrRegistrationHomeOwnerIF } from '@/interfaces'
import { HomeTenancyTypes } from '@/enums'
import { MixedRolesErrors } from '@/resources'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

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
    propsData: {},
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
    await nextTick()
  })
  afterEach(() => {
    wrapper.destroy()
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

    await doneBtn.trigger('click')
    // should not be any errors
    // expect(addOwnerSection.findAll(ERROR_MSG).length).toBe(0)
    setTimeout(async () => {
      expect(addOwnerSection.exists()).toBeFalsy() // Hidden by default
    }, 500)
  }

  // Tests

  it('renders Home Owners and its sub components', () => {
    expect(wrapper.exists()).toBeTruthy()
    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy() // Hidden by default
    expect(wrapper.findComponent(HomeOwnersTable).exists()).toBeTruthy()
    expect(wrapper.findComponent(SimpleHelpToggle).exists()).toBeTruthy()
  })

  it('renders Add Edit Home Owner and its sub components', async () => {
    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBe(false) // Hidden by default
    openAddPerson()
    await nextTick()
    await nextTick()
    clickCancelAddOwner()
    await nextTick()
    await nextTick()
    openAddOrganization()
    await nextTick()
    await nextTick()
    clickCancelAddOwner()
  })

  it('renders home owner (person and org) via store dispatch', async () => {
    const owners = [mockedPerson] as MhrRegistrationHomeOwnerIF[]
    const homeOwnerGroup = [{ groupId: 1, owners: owners }] as MhrRegistrationHomeOwnerGroupIF[]

    // add a person
    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroup)

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

    // there should be no 'Added' badge shown, as the badge is only for MHR Transfers
    const addedBadge = ownersTable.find(getTestId('owner-added-badge'))
    expect(addedBadge.exists()).toBeFalsy()

    // add an organization
    homeOwnerGroup[0].owners.push(mockedOrganization)
    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroup)

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

  it('should edit home owner', async () => {
    const homeOwnerGroup = [
      { groupId: 1, owners: [mockedPerson, mockedOrganization] }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroup)

    let ownersTable = wrapper.findComponent(HomeOwnersTable)

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()
    expect(ownersTable.text()).not.toContain('Group 1')

    await ownersTable.find(getTestId('table-edit-btn')).trigger('click')
    await nextTick()

    const addOwnerSection = wrapper.findComponent(HomeOwnersTable).findComponent(AddEditHomeOwner)

    // edit owner should be open
    expect(addOwnerSection.exists()).toBeTruthy()

    // make updates to the owner
    addOwnerSection.find(getTestId('first-name')).setValue('Jean-Claude')
    addOwnerSection.find(getTestId('middle-name')).setValue('Van')
    addOwnerSection.find(getTestId('last-name')).setValue('Damme')

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

    const AddEditHomeOwnerComp: Wrapper<any> = wrapper.findComponent(AddEditHomeOwner)
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
    const homeOwnersTableData: Wrapper<any> = wrapper.findComponent(HomeOwnersTable)
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
    clickDoneAddOwner()
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

    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroup)
    wrapper.vm.setShowGroups(true)

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

    expect(addOwnerSection.findComponent(FractionalOwnership).exists()).toBeFalsy()
    await clickDoneAddOwner()

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

    const groupHeader: Wrapper<any> = ownersTable.findComponent(TableGroupHeader)
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

    const ownersTable: Wrapper<any> = wrapper.findComponent(HomeOwnersTable)
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
    const groupHeader: Wrapper<any> = ownersTable.findComponent(TableGroupHeader)
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

    expect(wrapper.vm.getMhrRegistrationHomeOwners.length).toBe(1)
    expect(
      wrapper
        .find(getTestId('home-owner-tenancy-type'))
        .text()
    ).toBe(HomeTenancyTypes.SOLE)

    // Add a second Owner to the Group
    homeOwnerGroup.push({ groupId: 1, owners: [mockedOrganization], type: '' })

    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroup)
    await nextTick()

    expect(wrapper.vm.getMhrRegistrationHomeOwners.length).toBe(2)
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

    const homeOwners = wrapper
    const MixedRolesError = homeOwners.find(getTestId('invalid-group-mixed-owners'))
    expect(MixedRolesError.exists()).toBeTruthy()
    expect(MixedRolesError.text()).toContain(MixedRolesErrors.hasMixedOwnerTypes)

    // add one more owner to the second group to trigger a new error message
    homeOwnerGroups.push({
      groupId: 2,
      owners: [mockedExecutor, mockedExecutor],
      type: ''
    } as MhrRegistrationHomeOwnerGroupIF)

    await store.setMhrTransferHomeOwnerGroups(homeOwnerGroups)
    await nextTick()

    expect(MixedRolesError.text()).toContain(MixedRolesErrors.hasMixedOwnerTypesInGroup)

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
    await nextTick()

    const homeOwners = wrapper
    const MixedRolesError = homeOwners.find(getTestId('invalid-group-mixed-owners'))
    expect(MixedRolesError.exists()).toBeTruthy()

    // remove the executor from the group
    homeOwnerGroups[0].owners = [mockedOwner]
    await store.setMhrRegistrationHomeOwnerGroups(homeOwnerGroups)
    await nextTick()

    expect(MixedRolesError.exists()).toBeFalsy()
  })
})
