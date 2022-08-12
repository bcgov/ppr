import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

import { HomeOwners } from '@/views'
import {
  AddEditHomeOwner,
  HomeOwnersTable,
  HomeOwnerGroups,
  TableGroupHeader
} from '@/components/mhrRegistration/HomeOwners'
import { SimpleHelpToggle } from '@/components/common'
import { mockedPerson, mockedOrganization } from './test-data/mock-mhr-registration'
import { getTestId } from './utils/helper-functions'
import { MhrRegistrationHomeOwnerGroupIF, MhrRegistrationHomeOwnerIF } from '@/interfaces'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(HomeOwners, {
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
  })
  afterEach(() => {
    wrapper.destroy()
  })

  // Helper functions

  const openAddPerson = async () => {
    const homeOwnersSection = wrapper.findComponent(HomeOwners)
    await homeOwnersSection.find(getTestId('add-person-btn')).trigger('click')
    await Vue.nextTick()
    expect(homeOwnersSection.findComponent(AddEditHomeOwner).exists()).toBeTruthy()
    expect(homeOwnersSection.findComponent(HomeOwnerGroups).exists()).toBeTruthy()
  }

  const openAddOrganization = async () => {
    const homeOwnersSection = wrapper.findComponent(HomeOwners)
    await homeOwnersSection.find(getTestId('add-org-btn')).trigger('click')
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

  // Tests

  it('renders Home Owners and its sub components', () => {
    expect(wrapper.findComponent(HomeOwners).exists()).toBeTruthy()
    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy() // Hidden by default
    expect(wrapper.findComponent(HomeOwnersTable).exists()).toBeTruthy()
    expect(wrapper.findComponent(SimpleHelpToggle).exists()).toBeTruthy()
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

  it('renders home owner (person and org) via store dispatch', async () => {
    const owners = [mockedPerson] as MhrRegistrationHomeOwnerIF[]
    const homeOwnerGroup = [{ groupId: '1', owners: owners }] as MhrRegistrationHomeOwnerGroupIF[]

    // add a person
    await store.dispatch('setMhrRegistrationHomeOwnerGroups', homeOwnerGroup)

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

    // add an organization
    homeOwnerGroup[0].owners.push(mockedOrganization)
    await store.dispatch('setMhrRegistrationHomeOwnerGroups', homeOwnerGroup)

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

  it('should edit home owner', async () => {
    const homeOwnerGroup = [
      { groupId: '1', owners: [mockedPerson, mockedOrganization] }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    await store.dispatch('setMhrRegistrationHomeOwnerGroups', homeOwnerGroup)

    let ownersTable = wrapper.findComponent(HomeOwners).findComponent(HomeOwnersTable)

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()
    expect(ownersTable.text()).not.toContain('Group 1')

    await ownersTable.find(getTestId('table-edit-btn')).trigger('click')

    const addOwnerSection = wrapper.findComponent(HomeOwnersTable).findComponent(AddEditHomeOwner)

    // edit owner should be open
    expect(addOwnerSection.exists()).toBeTruthy()

    // make updates to the owner
    addOwnerSection.find(getTestId('first-name')).setValue('Jean-Claude')
    addOwnerSection.find(getTestId('middle-name')).setValue('Van')
    addOwnerSection.find(getTestId('last-name')).setValue('Damme')

    await clickDoneAddOwner()

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()

    ownersTable = wrapper.findComponent(HomeOwners).findComponent(HomeOwnersTable)

    // check for new values
    expect(ownersTable.exists()).toBeTruthy()
    expect(ownersTable.text()).toContain('Jean-Claude')
    expect(ownersTable.text()).toContain('Van')
    expect(ownersTable.text()).toContain('Damme')
  })

  it('should delete a home owner group', async () => {
    const homeOwnerGroups = [
      { groupId: '1', owners: [mockedPerson] },
      { groupId: '2', owners: [mockedOrganization] }
    ] as MhrRegistrationHomeOwnerGroupIF[]

    await store.dispatch('setMhrRegistrationHomeOwnerGroups', homeOwnerGroups)

    // need to open Edit Owner section to set the showGroups flag
    await wrapper
      .findComponent(HomeOwnersTable)
      .find(getTestId('table-edit-btn'))
      .trigger('click')

    wrapper.findComponent(AddEditHomeOwner).vm.$data.showGroups = true

    await wrapper
      .findComponent(AddEditHomeOwner)
      .find(getTestId('cancel-btn'))
      .trigger('click')

    expect(wrapper.findComponent(AddEditHomeOwner).exists()).toBeFalsy()

    const ownersTable = wrapper.findComponent(HomeOwners).findComponent(HomeOwnersTable)
    expect(ownersTable.findAllComponents(TableGroupHeader).length).toBe(2)
    expect(ownersTable.text()).toContain('Group 1')
    expect(ownersTable.text()).toContain('Group 2')

    // delete first group (person)
    const homeOwnersTableData = wrapper.findComponent(HomeOwnersTable).vm.$data
    await homeOwnersTableData.deleteGroup('1')

    // second group should become first
    expect(wrapper.findComponent(HomeOwnersTable).text()).toContain(mockedOrganization.organizationName)
    expect(wrapper.findComponent(HomeOwnersTable).text()).not.toContain(mockedPerson.individualName.first)
    expect(ownersTable.findAllComponents(TableGroupHeader).length).toBe(1)
  })
})
