// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { Breadcrumb } from '@/components/common'
// Other
import { RouteNames } from '@/enums'
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
import { AddCollateral } from '@/views'

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
function createComponent (
  mockRoute: string,
  setCurrentPath: string,
  setCurrentPathName: RouteNames
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  localVue.use(VueRouter)
  const router = mockRouter.mock()
  router.push({ name: mockRoute })

  return mount(Breadcrumb, {
    localVue,
    propsData: { setCurrentPath: setCurrentPath, setCurrentPathName: setCurrentPathName },
    store,
    router,
    vuetify
  })
}

async function assertBreadcrumbItemForRole (wrapper: Wrapper<any>, roles: Array<string>, isSbc: boolean, breadcrumbItemContent: string) {
  await store.dispatch('setUserAccessRole', { authRoles: roles, isSbc })
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
    await store.dispatch('setUserAccessRole', { authRoles: ['staff', 'ppr'], isSbc: true })
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
  })

  it('renders on dashboard with breadcrumb', () => {
    wrapper = createComponent(RouteNames.DASHBOARD, dashboardRoute.path, dashboardRoute.name)
    const userRole = wrapper.vm.$store.state.stateModel.accountInformation.userAccessRole as string
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbDashboard.length)
    tombstoneBreadcrumbDashboard[1].text = breadcrumbsTitles[userRole]
    for (let i = 0; i < tombstoneBreadcrumbDashboard.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(tombstoneBreadcrumbDashboard[i].text)
    }
  })

  it('renders on search with breadcrumb', () => {
    wrapper = createComponent(RouteNames.SEARCH, searchRoute.path, searchRoute.name)
    const userRole = wrapper.vm.$store.state.stateModel.accountInformation.userAccessRole as string
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbSearch.length)
    tombstoneBreadcrumbSearch[1].text = breadcrumbsTitles[userRole]
    for (let i = 0; i < tombstoneBreadcrumbSearch.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(tombstoneBreadcrumbSearch[i].text)
    }
  })

  it('renders on discharge: review discharge with breadcrumb', () => {
    wrapper = createComponent(RouteNames.REVIEW_DISCHARGE, reviewDischargeRoute.path, reviewDischargeRoute.name)
    const userRole = wrapper.vm.$store.state.stateModel.accountInformation.userAccessRole as string
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbDischarge.length)
    tombstoneBreadcrumbDischarge[1].text = breadcrumbsTitles[userRole]
    for (let i = 0; i < tombstoneBreadcrumbDischarge.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(tombstoneBreadcrumbDischarge[i].text)
    }
  })

  it('renders on discharge: confirm discharge with breadcrumb', () => {
    wrapper = createComponent(RouteNames.CONFIRM_DISCHARGE, confirmDischargeRoute.path, confirmDischargeRoute.name)
    const userRole = wrapper.vm.$store.state.stateModel.accountInformation.userAccessRole as string
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbDischarge.length)
    tombstoneBreadcrumbDischarge[1].text = breadcrumbsTitles[userRole]
    for (let i = 0; i < tombstoneBreadcrumbDischarge.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(tombstoneBreadcrumbDischarge[i].text)
    }
  })

  it('renders on new reg: length trust with breadcrumb', () => {
    wrapper = createComponent(RouteNames.LENGTH_TRUST, addLengthTrustRoute.path, addLengthTrustRoute.name)
    const userRole = wrapper.vm.$store.state.stateModel.accountInformation.userAccessRole as string
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRegistration.length)
    tombstoneBreadcrumbRegistration[1].text = breadcrumbsTitles[userRole]
    for (let i = 0; i < tombstoneBreadcrumbRegistration.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(tombstoneBreadcrumbRegistration[i].text)
    }
  })

  it('renders on new reg: secured parties / debtors with breadcrumb', () => {
    wrapper = createComponent(RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS, addPartiesRoute.path, addPartiesRoute.name)
    const userRole = wrapper.vm.$store.state.stateModel.accountInformation.userAccessRole as string
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRegistration.length)
    tombstoneBreadcrumbRegistration[1].text = breadcrumbsTitles[userRole]
    for (let i = 0; i < tombstoneBreadcrumbRegistration.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(tombstoneBreadcrumbRegistration[i].text)
    }
  })

  it('renders on new reg: collateral with breadcrumb', () => {
    wrapper = createComponent(RouteNames.ADD_COLLATERAL, addCollateralRoute.path, addCollateralRoute.name)
    const userRole = wrapper.vm.$store.state.stateModel.accountInformation.userAccessRole as string
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRegistration.length)
    tombstoneBreadcrumbRegistration[1].text = breadcrumbsTitles[userRole]
    for (let i = 0; i < tombstoneBreadcrumbRegistration.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(tombstoneBreadcrumbRegistration[i].text)
    }
  })

  it('renders on new reg: review confirm with breadcrumb', () => {
    wrapper = createComponent(RouteNames.REVIEW_CONFIRM, confirmNewRegRoute.path, confirmNewRegRoute.name)
    const userRole = wrapper.vm.$store.state.stateModel.accountInformation.userAccessRole as string
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRegistration.length)
    tombstoneBreadcrumbRegistration[1].text = breadcrumbsTitles[userRole]
    for (let i = 0; i < tombstoneBreadcrumbRegistration.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(tombstoneBreadcrumbRegistration[i].text)
    }
  })

  it('renders on renew: review renewal with breadcrumb', () => {
    wrapper = createComponent(RouteNames.RENEW_REGISTRATION, reviewRenewRoute.path, reviewRenewRoute.name)
    const userRole = wrapper.vm.$store.state.stateModel.accountInformation.userAccessRole as string
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRenewal.length)
    tombstoneBreadcrumbRenewal[1].text = breadcrumbsTitles[userRole]
    for (let i = 0; i < tombstoneBreadcrumbRenewal.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(tombstoneBreadcrumbRenewal[i].text)
    }
  })

  it('renders on renew: confirm renewal with breadcrumb', () => {
    wrapper = createComponent(RouteNames.CONFIRM_RENEWAL, confirmRenewRoute.path, confirmRenewRoute.name)
    const userRole = wrapper.vm.$store.state.stateModel.accountInformation.userAccessRole as string
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRenewal.length)
    tombstoneBreadcrumbRenewal[1].text = breadcrumbsTitles[userRole]
    for (let i = 0; i < tombstoneBreadcrumbRenewal.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(tombstoneBreadcrumbRenewal[i].text)
    }
  })

  it('renders on amendment: review amendment with breadcrumb', () => {
    wrapper = createComponent(RouteNames.AMEND_REGISTRATION, reviewAmendRoute.path, reviewAmendRoute.name)
    const userRole = wrapper.vm.$store.state.stateModel.accountInformation.userAccessRole as string
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbAmendment.length)
    tombstoneBreadcrumbAmendment[1].text = breadcrumbsTitles[userRole]
    for (let i = 0; i < tombstoneBreadcrumbAmendment.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(tombstoneBreadcrumbAmendment[i].text)
    }
  })

  it('renders on amendment: confirm amendment with breadcrumb', () => {
    wrapper = createComponent(RouteNames.CONFIRM_AMENDMENT, confirmAmendRoute.path, confirmAmendRoute.name)
    const userRole = wrapper.vm.$store.state.stateModel.accountInformation.userAccessRole as string
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbAmendment.length)
    tombstoneBreadcrumbAmendment[1].text = breadcrumbsTitles[userRole]
    for (let i = 0; i < tombstoneBreadcrumbAmendment.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(tombstoneBreadcrumbAmendment[i].text)
    }
  })

  it('renders staff dashboard with breadcrumb', () => {
    wrapper = createComponent(RouteNames.DASHBOARD, dashboardRoute.path, dashboardRoute.name)
    const userRole = wrapper.vm.$store.state.stateModel.accountInformation.userAccessRole as string
    expect(wrapper.find(backBtn).exists()).toBe(true)
    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbDashboard.length)
    tombstoneBreadcrumbAmendment[1].text = breadcrumbsTitles[userRole]
    expect(breadcrumbs.at(1).text()).toContain('Staff')
  })

  it('displays different breadcrumbs for different auth roles', async () => {
    wrapper = createComponent(RouteNames.DASHBOARD, dashboardRoute.path, dashboardRoute.name)

    const STAFF_PPR = ['staff', 'ppr']
    const STAFF_MHR = ['staff', 'mhr']
    const CLIENT_MHR = ['mhr']
    const CLIENT_PPR = ['ppr']
    const STAFF_PPR_MHR = ['staff', 'ppr', 'mhr']
    const CLIENT_PPR_MHR = ['ppr', 'mhr']

    await assertBreadcrumbItemForRole(wrapper, STAFF_PPR, true, 'Staff Personal Property Registry')
    await assertBreadcrumbItemForRole(wrapper, STAFF_MHR, true, 'Staff Manufactured Home Registry')
    await assertBreadcrumbItemForRole(wrapper, CLIENT_MHR, false, 'My Manufactured Home Registry')
    await assertBreadcrumbItemForRole(wrapper, CLIENT_PPR, false, 'My Personal Property Registry')
    await assertBreadcrumbItemForRole(wrapper, STAFF_PPR_MHR, true, 'Staff Asset Registries')
    await assertBreadcrumbItemForRole(wrapper, CLIENT_PPR_MHR, false, 'My Asset Registries')
  })
})
