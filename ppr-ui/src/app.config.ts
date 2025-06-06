import pkg from '../package.json'

const connectLayerName = pkg.connectLayerName
const connnectLayerVersion = pkg.dependencies['@sbc-connect/nuxt-core-layer-beta']

export default defineAppConfig({
  connect: {
    core: {
      header: {
        options: {
          localeSelect: false
        }
      },
      footer: {
        versions: [
          (connectLayerName && connnectLayerVersion) ? `${connectLayerName} v${connnectLayerVersion}` : ''
        ]
      },
    },
    feeWidget: {
      itemLabelTooltip: {
        test: {
          i18nkey: '',
          hrefRtcKey: ''
        }
      }
    },
  },
  ui: {
    icons: {}
  }
})
