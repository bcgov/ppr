import { fileURLToPath } from 'node:url'
import { defineVitestConfig } from '@nuxt/test-utils/config'

export default defineVitestConfig({
  test: {
    dir: 'tests',
    environment: 'nuxt',
    environmentOptions: {
      nuxt: {
        rootDir: fileURLToPath(new URL('./', import.meta.url)),
        domEnvironment:
          (process.env.VITEST_DOM_ENV as 'happy-dom' | 'jsdom') ?? 'happy-dom',

        overrides: {
          modules: ['@nuxtjs/i18n'],
          i18n: {
            // minimal i18n test config
            locales: [{ code: 'en', file: 'en.json' }],
            defaultLocale: 'en',
            vueI18n: { legacy: false, locale: 'en', messages: { en: {} } }
          }
        }

      }
    },
    setupFiles: ['../tests/i18n.ts', '../tests/setup.ts'],
    globals: true,
    silent: true,
    testTimeout: 30_000, // 30s for each test
    hookTimeout: 30_000, // 30s for beforeAll/afterAll/etc
    css: {
      preprocessorOptions: {
        scss: {
          api: 'modern-compiler', // or 'modern'
        },
      },
    },
  }
})
