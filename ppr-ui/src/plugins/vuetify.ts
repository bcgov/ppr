// Vuetify
import { createVuetify, IconComponent } from 'vuetify'

// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import 'vuetify/dist/vuetify.min.css'
import '@mdi/font/css/materialdesignicons.min.css' // ensure you are using css-loader
import '@/assets/styles/base.scss'
import '@/assets/styles/layout.scss'
import '@/assets/styles/overrides.scss'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

// Custom Svg Icons
import { ExecutorBusinessIcon, ExecutorPersonIcon, HomeLocationIcon, HomeOwnersIcon } from '@/assets/svgs'

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
      ExecutorBusinessIcon: {
        component: ExecutorBusinessIcon as IconComponent
      },
      ExecutorPersonIcon: {
        component: ExecutorPersonIcon as IconComponent
      },
      HomeLocationIcon: {
        component: HomeLocationIcon as IconComponent
      },
      HomeOwnersIcon: {
        component: HomeOwnersIcon as IconComponent
      }
    }
  },
  components,
  directives
})
