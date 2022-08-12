// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
// local components
import { BaseSnackbar } from '@/components/common'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (msg: string): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')

  return mount(BaseSnackbar, {
    localVue,
    propsData: {
      setMessage: msg,
      toggleSnackbar: false
    },
    store,
    vuetify
  })
}

describe('BaseSnackbar component tests', () => {
  let wrapper: any

  beforeEach(async () => {
    wrapper = createComponent('')
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders snackbar invisible before toggled', () => {
    expect(wrapper.find('.v-snack__wrapper').exists()).toBe(true)
    expect(wrapper.find('.v-snack__wrapper').isVisible()).toBe(false)
  })

  it('renders snackbar visible after toggled', async () => {
    // toggle show snackbar
    const msg = 'Registration was successfully added to your table.'
    await wrapper.setProps({ setMessage: msg, toggleSnackbar: true })
    expect(wrapper.find('.v-snack__wrapper').exists()).toBe(true)
    expect(wrapper.find('.v-snack__wrapper').isVisible()).toBe(true)
    expect(wrapper.find('.v-snack__wrapper').text()).toBe(msg)
    // close snackbar
    expect(wrapper.find('.snackbar-btn-close').exists()).toBe(true)
    await wrapper.find('.snackbar-btn-close').trigger('click')
    expect(wrapper.vm.$data.showSnackbar).toBe(false)
    expect(wrapper.find('.v-snack__wrapper').isVisible()).toBe(false)
    // verify toggle works again after the first time
    await wrapper.setProps({ toggleSnackbar: false })
    expect(wrapper.vm.$data.showSnackbar).toBe(true)
    expect(wrapper.find('.v-snack__wrapper').isVisible()).toBe(true)
    expect(wrapper.find('.v-snack__wrapper').text()).toBe(msg)
  })

  it('renders snackbar invisible 5 seconds after toggled', async () => {
    // toggle show snackbar
    await wrapper.setProps({ toggleSnackbar: true })
    // wait 5 seconds and check to see it is invisible
    setTimeout(async () => {
      expect(wrapper.find('.v-snack__wrapper').exists()).toBe(true)
      expect(wrapper.find('.v-snack__wrapper').isVisible()).toBe(true)
    }, 500)
  })
})
