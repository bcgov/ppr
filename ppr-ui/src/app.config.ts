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
    select: {
      slots: {
        base: '',
        content: 'rounded-sm',
        group: 'px-0 py-2',
        trailingIcon: 'group-data-[state=open]:rotate-180 transition-transform duration-200 text-bcGovGray-midGray',
        item: 'my-0.75 text-bcGovGray-900 before:rounded-none data-[state=checked]:text-blue-500 cursor-pointer',
        itemLeadingIcon: 'group-data-[state=checked]:text-blue-500 group-data-highlighted:text-blue-500 text-bcGovGray-900',
        placeholder: 'text-bcGovColor-midGray',
      }
    },
  }
})
