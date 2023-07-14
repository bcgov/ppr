// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { HomeCertification } from '@/components/mhrRegistration'
import { SharedDatePicker } from '@/components/common'
import flushPromises from 'flush-promises'
import { MhrRegistrationType } from '@/resources'
import { mockedManufacturerAuthRoles } from './test-data'
import { HomeCertificationOptions, AuthRoles } from '@/enums'
import { getTestId } from './utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchBar> object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()

  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount((HomeCertification as any), {
    localVue,
    propsData: {},
    store,
    vuetify
  })
}

describe('Home Certification - staff', () => {
  let wrapper: Wrapper<any>

  beforeAll(async () => {
    await store.setAuthRoles([AuthRoles.PPR_STAFF, AuthRoles.STAFF, AuthRoles.MHR, AuthRoles.PPR])
  })

  beforeEach(async () => {
    wrapper = createComponent()
    await store.setMhrHomeDescription({ key: 'certificationOption', value: null })
    await store.setMhrHomeDescription({ key: 'noCertification', value: null })
    wrapper.vm.certificationOption = null
    wrapper.vm.hasNoCertification = false
    await nextTick()
    await flushPromises()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  afterAll(async () => {
    await store.setAuthRoles([])
  })

  it('renders base component with default sub components', async () => {
    expect(wrapper.findComponent(HomeCertification).exists()).toBe(true)
    expect(wrapper.findComponent(SharedDatePicker).exists()).toBe(false)
  })

  it('renders with default values', async () => {
    /// Verify Radio grp
    expect(wrapper.find('#certification-option-btns').exists()).toBe(true)

    // Verify Forms hidden before radio btn selection
    expect(wrapper.find('#csa-form').isVisible()).toBe(false)
    expect(wrapper.find('#engineer-form').isVisible()).toBe(false)
    expect(wrapper.find('#no-certification-checkbox').isVisible()).toBe(true)
    expect(wrapper.find(getTestId('no-certification-tooltip')).exists()).toBe(true)
  })

  it('opens the CSA Form when selected', async () => {
    // Verify Forms hidden before radio btn selection
    expect(wrapper.find('#csa-form').isVisible()).toBe(false)
    expect(wrapper.find('#engineer-form').isVisible()).toBe(false)

    // Click the btn
    await wrapper.find('#csa-option').trigger('click')

    // Verify CSA Form
    expect(wrapper.find('#csa-form').isVisible()).toBe(true)
    expect(wrapper.find('#csa-number').isVisible()).toBe(true)
    expect(wrapper.find('#csa-standard').isVisible()).toBe(true)

    // Verify Engineer Form
    expect(wrapper.find('#engineer-form').isVisible()).toBe(false)
    expect(wrapper.find('#engineer-name').isVisible()).toBe(false)
    expect(wrapper.find('#date-of-engineer-report').exists()).toBe(false)
  })

  it('opens the Engineer Form when selected', async () => {
    // Verify Forms hidden before radio btn selection
    expect(wrapper.find('#csa-form').isVisible()).toBe(false)
    expect(wrapper.find('#engineer-form').isVisible()).toBe(false)

    // Click the btn
    await wrapper.find('#engineer-option').trigger('click')

    // Verify Engineer Form
    expect(wrapper.find('#engineer-form').isVisible()).toBe(true)
    expect(wrapper.find('#engineer-name').isVisible()).toBe(true)
    expect(wrapper.find('#date-of-engineer-report').isVisible()).toBe(true)

    // Verify CSA Form
    expect(wrapper.find('#csa-form').isVisible()).toBe(false)
    expect(wrapper.find('#csa-number').isVisible()).toBe(false)
    expect(wrapper.find('#csa-standard').isVisible()).toBe(false)
  })

  it('toggles between form options', async () => {
    // Verify Forms hidden before radio btn selection
    expect(wrapper.find('#csa-form').isVisible()).toBe(false)
    expect(wrapper.find('#engineer-form').isVisible()).toBe(false)

    // Click the btn
    await wrapper.find('#engineer-option').trigger('click')

    // Verify Engineer Form
    expect(wrapper.find('#engineer-form').isVisible()).toBe(true)
    expect(wrapper.find('#engineer-name').isVisible()).toBe(true)
    expect(wrapper.find('#date-of-engineer-report').isVisible()).toBe(true)

    // Verify CSA Form
    expect(wrapper.find('#csa-form').isVisible()).toBe(false)
    expect(wrapper.find('#csa-number').isVisible()).toBe(false)
    expect(wrapper.find('#csa-standard').isVisible()).toBe(false)

    // Verify Form Toggle

    // Click the btn
    await wrapper.find('#csa-option').trigger('click')

    // Verify CSA Form
    expect(wrapper.find('#csa-form').isVisible()).toBe(true)
    expect(wrapper.find('#csa-number').isVisible()).toBe(true)
    expect(wrapper.find('#csa-standard').isVisible()).toBe(true)

    // Verify Engineer Form
    expect(wrapper.find('#engineer-form').isVisible()).toBe(false)
    expect(wrapper.find('#engineer-name').isVisible()).toBe(false)
    expect(wrapper.find('#date-of-engineer-report').exists()).toBe(false)
  })

  it('renders the DatePicker for the engineer option', async () => {
    // Click the btn
    await wrapper.find('#engineer-option').trigger('click')
    expect(wrapper.findComponent(SharedDatePicker).exists()).toBe(true)
  })

  it('collapses form if no certification checkbox is selected', async () => {
    await wrapper.find('#csa-option').trigger('click')
    expect(wrapper.find('#csa-form').isVisible()).toBe(true)

    await wrapper.find('#no-certification-checkbox').trigger('click')
    expect(wrapper.find('#csa-form').isVisible()).toBe(false)
  })

  it('disables buttons if no certification checkbox is selected', async () => {
    await wrapper.find('#no-certification-checkbox').trigger('click')

    expect(wrapper.find('#csa-option').attributes('disabled')).toBe('disabled')
    expect(wrapper.find('#engineer-option').attributes('disabled')).toBe('disabled')

    // Enables button after unselected
    await wrapper.find('#no-certification-checkbox').trigger('click')
    expect(wrapper.find('#csa-option').attributes('disabled')).toBe(undefined)
    expect(wrapper.find('#engineer-option').attributes('disabled')).toBe(undefined)
  })

  it('sets the home certification section to valid if no certification checkbox is selected', async () => {
    expect(store.getMhrRegistrationValidationModel.yourHomeValid.homeCertificationValid).toBe(false)
    await wrapper.find('#no-certification-checkbox').trigger('click')
    expect(store.getMhrRegistrationValidationModel.yourHomeValid.homeCertificationValid).toBe(true)
  })
})

describe('Home Certification - manufacturer', () => {
  let wrapper: Wrapper<any>

  beforeAll(async () => {
    await store.setAuthRoles(mockedManufacturerAuthRoles)
    await store.setRegistrationType(MhrRegistrationType)
    // When a manufacturer registration is inited it sets the certificatonOption to CSA
    await store.setMhrHomeDescription({ key: 'certificationOption', value: HomeCertificationOptions.CSA })
  })

  beforeEach(async () => {
    wrapper = createComponent()
    await nextTick()
    await flushPromises()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  afterAll(async () => {
    await store.setAuthRoles(null)
    await store.setRegistrationType(null)
  })

  it('renders base component with correct sub components', async () => {
    expect(wrapper.findComponent(HomeCertification).exists()).toBe(true)
    expect(wrapper.findComponent(SharedDatePicker).exists()).toBe(false)

    /// Verify Radio group does not exist
    expect(wrapper.find('#certification-option-btns').exists()).toBe(false)

    // Verify only csa-form is shown
    expect(wrapper.find('#csa-form').isVisible()).toBe(true)
    expect(wrapper.find('#engineer-form').exists()).toBe(false)
    expect(wrapper.find('#no-certification').exists()).toBe(false)
    expect(wrapper.find(getTestId('no-certification-tooltip')).exists()).toBe(false)
  })
})
