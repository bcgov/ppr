// Setup file for Vitest tests
import { vi } from 'vitest'
import { config } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

// Setup Pinia
setActivePinia(createPinia())

// FeeWidget, no-props stub
config.global.stubs = {
  // Works for locally-registered or auto-imported components
  ConnectFeeWidget: {
    template: '<div data-testid="fee-widget-stub"></div>',
  }
}

// Mock useI18n globally
vi.stubGlobal('useI18n', () => ({
  t: (k: string) => k,      // echo key
  locale: { value: 'en' }   // minimal shape if you read locale
}))

vi.mock('@/utils/auth-helper', () => ({
  getRegisteringPartyFromAuth: vi.fn(() =>
    Promise.resolve({})),
  getStaffRegisteringParty: vi.fn(() =>
    Promise.resolve({})),
  getAccountInfoFromAuth: vi.fn(() =>Promise.resolve({
    name: 'Test Business',
    personName: {
      first: '',
      last: '',
      middle: ''
    },
    id: '12345',
    isBusinessAccount: false,
    mailingAddress: {
      street: '123 Main St',
      city: 'Test City',
      province: 'BC',
      postalCode: 'V1V 1V1',
      country: 'CA'
    },
    accountAdmin: {
      firstName: 'John',
      lastName: 'Doe',
      email: 'john@example.com',
      phone: '250-123-4567',
      phoneExtension: '123'
    }
  }))
}))

// keycloak-js: return a no-op client that always "initializes"
vi.mock('keycloak-js', () => ({
  default: vi.fn(() => ({
    init: vi.fn().mockResolvedValue(true),
    login: vi.fn(),
    logout: vi.fn(),
    updateToken: vi.fn().mockResolvedValue(true),
    isTokenExpired: vi.fn().mockReturnValue(false),
    token: 'test-token',
    authenticated: true,
  })),
}))

vi.mock('launchdarkly-js-client-sdk', () => ({
  initialize: vi.fn(() => ({
    on: vi.fn(),
    off: vi.fn(),
    variation: vi.fn().mockReturnValue(false),
    identify: vi.fn(),
    close: vi.fn(),
  })),
}))

// stub an EventTarget (VisualViewport extends EventTarget)
const vv = new EventTarget() as EventTarget & {
  width?: number; height?: number; scale?: number;
  offsetLeft?: number; offsetTop?: number; pageLeft?: number; pageTop?: number;
}
vv.width = 1024
vv.height = 768
vv.scale = 1

vi.stubGlobal('visualViewport', vv)

// ESM-friendly mock preserving other exports
vi.mock('h3', async (importOriginal) => {
  const mod = await importOriginal<any>()
  return {
    ...mod,
    createError: (input: any) => {
      const message =
        (input?.message ?? input?.statusMessage ?? 'Test: normalized error')
      const statusCode = input?.statusCode ?? 500
      // Return a minimal error-like object without throwing
      return { statusCode, message, cause: input }
    }
  }
})





