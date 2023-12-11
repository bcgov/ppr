import { vi, describe, it, expect, beforeEach } from 'vitest'
import { useStore } from '@/store/store'
import { createComponent } from './utils'
import App from '@/App.vue'
import SbcHeader from 'sbc-common-components/src/components/SbcHeader.vue'
import SbcFooter from 'sbc-common-components/src/components/SbcFooter.vue'
import { Tombstone } from '@/components/tombstone'
import { Breadcrumb } from '@/components/common'
import {
  mockedDisableAllUserSettingsResponse,
  mockedFinancingStatementAll,
  mockedProductSubscriptions
} from './test-data'
import { FeeCodes } from '@/composables/fees/enums'
import { AccountProductCodes, AccountProductMemberships } from '@/enums'
import { StatusCodes } from 'http-status-codes'
import { axe } from 'vitest-axe'
import { nextTick } from 'vue'

const store = useStore()

// Axios mocks
// Mock the axios-auth instance created in utility file
vi.mock('@/utils/axios-auth', () => {
  const mockAxiosInstance = {
    get: vi.fn((url) => {
      switch (url) {
        case 'orgs/test_id/products':
          return Promise.resolve({ data: mockedProductSubscriptions.ALL })
        case 'users/@me':
          return Promise.resolve({
            data: {
              contacts: [],
              firstname: 'first',
              lastname: 'last',
              username: 'username'
            },
            status: StatusCodes.OK
          })
        case `accounts/test_id/products/${AccountProductCodes.RPPR}/authorizations`:
          return Promise.resolve({
            data: {
              membership: AccountProductMemberships.MEMBER,
              roles: ['search']
            }
          })
      }
    })
  }

  return { axios: mockAxiosInstance }
})

// Mock the axios-ppr instance created in utility file
vi.mock('@/utils/axios-ppr', () => {
  const mockAxiosInstance = {
    get: vi.fn((url) => {
      if (url === 'user-profile') {
        return Promise.resolve({ data: mockedDisableAllUserSettingsResponse, status: StatusCodes.OK })
      }
    })
  }

  return { axios: mockAxiosInstance }
})

// Mock the axios-pay instance created in utility file
vi.mock('@/utils/axios-pay', () => {
  const mockAxiosInstance = {
    get: vi.fn((url) => {
      if (url === `fees/PPR/${FeeCodes.SEARCH}`) {
        return Promise.resolve({ data: { filingFees: 0, serviceFees: 1 }, status: StatusCodes.OK })
      }
    })
  }

  return { axios: mockAxiosInstance }
})

describe('App component basic rendering normal account', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(App, {
      appReady: true
    })

    // Mock present token service to prevent running in test env
    wrapper.vm.tokenService = true

    // Wait for the component and subcomponents to render
    await new Promise((resolve) => {
      setTimeout(() => {
        resolve()
      }, 1000)
    })
  })

  it('should have no accessibility violations', async () => {
    // Run the axe-core accessibility check on the component's HTML
    const results = await axe(wrapper.html())
    // Use the custom vitest-axe matcher to check for violations
    expect(results).toHaveNoViolations()
  })

  it('renders the sub-components properly', async () => {
    expect(wrapper.findComponent(App).exists()).toBe(true)
    expect(wrapper.findComponent(SbcHeader).exists()).toBe(true)
    expect(wrapper.findComponent(SbcFooter).exists()).toBe(true)
    expect(wrapper.findComponent(Tombstone).exists()).toBe(false)
    expect(wrapper.findComponent(Breadcrumb).exists()).toBe(false)
  })

  it('gets auth and user info/settings properly', async () => {
    expect(store.getStateModel.authorization.authRoles).toContain('ppr')
    expect(store.getStateModel.userInfo).not.toBeNull()
    expect(store.getStateModel.userInfo.firstname).toBe('first')
    expect(store.getStateModel.userInfo.lastname).toBe('last')
    expect(store.getStateModel.userInfo.username).toBe('username')
    expect(store.getStateModel.userInfo.settings.paymentConfirmationDialog).toBe(false)
    expect(store.getStateModel.userInfo.settings.selectConfirmationDialog).toBe(false)
  })

  it('fee settings are set to expected values', async () => {
    expect(store.getStateModel.userInfo.feeSettings.isNonBillable).toBe(true)
    expect(store.getStateModel.userInfo.feeSettings.serviceFee).toBe(1)
  })
})

