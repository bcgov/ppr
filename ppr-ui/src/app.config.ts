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
        itemLeadingIcon: 'group-data-[state=checked]:text-blue-500 group-data-highlighted:text-blue-500 ' +
          'text-bcGovGray-900',
        placeholder: 'text-bcGovColor-midGray',
      }
    },
    table: {
      slots: {
        th: 'p-4',
        td: 'p-4 h-[65px]'
      }
    },
    fileUpload: {
      slots: {
        root: 'relative flex flex-col',
        base: [
          'w-full flex-1 bg-default border border-default flex flex-col gap-2 items-stretch justify-center rounded-lg' +
          ' focus-visible:outline-2 transition-[background]'
        ],
        wrapper: 'flex flex-col items-center justify-center text-center',
        icon: 'shrink-0',
        avatar: 'shrink-0',
        label: 'text-base text-default mt-2 text-bcGovGray-700 font-bold',
        description: 'text-bcGovGray-700 my-2 text-base',
        actions: 'flex flex-wrap gap-1.5 shrink-0 mt-4',
        file: 'relative bg-white gap-4 p-6! border-x-0! border-t-0! rounded-[0px]!',
        fileLeadingAvatar: 'shrink-0',
        fileWrapper: 'flex flex-col min-w-0',
        fileName: 'text-default truncate',
        fileSize: 'text-muted truncate',
        fileTrailingButton: ''
      }
    },
    textarea: {
      slots: {
        base: 'text-gray-900 border-0 border-b-[1px] border-gray-500 ring-0 focus:ring-0 h-[125px]',
        placeholder: 'placeholder-gray-700'
      }
    }
  }
})
