// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '@/store/store'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { Breadcrumb } from '@/components/common'
// Other
import { AuthRoles, ProductCode, RouteNames } from '@/enums'
import {
  tombstoneBreadcrumbDashboard,
  tombstoneBreadcrumbDischarge,
  tombstoneBreadcrumbRegistration,
  tombstoneBreadcrumbSearch,
  tombstoneBreadcrumbAmendment,
  tombstoneBreadcrumbRenewal,
  breadcrumbsTitles
} from '@/resources'
import { routes } from '@/router'
import { getTestId } from './utils'

// unit test resources
import mockRouter from './MockRouter'
import { mockedManufacturerAuthRoles } from './test-data'

import { defaultFlagSet, getRoleProductCode } from '@/utils'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

setActivePinia(createPinia())
const store = useStore()
const router = mockRouter.mock()

// selectors
const backBtn = '#breadcrumb-back-btn'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (mockRoute: RouteNames): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  localVue.use(VueRouter)

  router.replace({ name: mockRoute })
  document.body.setAttribute('data-app', 'true')
  return mount((Breadcrumb as any), {
    localVue,
    store,
    router,
    vuetify
  })
}

describe('Breadcrumb component tests', () => {
  let wrapper: any
  const { assign } = window.location

  beforeEach(async () => { // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any

    await store.setAuthRoles(['staff', 'ppr', 'sbc'])
    await nextTick()
  })

  afterEach(() => {
    router.replace('/')
    window.location.assign = assign
    wrapper.destroy()
  })

  it('renders on dashboard with breadcrumb', () => {
    wrapper = createComponent(RouteNames.DASHBOARD)

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbDashboard.length)

    tombstoneBreadcrumbDashboard[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbDashboard.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbDashboard[i].text))
    }
  })

  it('renders on search with breadcrumb', () => {
    wrapper = createComponent(RouteNames.SEARCH)

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbSearch.length)

    tombstoneBreadcrumbSearch[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbSearch.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbSearch[i].text))
    }
  })

  it('renders on discharge: review discharge with breadcrumb', () => {
    wrapper = createComponent(RouteNames.REVIEW_DISCHARGE)

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbDischarge.length)

    tombstoneBreadcrumbDischarge[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbDischarge.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbDischarge[i].text))
    }
  })

  it('renders on discharge: confirm discharge with breadcrumb', () => {
    wrapper = createComponent(RouteNames.CONFIRM_DISCHARGE)

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbDischarge.length)

    tombstoneBreadcrumbDischarge[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbDischarge.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbDischarge[i].text))
    }
  })

  it('renders on new reg: length trust with breadcrumb', () => {
    wrapper = createComponent(RouteNames.LENGTH_TRUST)

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRegistration.length)

    tombstoneBreadcrumbRegistration[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbRegistration.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbRegistration[i].text))
    }
  })

  it('renders on new reg: secured parties / debtors with breadcrumb', () => {
    wrapper = createComponent(RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS)

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRegistration.length)

    tombstoneBreadcrumbRegistration[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbRegistration.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbRegistration[i].text))
    }
  })

  it('renders on new reg: collateral with breadcrumb', () => {
    wrapper = createComponent(RouteNames.ADD_COLLATERAL)

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRegistration.length)

    tombstoneBreadcrumbRegistration[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbRegistration.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbRegistration[i].text))
    }
  })

  it('renders on new reg: review confirm with breadcrumb', () => {
    wrapper = createComponent(RouteNames.REVIEW_CONFIRM)

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRegistration.length)

    tombstoneBreadcrumbRegistration[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbRegistration.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbRegistration[i].text))
    }
  })

  it('renders on renew: review renewal with breadcrumb', () => {
    wrapper = createComponent(RouteNames.RENEW_REGISTRATION)

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRenewal.length)

    tombstoneBreadcrumbRenewal[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbRenewal.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbRenewal[i].text))
    }
  })

  it('renders on renew: confirm renewal with breadcrumb', () => {
    wrapper = createComponent(RouteNames.CONFIRM_RENEWAL)

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRenewal.length)

    tombstoneBreadcrumbRenewal[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbRenewal.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbRenewal[i].text))
    }
  })

  it('renders on amendment: review amendment with breadcrumb', () => {
    wrapper = createComponent(RouteNames.AMEND_REGISTRATION)

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbAmendment.length)

    tombstoneBreadcrumbAmendment[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbAmendment.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbAmendment[i].text))
    }
  })

  it('renders on amendment: confirm amendment with breadcrumb', () => {
    wrapper = createComponent(RouteNames.CONFIRM_AMENDMENT)

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbAmendment.length)

    tombstoneBreadcrumbAmendment[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbAmendment.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbAmendment[i].text))
    }
  })

  it('renders staff dashboard with breadcrumb', () => {
    wrapper = createComponent(RouteNames.DASHBOARD)

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbDashboard.length)

    tombstoneBreadcrumbAmendment[1].text = breadcrumbsTitles[userRoleProductCode]
    expect(breadcrumbs.at(1).text()).toContain('Staff')
  })

  it('renders on Mhr Registration: staff', () => {
    wrapper = createComponent(RouteNames.MHR_REGISTRATION)

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.MHR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRegistration.length)
    expect(breadcrumbs.at(1).text()).toContain('Staff')

    tombstoneBreadcrumbRegistration[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbRegistration.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbRegistration[i].text))
    }
  })

  it('renders on Mhr Registration: Manufacturer - Only Mhr', async () => {
    // Set up
    await store.setAuthRoles(mockedManufacturerAuthRoles)

    defaultFlagSet['mhr-ui-enabled'] = true

    store.setUserProductSubscriptionsCodes([ProductCode.MHR])

    await nextTick()

    wrapper = createComponent(RouteNames.MHR_REGISTRATION)

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.MHR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRegistration.length)
    expect(breadcrumbs.at(1).text()).toContain('My Manufactured Home Registry')

    tombstoneBreadcrumbRegistration[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbRegistration.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbRegistration[i].text))
    }

    // Tear down
    defaultFlagSet['mhr-ui-enabled'] = false
    store.setUserProductSubscriptionsCodes([])
  })

  it('renders on Mhr Registration: Manufacturer - MHR and PPR', async () => {
    // Set up
    await store.setAuthRoles(mockedManufacturerAuthRoles)

    defaultFlagSet['mhr-ui-enabled'] = true

    store.setUserProductSubscriptionsCodes([ProductCode.MHR, ProductCode.PPR])

    await nextTick()

    wrapper = createComponent(RouteNames.MHR_REGISTRATION)

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.MHR, ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRegistration.length)

    tombstoneBreadcrumbRegistration[1].text = breadcrumbsTitles[userRoleProductCode]
    expect(breadcrumbs.at(1).text()).toContain('My Asset')
    for (let i = 0; i < tombstoneBreadcrumbRegistration.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbRegistration[i].text))
    }

    // Tear down
    defaultFlagSet['mhr-ui-enabled'] = false
    store.setUserProductSubscriptionsCodes([])
  })
})
