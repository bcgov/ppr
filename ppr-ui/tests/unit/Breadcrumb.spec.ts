// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
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
import { defaultFlagSet, getRoleProductCode } from '@/utils'
import { nextTick } from '@vue/composition-api'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// selectors
const backBtn = '#breadcrumb-back-btn'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (mockRoute: string, setCurrentPath: string, setCurrentPathName: RouteNames): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  localVue.use(VueRouter)
  const router = mockRouter.mock()
  router.push({ name: mockRoute })

  return mount(Breadcrumb, {
    localVue,
    propsData: {
      setCurrentPath: setCurrentPath,
      setCurrentPathName: setCurrentPathName
    },
    store,
    router,
    vuetify
  })
}

async function assertBreadcrumbItemForRole (
  wrapper: Wrapper<any>,
  roles: Array<AuthRoles>,
  breadcrumbItemContent: string,
  subscribedProductsCodes: Array<ProductCode> = []
) {
  await store.dispatch('setAuthRoles', roles)
  await store.dispatch('setRoleSbc', !roles.includes(AuthRoles.PUBLIC))
  await store.dispatch('setUserProductSubscriptionsCodes', subscribedProductsCodes)

  wrapper = createComponent(RouteNames.DASHBOARD, dashboardRoute.path, dashboardRoute.name)
  const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
  expect(breadcrumbs.length).toBe(tombstoneBreadcrumbDashboard.length)
  expect(breadcrumbs.at(1).text()).toContain(breadcrumbItemContent)
}

const dashboardRoute = routes.find(obj => {
  return obj.name === RouteNames.DASHBOARD
})
const searchRoute = routes.find(obj => {
  return obj.name === RouteNames.SEARCH
})
const addLengthTrustRoute = routes.find(obj => {
  return obj.name === RouteNames.LENGTH_TRUST
})
const addPartiesRoute = routes.find(obj => {
  return obj.name === RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS
})
const addCollateralRoute = routes.find(obj => {
  return obj.name === RouteNames.ADD_COLLATERAL
})
const confirmNewRegRoute = routes.find(obj => {
  return obj.name === RouteNames.REVIEW_CONFIRM
})
const reviewDischargeRoute = routes.find(obj => {
  return obj.name === RouteNames.REVIEW_DISCHARGE
})
const confirmDischargeRoute = routes.find(obj => {
  return obj.name === RouteNames.CONFIRM_DISCHARGE
})
const reviewRenewRoute = routes.find(obj => {
  return obj.name === RouteNames.RENEW_REGISTRATION
})
const confirmRenewRoute = routes.find(obj => {
  return obj.name === RouteNames.CONFIRM_RENEWAL
})
const reviewAmendRoute = routes.find(obj => {
  return obj.name === RouteNames.AMEND_REGISTRATION
})
const confirmAmendRoute = routes.find(obj => {
  return obj.name === RouteNames.CONFIRM_AMENDMENT
})

describe('Breadcrumb component tests', () => {
  let wrapper: any
  const { assign } = window.location

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any
    await store.dispatch('setAuthRoles', ['staff', 'ppr', 'sbc'])
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
  })

  it('renders on dashboard with breadcrumb', () => {
    wrapper = createComponent(RouteNames.DASHBOARD, dashboardRoute.path, dashboardRoute.name)
    const userRoleProductCode = getRoleProductCode(store.getters.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbDashboard.length)
    tombstoneBreadcrumbDashboard[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbDashboard.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbDashboard[i].text))
    }
  })

  it('renders on search with breadcrumb', () => {
    wrapper = createComponent(RouteNames.SEARCH, searchRoute.path, searchRoute.name)
    const userRoleProductCode = getRoleProductCode(store.getters.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbSearch.length)
    tombstoneBreadcrumbSearch[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbSearch.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbSearch[i].text))
    }
  })

  it('renders on discharge: review discharge with breadcrumb', () => {
    wrapper = createComponent(RouteNames.REVIEW_DISCHARGE, reviewDischargeRoute.path, reviewDischargeRoute.name)
    const userRoleProductCode = getRoleProductCode(store.getters.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbDischarge.length)
    tombstoneBreadcrumbDischarge[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbDischarge.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbDischarge[i].text))
    }
  })

  it('renders on discharge: confirm discharge with breadcrumb', () => {
    wrapper = createComponent(RouteNames.CONFIRM_DISCHARGE, confirmDischargeRoute.path, confirmDischargeRoute.name)
    const userRoleProductCode = getRoleProductCode(store.getters.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbDischarge.length)
    tombstoneBreadcrumbDischarge[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbDischarge.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbDischarge[i].text))
    }
  })

  it('renders on new reg: length trust with breadcrumb', () => {
    wrapper = createComponent(RouteNames.LENGTH_TRUST, addLengthTrustRoute.path, addLengthTrustRoute.name)
    const userRoleProductCode = getRoleProductCode(store.getters.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRegistration.length)
    tombstoneBreadcrumbRegistration[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbRegistration.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbRegistration[i].text))
    }
  })

  it('renders on new reg: secured parties / debtors with breadcrumb', () => {
    wrapper = createComponent(RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS, addPartiesRoute.path, addPartiesRoute.name)
    const userRoleProductCode = getRoleProductCode(store.getters.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRegistration.length)
    tombstoneBreadcrumbRegistration[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbRegistration.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbRegistration[i].text))
    }
  })

  it('renders on new reg: collateral with breadcrumb', () => {
    wrapper = createComponent(RouteNames.ADD_COLLATERAL, addCollateralRoute.path, addCollateralRoute.name)
    const userRoleProductCode = getRoleProductCode(store.getters.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRegistration.length)
    tombstoneBreadcrumbRegistration[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbRegistration.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbRegistration[i].text))
    }
  })

  it('renders on new reg: review confirm with breadcrumb', () => {
    wrapper = createComponent(RouteNames.REVIEW_CONFIRM, confirmNewRegRoute.path, confirmNewRegRoute.name)
    const userRoleProductCode = getRoleProductCode(store.getters.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRegistration.length)
    tombstoneBreadcrumbRegistration[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbRegistration.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbRegistration[i].text))
    }
  })

  it('renders on renew: review renewal with breadcrumb', () => {
    wrapper = createComponent(RouteNames.RENEW_REGISTRATION, reviewRenewRoute.path, reviewRenewRoute.name)
    const userRoleProductCode = getRoleProductCode(store.getters.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRenewal.length)
    tombstoneBreadcrumbRenewal[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbRenewal.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbRenewal[i].text))
    }
  })

  it('renders on renew: confirm renewal with breadcrumb', () => {
    wrapper = createComponent(RouteNames.CONFIRM_RENEWAL, confirmRenewRoute.path, confirmRenewRoute.name)
    const userRoleProductCode = getRoleProductCode(store.getters.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRenewal.length)
    tombstoneBreadcrumbRenewal[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbRenewal.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbRenewal[i].text))
    }
  })

  it('renders on amendment: review amendment with breadcrumb', () => {
    wrapper = createComponent(RouteNames.AMEND_REGISTRATION, reviewAmendRoute.path, reviewAmendRoute.name)
    const userRoleProductCode = getRoleProductCode(store.getters.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbAmendment.length)
    tombstoneBreadcrumbAmendment[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbAmendment.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbAmendment[i].text))
    }
  })

  it('renders on amendment: confirm amendment with breadcrumb', () => {
    wrapper = createComponent(RouteNames.CONFIRM_AMENDMENT, confirmAmendRoute.path, confirmAmendRoute.name)
    const userRoleProductCode = getRoleProductCode(store.getters.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbAmendment.length)
    tombstoneBreadcrumbAmendment[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbAmendment.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbAmendment[i].text))
    }
  })

  it('renders staff dashboard with breadcrumb', () => {
    wrapper = createComponent(RouteNames.DASHBOARD, dashboardRoute.path, dashboardRoute.name)
    const userRoleProductCode = getRoleProductCode(store.getters.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbDashboard.length)
    tombstoneBreadcrumbAmendment[1].text = breadcrumbsTitles[userRoleProductCode]
    expect(breadcrumbs.at(1).text()).toContain('Staff')
  })

  it('displays different breadcrumbs for different auth roles', async () => {
    await store.dispatch('setAuthRoles', [])
    await store.dispatch('setRoleSbc', false)
    await store.dispatch('setUserProductSubscriptionsCodes', [])

    const STAFF_PPR = [AuthRoles.STAFF, AuthRoles.PPR]
    const STAFF_MHR = [AuthRoles.STAFF, AuthRoles.MHR]
    const CLIENT_MHR = [AuthRoles.PUBLIC, AuthRoles.MHR]
    const CLIENT_PPR = [AuthRoles.PUBLIC, AuthRoles.PPR]
    const STAFF_PPR_MHR = [AuthRoles.STAFF, AuthRoles.PPR, AuthRoles.MHR]
    const CLIENT_PPR_MHR = [AuthRoles.PUBLIC, AuthRoles.PPR, AuthRoles.MHR]

    defaultFlagSet['mhr-ui-enabled'] = false
    await assertBreadcrumbItemForRole(wrapper, CLIENT_PPR, 'My Personal Property Registry', [ProductCode.PPR])
    await assertBreadcrumbItemForRole(wrapper, STAFF_PPR, 'Staff Personal Property Registry')
    await assertBreadcrumbItemForRole(wrapper, STAFF_MHR, 'Staff Personal Property Registry')
    defaultFlagSet['mhr-ui-enabled'] = true
    await assertBreadcrumbItemForRole(wrapper, STAFF_PPR, 'Staff Asset Registries')
    await assertBreadcrumbItemForRole(wrapper, STAFF_MHR, 'Staff Asset Registries')
    await assertBreadcrumbItemForRole(wrapper, CLIENT_MHR, 'My Manufactured Home Registry', [ProductCode.MHR])
    await assertBreadcrumbItemForRole(wrapper, STAFF_PPR_MHR, 'Staff Asset Registries', [])
    await assertBreadcrumbItemForRole(wrapper, CLIENT_PPR_MHR, 'My Asset Registries', [
      ProductCode.MHR,
      ProductCode.PPR
    ])
  })
})
