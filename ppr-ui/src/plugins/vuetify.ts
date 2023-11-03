// Vuetify
import { h } from 'vue'
import { createVuetify } from 'vuetify'
import type { IconSet, IconProps } from 'vuetify'

// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/dist/vuetify.min.css'
import '@mdi/font/css/materialdesignicons.min.css' // ensure you are using css-loader
import '@/assets/styles/base.scss'
import '@/assets/styles/layout.scss'
import '@/assets/styles/overrides.scss'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

// Custom Svg Icons
import { ExecutorBusinessIcon, ExecutorPersonIcon, HomeLocationIcon, HomeOwnersIcon } from '@/assets/svgs'

const customSvgNameToComponent: any = {
  ExecutorBusinessIcon, ExecutorPersonIcon, HomeLocationIcon, HomeOwnersIcon
}

const custom: IconSet = {
  component: (props: IconProps) =>
    h(props.tag, [h(customSvgNameToComponent[props.icon as string], { class: 'v-icon__svg' })]),
}

export default createVuetify({
  theme: {
    defaultTheme: 'bcgov',
    themes: {
      bcgov: {
        colors: {
          primary: '#1669bb', // same as $$primary-blue
          darkBlue: '#38598a',
          lightBlue: '#E2E8EE', // same as $app-lt-blue
          error: '#d3272c',
          success: '#1a9031',
          darkGray: '#495057', // same as theme $gray7
          caution: '#F8661A' // same as them $app-orange
        }
      }
    }
  },
  icons: {
    defaultSet: 'mdi',
    sets: {
      custom: custom
    }
  },
  components,
  directives
})
