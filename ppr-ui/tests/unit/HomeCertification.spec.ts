// Libraries
import { nextTick } from 'vue'
import { useStore } from '@/store/store'

// Components
import { HomeCertification } from '@/components/mhrRegistration'
import flushPromises from 'flush-promises'
import { MhrRegistrationType } from '@/resources'
import { mockedManufacturerAuthRoles } from './test-data'
import { HomeCertificationOptions, AuthRoles, ProductCode } from '@/enums'
import { createComponent, getTestId } from './utils'
import { InputFieldDatePicker } from '@/components/common'

const store = useStore()

describe('Home Certification - staff', () => {
  let wrapper

  beforeAll(async () => {
    await store.setAuthRoles([AuthRoles.PPR_STAFF, AuthRoles.STAFF, AuthRoles.MHR, AuthRoles.PPR])
  })

  beforeEach(async () => {
    wrapper = await createComponent(HomeCertification, { appReady: true })
    await store.setMhrHomeDescription({ key: 'certificationOption', value: null })
    await store.setMhrHomeDescription({ key: 'hasNoCertification', value: null })
    wrapper.vm.certificationOption = null
    wrapper.vm.hasNoCertification = false
    await nextTick()
    await flushPromises()
  })

  afterAll(async () => {
    await store.setAuthRoles([])
  })

  it('renders base component with default sub components', async () => {
    expect(wrapper.findComponent(HomeCertification).exists()).toBe(true)
    expect(wrapper.findComponent(InputFieldDatePicker).exists()).toBe(false)
  })

  it('renders with default values', async () => {
    /// Verify Radio grp
    expect(wrapper.find(getTestId('certification-option-btns')).exists()).toBe(true)

    // Verify Forms hidden before radio btn selection
    expect(wrapper.find('#csa-form').exists()).toBe(false)
    expect(wrapper.find('#engineer-form').exists()).toBe(false)
    expect(wrapper.find('#no-certification-checkbox').exists()).toBe(true)
    expect(wrapper.find(getTestId('no-certification-tooltip')).exists()).toBe(true)
  })

  it('opens the CSA Form when selected', async () => {
    // Verify Forms hidden before radio btn selection
    expect(wrapper.find('#csa-form').exists()).toBe(false)
    expect(wrapper.find('#engineer-form').exists()).toBe(false)

    // Click the btn
    await wrapper.find('#csa-option').setValue(true)

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
    await wrapper.find('#engineer-option').setValue(true)

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
    await wrapper.find('#engineer-option').setValue(true)

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
    await wrapper.find('#csa-option').setValue(true)

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
    await wrapper.find('#engineer-option').setValue(true)
    expect(wrapper.findComponent(InputFieldDatePicker).exists()).toBe(true)
  })

  it('collapses form if no certification checkbox is selected', async () => {
    await wrapper.find('#csa-option').setValue(true)
    expect(wrapper.find('#csa-form').exists()).toBe(true)

    await wrapper.find('#no-certification-checkbox').setValue(true)
    expect(wrapper.find('#csa-form').exists()).toBe(false)
  })

  it('disables buttons if no certification checkbox is selected', async () => {
    await wrapper.find('#no-certification-checkbox').setValue(false)

    expect(wrapper.find('#csa-option').getCurrentComponent().props.disabled).toBe(false)
    expect(wrapper.find('#engineer-option').getCurrentComponent().props.disabled).toBe(false)

    // Enables button after unselected
    await wrapper.find('#no-certification-checkbox').setValue(true)
    expect(wrapper.find('#csa-option').getCurrentComponent().props.disabled).toBe(true)
    expect(wrapper.find('#engineer-option').getCurrentComponent().props.disabled).toBe(true)
  })

  it('sets the home certification section to valid if no certification checkbox is selected', async () => {
    expect(store.getMhrRegistrationValidationModel.yourHomeValid.homeCertificationValid).toBe(false)
    await wrapper.find('#no-certification-checkbox').setValue(true)
    expect(store.getMhrRegistrationValidationModel.yourHomeValid.homeCertificationValid).toBe(true)
  })
})

describe('Home Certification - manufacturer', () => {
  let wrapper

  beforeAll(async () => {
    await store.setAuthRoles(mockedManufacturerAuthRoles)
    await store.setRegistrationType(MhrRegistrationType)
    // When a manufacturer registration is inited it sets the certificatonOption to CSA
    await store.setMhrHomeDescription({ key: 'certificationOption', value: HomeCertificationOptions.CSA })
    await store.setUserProductSubscriptionsCodes([ProductCode.MHR, ProductCode.MANUFACTURER])
  })

  beforeEach(async () => {
    wrapper = await createComponent(HomeCertification, { appReady: true })
    await nextTick()
    await flushPromises()
  })

  afterAll(async () => {
    await store.setAuthRoles([])
    await store.setRegistrationType(null)
  })

  it('renders base component with correct sub components', async () => {
    expect(wrapper.findComponent(HomeCertification).exists()).toBe(true)
    expect(wrapper.findComponent(InputFieldDatePicker).exists()).toBe(false)

    /// Verify Radio group does not exist
    expect(wrapper.find(getTestId('certification-option-btns')).exists()).toBe(false)

    // Verify only csa-form is shown
    expect(wrapper.find('#csa-form').exists()).toBe(true)
    expect(wrapper.find('#engineer-form').exists()).toBe(false)
    expect(wrapper.find('#no-certification').exists()).toBe(false)
    expect(wrapper.find(getTestId('no-certification-tooltip')).exists()).toBe(false)
  })
})
