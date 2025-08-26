import { nextTick } from 'vue'
import { useStore } from '@/store/store'

// Components
import { Breadcrumb } from '@/components/common'
// Other
import { ProductCode, RouteNames } from '@/enums'
import {
  tombstoneBreadcrumbDashboard,
  tombstoneBreadcrumbDischarge,
  tombstoneBreadcrumbRegistration,
  tombstoneBreadcrumbPprSearch,
  tombstoneBreadcrumbMhrSearch,
  tombstoneBreadcrumbAmendment,
  tombstoneBreadcrumbRenewal,
  breadcrumbsTitles
} from '@/resources'
import { createComponent, getTestId } from './utils'

// unit test resources
import { mockedManufacturerAuthRoles } from './test-data'
import { defaultFlagSet, getRoleProductCode } from '@/utils'


const store = useStore()

// selectors
const backBtn = '#breadcrumb-back-btn'

describe('Breadcrumb component tests', () => {
  let wrapper: any

  beforeEach(async () => { // mock the window.location.assign function
    await store.setAuthRoles(['staff', 'ppr', 'sbc'])
    await nextTick()
  })

  it('renders on dashboard with breadcrumb', async () => {
    wrapper = await createComponent(Breadcrumb, {}, RouteNames.DASHBOARD)
    await nextTick()

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbDashboard.length)

    tombstoneBreadcrumbDashboard[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbDashboard.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbDashboard[i].text))
    }
  })

  it('renders on search with breadcrumb', async () => {
    wrapper = await createComponent(Breadcrumb, null, RouteNames.SEARCH)
    await nextTick()

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbPprSearch.length)

    tombstoneBreadcrumbPprSearch[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbPprSearch.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbPprSearch[i].text))
    }
  })

  it('renders on MHR search with breadcrumb', async () => {
    wrapper = await createComponent(Breadcrumb, null, RouteNames.MHRSEARCH)
    await nextTick()

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbMhrSearch.length)

    tombstoneBreadcrumbMhrSearch[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbMhrSearch.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbMhrSearch[i].text))
    }
  })

  it('renders on discharge: review discharge with breadcrumb', async () => {
    wrapper = await createComponent(Breadcrumb, null, RouteNames.REVIEW_DISCHARGE)
    await nextTick()

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbDischarge.length)

    tombstoneBreadcrumbDischarge[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbDischarge.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbDischarge[i].text))
    }
  })

  it('renders on discharge: confirm discharge with breadcrumb', async () => {
    wrapper = await createComponent(Breadcrumb, null, RouteNames.CONFIRM_DISCHARGE)
    await nextTick()

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbDischarge.length)

    tombstoneBreadcrumbDischarge[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbDischarge.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbDischarge[i].text))
    }
  })

  it('renders on new reg: length trust with breadcrumb', async () => {
    wrapper = await createComponent(Breadcrumb, null, RouteNames.LENGTH_TRUST)
    await nextTick()

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRegistration.length)

    tombstoneBreadcrumbRegistration[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbRegistration.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbRegistration[i].text))
    }
  })

  it('renders on new reg: secured parties / debtors with breadcrumb', async () => {
    wrapper = await createComponent(Breadcrumb, null, RouteNames.ADD_SECUREDPARTIES_AND_DEBTORS)
    await nextTick()

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRegistration.length)

    tombstoneBreadcrumbRegistration[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbRegistration.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbRegistration[i].text))
    }
  })

  it('renders on new reg: collateral with breadcrumb', async () => {
    wrapper = await createComponent(Breadcrumb, null, RouteNames.ADD_COLLATERAL)
    await nextTick()

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRegistration.length)

    tombstoneBreadcrumbRegistration[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbRegistration.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbRegistration[i].text))
    }
  })

  it('renders on new reg: review confirm with breadcrumb', async () => {
    wrapper = await createComponent(Breadcrumb, null, RouteNames.REVIEW_CONFIRM)
    await nextTick()

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRegistration.length)

    tombstoneBreadcrumbRegistration[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbRegistration.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbRegistration[i].text))
    }
  })

  it('renders on renew: review renewal with breadcrumb', async () => {
    wrapper = await createComponent(Breadcrumb, null, RouteNames.RENEW_REGISTRATION)
    await nextTick()

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRenewal.length)

    tombstoneBreadcrumbRenewal[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbRenewal.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbRenewal[i].text))
    }
  })

  it('renders on renew: confirm renewal with breadcrumb', async () => {
    wrapper = await createComponent(Breadcrumb, null, RouteNames.CONFIRM_RENEWAL)
    await nextTick()

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbRenewal.length)

    tombstoneBreadcrumbRenewal[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbRenewal.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbRenewal[i].text))
    }
  })

  it('renders on amendment: review amendment with breadcrumb', async () => {
    wrapper = await createComponent(Breadcrumb, null, RouteNames.AMEND_REGISTRATION)
    await nextTick()

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbAmendment.length)

    tombstoneBreadcrumbAmendment[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbAmendment.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbAmendment[i].text))
    }
  })

  it('renders on amendment: confirm amendment with breadcrumb', async () => {
    wrapper = await createComponent(Breadcrumb, null, RouteNames.CONFIRM_AMENDMENT)
    await nextTick()

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbAmendment.length)

    tombstoneBreadcrumbAmendment[1].text = breadcrumbsTitles[userRoleProductCode]
    for (let i = 0; i < tombstoneBreadcrumbAmendment.length; i++) {
      expect(breadcrumbs.at(i).text()).toContain(wrapper.vm.handleStaff(tombstoneBreadcrumbAmendment[i].text))
    }
  })

  it('renders staff dashboard with breadcrumb', async () => {
    wrapper = await createComponent(Breadcrumb, null, RouteNames.DASHBOARD)
    await nextTick()

    const userRoleProductCode = getRoleProductCode(store.getUserRoles, [ProductCode.PPR])
    expect(wrapper.find(backBtn).exists()).toBe(true)

    const breadcrumbs = wrapper.findAll(getTestId('breadcrumb-item'))
    expect(breadcrumbs.length).toBe(tombstoneBreadcrumbDashboard.length)

    tombstoneBreadcrumbAmendment[1].text = breadcrumbsTitles[userRoleProductCode]
    expect(breadcrumbs.at(1).text()).toContain('Staff')
  })

  it('renders on Mhr Registration: staff', async () => {
    wrapper = await createComponent(Breadcrumb, null, RouteNames.YOUR_HOME)
    await nextTick()

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
    wrapper = await createComponent(Breadcrumb, null, RouteNames.YOUR_HOME)
    await nextTick()

    // Set up
    store.setAuthRoles(mockedManufacturerAuthRoles)
    store.setUserProductSubscriptionsCodes([ProductCode.MHR])
    await nextTick()

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
    store.setUserProductSubscriptionsCodes([])
  })

  it('renders on Mhr Registration: Manufacturer - MHR and PPR', async () => {
    wrapper = await createComponent(Breadcrumb, null, RouteNames.YOUR_HOME)
    await nextTick()

    // Set up
    store.setAuthRoles(mockedManufacturerAuthRoles)
    store.setUserProductSubscriptionsCodes([ProductCode.MHR, ProductCode.PPR])
    await nextTick()

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
    store.setUserProductSubscriptionsCodes([])
  })
})
