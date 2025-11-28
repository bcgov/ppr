import { nextTick } from 'vue'
import type { AccountInformationIF, UserInfoIF } from '@/interfaces'
import { useStore } from '@/store/store'
import { AuthRoles, ProductCode, RouteNames } from '@/enums'
import { createComponent } from './utils'
import { Tombstone, TombstoneDefault, TombstoneDynamic } from '@/components/tombstones'
import { defaultFlagSet } from '@/utils/feature-flags'

const store = useStore()

// selectors
const tombstoneHeader: string = '.tombstone-header'
const tombstoneSubHeader: string = '.tombstone-sub-header'

/**
 * Check tombstone header content against different roles.
 *
 */
async function assertHeaderForRole (
  wrapper,
  roles: Array<string>,
  headerContent: string,
  subscribedProductsCodes: Array<ProductCode> = []
) {
  await store.setAuthRoles(roles)
  await store.setRoleSbc(!roles.includes(AuthRoles.PUBLIC))
  await store.setUserProductSubscriptionsCodes(subscribedProductsCodes)
  const header = wrapper.findAll(tombstoneHeader)
  await expect(header.length).toBe(1)
  await expect(header.at(0).text()).toContain(headerContent)
}

describe('TombstoneDefault component tests', () => {
  let wrapper
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
    // setup data used by header
    await store.setAccountInformation(accountInfo)
    await store.setUserInfo(userInfo)
    wrapper = await createComponent(TombstoneDefault, null, RouteNames.DASHBOARD)
    await nextTick()
  })

  it('renders default Tombstone component with header and user info displayed', async () => {
    await store.setAuthRoles([AuthRoles.PUBLIC, AuthRoles.PPR])
    await store.setUserProductSubscriptionsCodes([ProductCode.PPR])
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
    const staffGroups = ['helpdesk', 'ppr_staff']
    await store.setAuthRoles(['staff', 'ppr'])
    for (let i = 0; i < staffGroups.length; i++) {
      if (staffGroups[i] === 'gov_account_user') await store.setAuthRoles([staffGroups[i]])
      else await store.setAuthRoles(['staff', 'ppr', staffGroups[i]])
      const header = wrapper.findAll(tombstoneHeader)
      expect(header.length).toBe(1)
      expect(header.at(0).text()).toContain('Staff Asset Registries')
      const subHeader = wrapper.findAll(tombstoneSubHeader)
      expect(subHeader.length).toBe(1)
      if (staffGroups[i] === 'helpdesk') {
        expect(subHeader.at(0).text()).toContain('BC Online Help')
      }
      expect(subHeader.at(0).text()).toContain(userInfo.firstname)
      expect(subHeader.at(0).text()).toContain(userInfo.lastname)
    }
    await store.setRoleSbc(true)
    const subHeader = wrapper.findAll(tombstoneSubHeader)
    expect(subHeader.at(0).text()).toContain('SBC Staff')
  })

  it('displays different headers for different auth roles', async () => {
    const STAFF_PPR = [AuthRoles.STAFF, AuthRoles.PPR]
    const STAFF_MHR = [AuthRoles.STAFF, AuthRoles.MHR]
    const CLIENT_MHR = [AuthRoles.PUBLIC, AuthRoles.MHR]
    const CLIENT_PPR = [AuthRoles.PUBLIC, AuthRoles.PPR]
    const STAFF_PPR_MHR = [AuthRoles.STAFF, AuthRoles.PPR, AuthRoles.MHR]
    const CLIENT_PPR_MHR = [AuthRoles.PUBLIC, AuthRoles.PPR, AuthRoles.MHR]
    const HELP_DESK_PPR_MHR = [AuthRoles.PPR, AuthRoles.MHR, AuthRoles.HELPDESK]

    /* eslint-disable max-len */
    await assertHeaderForRole(wrapper, CLIENT_PPR, 'My Personal Property Registry', [ProductCode.PPR])
    await assertHeaderForRole(wrapper, CLIENT_PPR_MHR, 'My Asset Registries', [ProductCode.PPR, ProductCode.MHR])
    await assertHeaderForRole(wrapper, STAFF_PPR, 'Staff Asset Registries')

    await assertHeaderForRole(wrapper, STAFF_MHR, 'Staff Asset Registries')
    await assertHeaderForRole(wrapper, CLIENT_MHR, 'My Manufactured Home Registry', [ProductCode.MHR])
    await assertHeaderForRole(wrapper, STAFF_PPR_MHR, 'Staff Asset Registries')
    await assertHeaderForRole(wrapper, CLIENT_PPR_MHR, 'My Asset Registries', [ProductCode.PPR, ProductCode.MHR])
    await assertHeaderForRole(wrapper, CLIENT_PPR_MHR, 'My Personal Property Registry', [ProductCode.PPR])
    await assertHeaderForRole(wrapper, HELP_DESK_PPR_MHR, 'Staff Asset Registries')
  })
})
