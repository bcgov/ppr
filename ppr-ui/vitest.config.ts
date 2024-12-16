import { fileURLToPath } from 'node:url'
import { defineVitestConfig } from '@nuxt/test-utils/config'

export default defineVitestConfig({
  test: {
    server: {
      deps: {
        inline: ['vuetify', 'vue-pdf-embed']
      }
    },
    globals: true,
    threads: true,
    testTimeout: 60000,
    setupFiles: '../tests/setup.ts',
    onConsoleLog (log) {
      if (log.includes('Vue warn')) return false // Filter out Vue warnings while preserving errors and logs.
      if (log.includes('AggregateError')) return false // Filter out failed network requests vs mocking them all.
    },
    dir: 'tests',
    environment: 'jsdom',
    environmentOptions: {
      nuxt: {
        rootDir: fileURLToPath(new URL('./', import.meta.url)),
        domEnvironment:
          (process.env.VITEST_DOM_ENV as 'happy-dom' | 'jsdom') ?? 'happy-dom'
      }
    }
  }
})
