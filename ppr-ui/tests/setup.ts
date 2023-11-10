// // setup.ts
import { afterEach, vi } from 'vitest'
import { config } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import vuetify from '@/plugins/vuetify'
import 'vitest-axe/extend-expect'

// Define Pinia/Vuetify globally
const pinia = createPinia()
setActivePinia(createPinia())

// Add properties to the wrapper
config.global.plugins.push([vuetify, pinia])
global.css = { supports: () => false }

// Mocks
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

// Mock the ResizeObserver
const ResizeObserverMock = vi.fn(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn()
}))
// Stub the global ResizeObserver
vi.stubGlobal('ResizeObserver', ResizeObserverMock)

afterEach(() => {
  // Clear all mocks after each test.
  vi.clearAllMocks()
})


