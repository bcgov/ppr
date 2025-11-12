
// tests/setup/i18n.ts
import { config } from '@vue/test-utils'
import { createI18n } from 'vue-i18n'

const messages = {
  en: {
    ConnectFeeWidget: {
      feeSummary: {
        title: 'Fees summary',
        total: 'Total'
      }
    },
    currency: { cad: 'CAD' } // if your template does t('currency.cad')
  }
}

const i18n = createI18n({
  legacy: false,            // Composition API mode for useI18n()
  locale: 'en',
  fallbackLocale: 'en',
  messages,
  // Optional: mute noisy dev warnings in tests (see A2)
  // missingWarn: false,
  // fallbackWarn: false
})


config.global.plugins = config.global.plugins || []
config.global.plugins.push(i18n)
