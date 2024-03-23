// // setup.ts
import { afterEach, beforeAll, vi } from 'vitest'
import { config } from '@vue/test-utils'
import { dataTestId } from './unit/plugins'
import { createPinia, setActivePinia } from 'pinia'
import vuetify from '@/plugins/vuetify'
import * as matchers from 'vitest-axe/matchers'
import 'vitest-axe/extend-expect'
import { expect } from 'vitest'

// Extend vitest with axe matchers
expect.extend(matchers)

// Define Pinia/Vuetify/router globally
const pinia = createPinia()
setActivePinia(createPinia())

// Add properties to the wrapper
config.global.plugins.push([vuetify, pinia, dataTestId])

// Suppress Vue warnings
config.global.config.warnHandler = () => null
global.css = { supports: () => false }

beforeAll(() => {
  // Mock the entire vue-pdf-embed module
  vi.mock('vue-pdf-embed', () => {
    // Replace the component with a dummy component or return an empty object
    return {
      default: {
        render () {
          return null
        }
      }
    }
  })

  // Mock the WysiwygEditor component
  vi.mock('@/components/common/WysiwygEditor.vue', () => {
    // Replace the component with a dummy component or return an empty object
    return {
      default: {
        render () {
          return null
        }
      }
    }
  })

  // Stub the SbcHeader component
  vi.mock('../node_modules/sbc-common-components/src/components/SbcHeader.vue', () => {
    // Replace the component with a dummy component or return an empty object
    return {
      default: {
        render () {
          return null
        }
      }
    }
  })

  // Mock lodash library and override the 'debounce' method to immediately invoke the provided function without delays
  vi.mock('lodash', async () => {
    const actualLodash: any = await vi.importActual('lodash')
    return {
      ...actualLodash.default,
      debounce: vi.fn((fn) => fn)
    }
  })

  // Mock the WysiwygEditors (imported editor portion) component functions
  global.ClipboardEvent = class ClipboardEvent {
    constructor(type, eventInitDict) {
      // Implement the constructor as needed
    }
  }
  global.DragEvent = class ClipboardEvent {
    constructor() {}
  }

  // Mock & Stub the global ResizeObserver
  vi.stubGlobal('ResizeObserver', vi.fn(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn()
  })))
  // Mock & Stub the global IntersectionObserver
  vi.stubGlobal('IntersectionObserver', vi.fn(() => ({
    observe: vi.fn(),
    disconnect: vi.fn()
  })))

  // Mock Sentry
  vi.mock('@sentry/browser', () => ({
    captureException: vi.fn()
  }))

  // Extend JSDOM with canvas to facilitate AA testing
  Object.defineProperty(HTMLCanvasElement.prototype, 'getContext', {
    value: vi.fn(),
    writable: true
  })
})

afterEach(() => {
  // Restore the mocked functions
  vi.restoreAllMocks()
})


