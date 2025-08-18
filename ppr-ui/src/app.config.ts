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
      },
      variants: {
        size: {
          bcGov: {
            base: 'px-0 py-0 text-base gap-1.5',
            leading: 'ps-2.5',
            trailing: 'pe-2.5',
            leadingIcon: 'size-5',
            leadingAvatarSize: '2xs',
            trailingIcon: 'size-5',
            label: 'p-1.5 text-xs gap-1.5',
            item: 'py-1.5 px-4 text-sm gap-3',
            itemLeadingIcon: 'size-5',
            itemLeadingAvatarSize: '2xs',
            itemLeadingChip: 'size-5',
            itemLeadingChipSize: 'md',
            itemTrailingIcon: 'size-5'
          }
        },
        variant: {
          bcGov: 'peer rounded-t-sm rounded-b-none bg-bcGovGray-100 focus:ring-0 focus:outline-none data-[state=open]:shadow-bcGovInput focus:shadow-bcGovInput text-bcGovGray-900'
        }
      },
      defaultVariants: {
        size: 'bcGov',
        color: 'primary',
        variant: 'bcGov'
      }
    },
  }
})
