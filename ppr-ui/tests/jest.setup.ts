// jest.setup.ts
// Global setup running before all tests
// Extend Jest with Accessibility unit test tool
import { toHaveNoViolations } from 'jest-axe'
expect.extend(toHaveNoViolations)

// Vue2 build
jest.mock('vue-pdf-embed/dist/vue2-pdf-embed', () => () => '<mock-vue-pdf-embed/>')

// Vue3 build: For post upgrade
// jest.mock('vue-pdf-embed', () => () => '<mock-vue-pdf-embed/>')
