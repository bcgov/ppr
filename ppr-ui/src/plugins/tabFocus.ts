// assets-ui/src/plugins/tabFocus.ts
import { defineNuxtPlugin } from '#app'

export const tabFocus = {
  install(app) {
    const TAB_KEY = 'Tab'

    const addTabFocusToComponent = (component: any) => {
      if (!component) return

      // Store the original mount function
      const originalMount = component.mounted

      // Modify the mounted lifecycle hook
      component.mounted = function () {
        // Call any existing mounted functions
        if (originalMount) originalMount.call(this)

        const input = this.$el.querySelector('input, textarea')
        if (!input) return

        const handleKeyDown = event => {
          if (event.key === TAB_KEY) {
            input.lastKeyPressed = TAB_KEY
          }
        }

        const handleFocus = () => {
          if (input.lastKeyPressed === TAB_KEY) {
            this.$el.classList.add('tab-focused')
          }
          input.lastKeyPressed = '' // Reset after check
        }

        const handleBlur = () => {
          this.$el.classList.remove('tab-focused')
        }

        window.addEventListener('keydown', handleKeyDown)
        input.addEventListener('focus', handleFocus)
        input.addEventListener('blur', handleBlur)

        input.cleanupEventListeners = () => {
          window.removeEventListener('keydown', handleKeyDown)
          input.removeEventListener('focus', handleFocus)
          input.removeEventListener('blur', handleBlur)
        }
      }

      // Modify the unmounted lifecycle hook to remove all event listeners
      component.unmounted = function () {
        const input = this.$el.querySelector('input, textarea')
        if (input && input.cleanupEventListeners) {
          input.cleanupEventListeners()
        }
      }
    }

    // Access the VTextField component and add tab focus events
    const VTextField = app.component('VTextField')
    addTabFocusToComponent(VTextField)

    // Access the VTextarea component and add tab focus events
    const VTextarea = app.component('VTextarea')
    addTabFocusToComponent(VTextarea)
  }
}

export default defineNuxtPlugin(nuxtApp => {
  nuxtApp.vueApp.use(tabFocus)
})
