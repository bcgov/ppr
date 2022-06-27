// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { HomeCertification } from '@/components/mhrRegistration'
import { SharedDatePicker } from '@/components/common'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(HomeCertification, {
    localVue,
    propsData: {},
    store,
    vuetify
  })
}

describe('Home Certification', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders base component with default sub components', async () => {
    expect(wrapper.findComponent(HomeCertification).exists()).toBe(true)
    expect(wrapper.findComponent(SharedDatePicker).exists()).toBe(false)
  })

  it('renders with default values', async () => {
    /// Verify Radio grp
    expect(wrapper.find('#certification-option-btns').exists()).toBe(true)

    // Verify Forms hidden before radio btn selection
    expect(wrapper.find('#csa-form').exists()).toBe(false)
    expect(wrapper.find('#engineer-form').exists()).toBe(false)
  })

  it('opens the CSA Form when selected', async () => {
    // Verify Forms hidden before radio btn selection
    expect(wrapper.find('#csa-form').exists()).toBe(false)
    expect(wrapper.find('#engineer-form').exists()).toBe(false)

    // Click the btn
    await wrapper.find('#csa-option').trigger('click')

    // Verify CSA Form
    expect(wrapper.find('#csa-form').exists()).toBe(true)
    expect(wrapper.find('#csa-number').exists()).toBe(true)
    expect(wrapper.find('#csa-standard').exists()).toBe(true)

    // Verify Engineer Form
    expect(wrapper.find('#engineer-form').exists()).toBe(false)
    expect(wrapper.find('#engineer-name').exists()).toBe(false)
    expect(wrapper.find('#date-of-engineer-report').exists()).toBe(false)
  })

  it('opens the Engineer Form when selected', async () => {
    // Verify Forms hidden before radio btn selection
    expect(wrapper.find('#csa-form').exists()).toBe(false)
    expect(wrapper.find('#engineer-form').exists()).toBe(false)

    // Click the btn
    await wrapper.find('#engineer-option').trigger('click')

    // Verify Engineer Form
    expect(wrapper.find('#engineer-form').exists()).toBe(true)
    expect(wrapper.find('#engineer-name').exists()).toBe(true)
    expect(wrapper.find('#date-of-engineer-report').exists()).toBe(true)

    // Verify CSA Form
    expect(wrapper.find('#csa-form').exists()).toBe(false)
    expect(wrapper.find('#csa-number').exists()).toBe(false)
    expect(wrapper.find('#csa-standard').exists()).toBe(false)
  })

  it('toggles between form options', async () => {
    // Verify Forms hidden before radio btn selection
    expect(wrapper.find('#csa-form').exists()).toBe(false)
    expect(wrapper.find('#engineer-form').exists()).toBe(false)

    // Click the btn
    await wrapper.find('#engineer-option').trigger('click')

    // Verify Engineer Form
    expect(wrapper.find('#engineer-form').exists()).toBe(true)
    expect(wrapper.find('#engineer-name').exists()).toBe(true)
    expect(wrapper.find('#date-of-engineer-report').exists()).toBe(true)

    // Verify CSA Form
    expect(wrapper.find('#csa-form').exists()).toBe(false)
    expect(wrapper.find('#csa-number').exists()).toBe(false)
    expect(wrapper.find('#csa-standard').exists()).toBe(false)

    // Verify Form Toggle

    // Click the btn
    await wrapper.find('#csa-option').trigger('click')

    // Verify CSA Form
    expect(wrapper.find('#csa-form').exists()).toBe(true)
    expect(wrapper.find('#csa-number').exists()).toBe(true)
    expect(wrapper.find('#csa-standard').exists()).toBe(true)

    // Verify Engineer Form
    expect(wrapper.find('#engineer-form').exists()).toBe(false)
    expect(wrapper.find('#engineer-name').exists()).toBe(false)
    expect(wrapper.find('#date-of-engineer-report').exists()).toBe(false)
  })

  it('renders the DatePicker for the engineer option', async () => {
    // Click the btn
    await wrapper.find('#engineer-option').trigger('click')
    expect(wrapper.findComponent(SharedDatePicker).exists()).toBe(true)
  })
})
