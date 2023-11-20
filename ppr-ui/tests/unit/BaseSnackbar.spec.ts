import { useStore } from '@/store/store'
import { createComponent } from './utils'
import { BaseSnackbar } from '@/components/common'
import { nextTick } from 'vue'
import { beforeEach, expect } from 'vitest'

const store = useStore()

// The v-snackbar component is not working with the testing library
// Will require a custom solution to test this component TBD
describe.skip('BaseSnackbar component tests', () => {
  let wrapper: any
  const msg = 'Registration was successfully added to your table.'

  beforeEach(async () => {
    wrapper = await createComponent(BaseSnackbar, { setMessage: msg, toggleSnackbar: true })
    await nextTick()
  })

  it('renders snackbar invisible before toggled', async () => {
    expect(wrapper.findComponent(BaseSnackbar).exists()).toBe(true)
    expect(wrapper.find('.v-snackbar__content').exists()).toBe(false)
  })

  it('renders snackbar visible after toggled', async () => {
    expect(wrapper.findComponent(BaseSnackbar).exists()).toBe(true)
    expect(wrapper.find('.v-snackbar__content').exists()).toBe(true)
    expect(wrapper.find('.v-snackbar__content').isVisible()).toBe(true)
    expect(wrapper.find('.v-snackbar__content').text()).toContain(msg)
    // close snackbar
    expect(wrapper.find('.snackbar-btn-close').exists()).toBe(true)
    await wrapper.find('.snackbar-btn-close').trigger('click')
    expect(wrapper.vm.showSnackbar).toBe(false)
    expect(wrapper.find('.v-snackbar__content').isVisible()).toBe(false)
  })

  it('renders snackbar invisible 5 seconds after toggled', async () => {
    // wait 5 seconds and check to see it is invisible
    setTimeout(async () => {
      expect(wrapper.find('.v-snackbar__content').exists()).toBe(true)
      expect(wrapper.find('.v-snackbar__content').isVisible()).toBe(true)
    }, 500)
  })
})
