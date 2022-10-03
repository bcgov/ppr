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
import { mockedPerson } from './test-data/mock-mhr-registration'
import { MhrRegistrationHomeOwnerGroupIF, MhrRegistrationHomeOwnerIF } from '@/interfaces'

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
      appReady: true
    },
    vuetify,
    router
  })
}

describe('Mhr Registration', () => {
  let wrapper: Wrapper<any>
  const currentAccount = {
    id: 'test_id'
  }
  sessionStorage.setItem('KEYCLOAK_TOKEN', 'token')
  sessionStorage.setItem('CURRENT_ACCOUNT', JSON.stringify(currentAccount))
  sessionStorage.setItem('AUTH_API_URL', 'https://bcregistry-bcregistry-mock.apigee.net/mockTarget/auth/api/v1/')

  beforeEach(async () => {
    wrapper = createComponent()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders and displays the Mhr Information View', async () => {
    expect(wrapper.findComponent(MhrInformation).exists()).toBe(true)
    expect(wrapper.find('#mhr-information-header').text()).toContain('Manufactured Home Information')
  })

  it('renders and displays the correct sub components', async () => {
    // Sticky container w/ Fee Summary
    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
  })

  it('should render Added badge after Owner is added to the table', async () => {

    const mhrInformationComponent = wrapper.findComponent(MhrInformation)
    expect(mhrInformationComponent.exists()).toBe(true)

    expect(mhrInformationComponent.findComponent(HomeOwnersTable).exists()).toBe(true)
    expect(mhrInformationComponent.findComponent(HomeOwnersTable).find(getTestId('no-data-msg')).isVisible()).toBeTruthy()

    const owners = [mockedPerson] as MhrRegistrationHomeOwnerIF[] // same IF for Transfer and Registration
    const homeOwnerGroup = [{ groupId: '1', owners: owners }] as MhrRegistrationHomeOwnerGroupIF[]

    await store.dispatch('setMhrTransferHomeOwnerGroups', homeOwnerGroup)

    const ownersTable = mhrInformationComponent.findComponent(HomeOwners).findComponent(HomeOwnersTable)
    expect(ownersTable.text()).toContain(mockedPerson.individualName.first)
    expect(ownersTable.text()).toContain(mockedPerson.individualName.last)

    const addedBadge = ownersTable.find(getTestId('owner-added-badge'))
    expect(addedBadge.isVisible()).toBe(true)
  })
})
