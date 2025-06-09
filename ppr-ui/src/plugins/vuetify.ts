import { defineNuxtPlugin } from '#app'
import { h } from 'vue'
import { createVuetify } from 'vuetify'
import type { IconSet, IconProps } from 'vuetify'
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.min.css'
import '@/assets/styles/base.scss'
import '@/assets/styles/layout.scss'
import '@/assets/styles/overrides.scss'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { ExecutorBusinessIcon, ExecutorPersonIcon, HomeLocationIcon, HomeOwnersIcon } from '@/assets/svgs'

const customSvgNameToComponent: any = {
  ExecutorBusinessIcon, ExecutorPersonIcon, HomeLocationIcon, HomeOwnersIcon
}

const custom: IconSet = {
  component: (props: IconProps) =>
    h(props.tag, [h(customSvgNameToComponent[props.icon as string], { class: 'v-icon__svg' })])
}

const vuetify = createVuetify({
  theme: {
    defaultTheme: 'bcgov',
    themes: {
      bcgov: {
        colors: {
          primary: '#1669bb',
          darkBlue: '#38598a',
          lightBlue: '#E2E8EE',
          error: '#d3272c',
          success: '#1a9031',
          darkGray: '#495057',
          caution: '#F8661A',
          greyLighten: '#e0e0e01f'
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

export default defineNuxtPlugin(nuxtApp => {
  nuxtApp.vueApp.use(vuetify)
})
