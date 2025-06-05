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
    selectMenu: {
      input: 'cursor-pointer bg-white text-gray-700 h-10 -mt-2 border-b-[1.5px] border-b-primary',
      popper: { offsetDistance: '0', placement: 'bottom-start', locked: 'true' },
      base: 'cursor-pointer bg-white w-full overflow-x-hidden',
      option: {
        selected: 'cursor-pointer bg-white text-primary-500 bg-white pe-0',
        container: 'w-full',
        empty: 'text-gray-700'
      }
    },
  }
})
