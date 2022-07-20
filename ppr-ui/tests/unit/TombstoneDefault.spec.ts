// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { TombstoneDefault } from '@/components/tombstone'

// Other
import { AccountInformationIF, UserInfoIF } from '@/interfaces'
import mockRouter from './MockRouter'
import { AuthRoles, ProductCode, RouteNames } from '@/enums'
import { defaultFlagSet } from '@/utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// selectors
const tombstoneHeader: string = '.tombstone-header'
const tombstoneSubHeader: string = '.tombstone-sub-header'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchedResultPpr> object with the given parameters.
 */
function createComponent (mockRoute: string): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  localVue.use(VueRouter)
  const router = mockRouter.mock()
  router.push({ name: mockRoute })

  return mount(TombstoneDefault, {
    localVue,
    propsData: {},
    store,
    router,
    vuetify
  })
}

/**
 * Check tombstone header content against different roles.
 *
 */
async function assertHeaderForRole (
  wrapper: Wrapper<any>, roles: Array<string>, headerContent: string, subscribedProductsCodes: Array<ProductCode> = []
) {
  await store.dispatch('setAuthRoles', roles)
  await store.dispatch('setRoleSbc', !roles.includes(AuthRoles.PUBLIC))
  await store.dispatch('setUserProductSubscriptionsCodes', subscribedProductsCodes)
  const header = wrapper.findAll(tombstoneHeader)
  await expect(header.length).toBe(1)
  await expect(header.at(0).text()).toContain(headerContent)
}

describe('TombstoneDefault component tests', () => {
  let wrapper: any
  const { assign } = window.location
  const accountInfo: AccountInformationIF = {
    accountType: '',
    id: 1,
    label: 'testPPR',
    type: ''
  }
  const userInfo: UserInfoIF = {
    contacts: [
      {
        created: '',
        createdBy: '',
        email: '',
        modified: '',
        phone: '',
        phoneExtension: ''
      }
    ],
    feeSettings: {
      isNonBillable: false,
      serviceFee: 1.50
    },
    firstname: 'test',
    lastname: 'tester',
    username: '123d3crr3',
    settings: {
      defaultDropDowns: true,
      defaultTableFilters: true,
      paymentConfirmationDialog: true,
      selectConfirmationDialog: true
    }
  }

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any

    // setup data used by header
    await store.dispatch('setAccountInformation', accountInfo)
    await store.dispatch('setUserInfo', userInfo)
    defaultFlagSet['mhr-ui-enabled'] = false
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
  })

  it('renders default Tombstone component with header and user info displayed', async () => {
    wrapper = createComponent(RouteNames.DASHBOARD)
    await store.dispatch('setAuthRoles', [AuthRoles.PUBLIC, AuthRoles.PPR])
    await store.dispatch('setUserProductSubscriptionsCodes', [ProductCode.PPR])
    expect(wrapper.findComponent(TombstoneDefault).exists()).toBe(true)
    const header = wrapper.findAll(tombstoneHeader)
    expect(header.length).toBe(1)
    expect(header.at(0).text()).toContain('My Personal Property Registry')
    const subHeader = wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.length).toBe(1)
    expect(subHeader.at(0).text()).toContain(userInfo.firstname)
    expect(subHeader.at(0).text()).toContain(userInfo.lastname)
    expect(subHeader.at(0).text()).toContain(accountInfo.label)
  })

  it('displays staff versions', async () => {
    wrapper = createComponent(RouteNames.DASHBOARD)
    const staffGroups = ['helpdesk', 'ppr_staff']
    await store.dispatch('setAuthRoles', ['staff', 'ppr'])
    for (let i = 0; i < staffGroups.length; i++) {
      if (staffGroups[i] === 'gov_account_user') await store.dispatch('setAuthRoles', [staffGroups[i]])
      else await store.dispatch('setAuthRoles', ['staff', 'ppr', staffGroups[i]])
      const header = wrapper.findAll(tombstoneHeader)
      expect(header.length).toBe(1)
      expect(header.at(0).text()).toContain('Staff Personal Property Registry')
      const subHeader = wrapper.findAll(tombstoneSubHeader)
      expect(subHeader.length).toBe(1)
      if (staffGroups[i] === 'helpdesk') {
        expect(subHeader.at(0).text()).toContain('BC Online Help')
      }
      expect(subHeader.at(0).text()).toContain(userInfo.firstname)
      expect(subHeader.at(0).text()).toContain(userInfo.lastname)
    }
    await store.dispatch('setRoleSbc', true)
    const subHeader = wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.at(0).text()).toContain('SBC Staff')
  })

  it('displays different headers for different auth roles', async () => {
    wrapper = createComponent(RouteNames.DASHBOARD)

    const STAFF_PPR = [AuthRoles.STAFF, AuthRoles.PPR]
    const STAFF_MHR = [AuthRoles.STAFF, AuthRoles.MHR]
    const CLIENT_MHR = [AuthRoles.PUBLIC, AuthRoles.MHR]
    const CLIENT_PPR = [AuthRoles.PUBLIC, AuthRoles.PPR]
    const STAFF_PPR_MHR = [AuthRoles.STAFF, AuthRoles.PPR, AuthRoles.MHR]
    const CLIENT_PPR_MHR = [AuthRoles.PUBLIC, AuthRoles.PPR, AuthRoles.MHR]
    const HELP_DESK_PPR_MHR = [AuthRoles.PPR, AuthRoles.MHR, AuthRoles.HELPDESK]

    defaultFlagSet['mhr-ui-enabled'] = false
    await assertHeaderForRole(wrapper, CLIENT_PPR, 'My Personal Property Registry', [ProductCode.PPR])
    await assertHeaderForRole(wrapper, CLIENT_PPR_MHR, 'My Personal Property Registry', [ProductCode.PPR, ProductCode.MHR])
    await assertHeaderForRole(wrapper, STAFF_PPR, 'Staff Personal Property Registry')
    defaultFlagSet['mhr-ui-enabled'] = true
    await assertHeaderForRole(wrapper, STAFF_MHR, 'Staff Asset Registries')
    await assertHeaderForRole(wrapper, CLIENT_MHR, 'My Manufactured Home Registry', [ProductCode.MHR])
    await assertHeaderForRole(wrapper, STAFF_PPR_MHR, 'Staff Asset Registries')
    await assertHeaderForRole(wrapper, CLIENT_PPR_MHR, 'My Asset Registries', [ProductCode.PPR, ProductCode.MHR])
    await assertHeaderForRole(wrapper, CLIENT_PPR_MHR, 'My Personal Property Registry', [ProductCode.PPR])
    await assertHeaderForRole(wrapper, HELP_DESK_PPR_MHR, 'Staff Asset Registries')
  })
})
