// // setup.ts
import { afterEach, beforeAll, beforeEach, vi } from 'vitest'
import { config } from '@vue/test-utils'
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
config.global.plugins.push([vuetify, pinia])
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

  // Mock the ResizeObserver
  const ResizeObserverMock = vi.fn(() => ({
    observe: vi.fn(),
    unobserve: vi.fn(),
    disconnect: vi.fn()
  }))
  // Stub the global ResizeObserver
  vi.stubGlobal('ResizeObserver', ResizeObserverMock)

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


