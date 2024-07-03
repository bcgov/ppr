/**
 * Plugin to modify the VTextField component to add a 'tab-focused' css class when the input
 * is focused via the Tab key. This allows to style the v-text-field's input differently
 * when it's focused with the keyboard, compared to when it's clicked with the mouse.
 *
 * The event listeners are cleaned up when the component is unmounted.
 */
export default {
  install(app) {
    const TAB_KEY = 'Tab'

    // Access the VTextField component if it's globally registered
    const VTextField = app.component('VTextField')

    if (!VTextField) return

    // Store the original mount function
    const originalMount = VTextField.mounted

    // Modify the mounted lifecycle hook
    VTextField.mounted = function () {
      // Call any existing mounted functions
      if (originalMount) originalMount.call(this)

      const input = this.$el.querySelector('input')
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
    VTextField.unmounted = function () {
      const input = this.$el.querySelector('input')
      if (input && input.cleanupEventListeners) {
        input.cleanupEventListeners()
      }
    }
  }
}
