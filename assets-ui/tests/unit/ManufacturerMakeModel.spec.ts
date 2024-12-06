import { nextTick } from 'vue'
import { createComponent } from './utils'
import { getTestId } from './utils'
import { ManufacturerMakeModel, ManufacturedYearInput, ManufacturedYearSelect } from '@/components/mhrRegistration'
import { MhrRegistrationType } from '@/resources'
import { mockedManufacturerAuthRoles } from './test-data'
import { ProductCode } from '@/enums'
import { useStore } from '@/store/store'

const store = useStore()

// Error message class selector
const ERROR_MSG = '.v-input--error .v-messages__message'

describe('ManufacturerMakeModel component - staff', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(ManufacturerMakeModel)
  })

  it('renders the component', async () => {
    expect(wrapper.findComponent(ManufacturerMakeModel).exists()).toBe(true)
    expect(wrapper.findComponent(ManufacturedYearInput).exists()).toBe(true)
    expect(wrapper.findComponent(ManufacturedYearSelect).exists()).toBe(false)

    wrapper.find(getTestId('manufacturer-name')).exists()
    wrapper.find(getTestId('manufacture-year')).exists()
    wrapper.find(getTestId('circa-year-checkbox')).exists()
    wrapper.find(getTestId('circa-year-tooltip')).exists()
    wrapper.find(getTestId('manufacturer-make')).exists()
    wrapper.find(getTestId('manufacturer-model')).exists()
  })

  it('verifies Name of Manufacturer field is not disabled', async () => {
    expect(wrapper.find(getTestId('manufacturer-name')).attributes('disabled')).toBe(undefined)
  })

  it('show error messages for Name of Manufacturer field', async () => {
    await wrapper.find('#manufacturer-name').setValue('x')
    await nextTick()
    await wrapper.find('#manufacturer-name').setValue('')
    await nextTick()

    expect(wrapper.findAll(ERROR_MSG).length).toBe(1)
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('Enter a manufacturer')
  })

  it('show error messages for Manufacturer Make Model inputs', async () => {
    await wrapper.find('#manufacturer-name').setValue('x'.repeat(70))
    await wrapper.find('#manufacturer-year').setValue('x'.repeat(6))
    await wrapper.find('#manufacturer-make').setValue('x'.repeat(70))
    await wrapper.find('#manufacturer-model').setValue('x'.repeat(70))
    await nextTick()
    const messages = wrapper.findAll(ERROR_MSG)
    expect(messages.length).toBe(4)
  })

  it('show error messages for Year of Manufacture field', async () => {
    // Set defaults to isolate year validation
    const form = await wrapper.findComponent('.v-form')
    await wrapper.find('#manufacturer-name').setValue('x')
    await wrapper.find('#manufacturer-make').setValue('x')
    await wrapper.find('#manufacturer-model').setValue('x')

    const yearInputField = await wrapper.find('#manufacturer-year')
    yearInputField.setValue('1899')
    await nextTick()

    // Validate Form
    await form.vm.validate()
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(1)
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('19 or 20')

    yearInputField.setValue('')
    yearInputField.setValue('1955')
    await nextTick()

    // Validate Form
    await form.vm.validate()
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(0)

    yearInputField.setValue('')
    yearInputField.setValue('20')
    await nextTick()

    // Validate Form
    await form.vm.validate()
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('Minimum 4')

    yearInputField.setValue('')
    yearInputField.setValue('200000')
    await nextTick()

    // Validate Form
    await form.vm.validate()
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('Maximum 4')

    yearInputField.setValue('')
    yearInputField.setValue('20aa')
    await nextTick()

    // Validate Form
    await form.vm.validate()
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('numbers only')

    yearInputField.setValue('')
    yearInputField.setValue('2033') // Enter grater number than year + 1
    await nextTick()

    // Validate Form
    await form.vm.validate()
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('more than 1')
  })

  it('show error messages for Make and Model fields', async () => {
    const form = await wrapper.findComponent('.v-form')
    await wrapper.find('#manufacturer-name').setValue('x')
    await wrapper.find('#manufacturer-year').setValue('2000')
    await wrapper.find('#manufacturer-make').setValue('x'.repeat(30))
    await wrapper.find('#manufacturer-model').setValue('x'.repeat(30))
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(0)

    // Enter more than 65 chars into Make and Model field to
    // exceed the limit for combined field length
    await wrapper.find('#manufacturer-make').setValue('x'.repeat(35))
    await wrapper.find('#manufacturer-model').setValue('x'.repeat(35))
    await nextTick()

    // Validate Form
    await form.vm.validate()
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(2)
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('cannot exceed 65')
    expect(wrapper.findAll(ERROR_MSG).at(1).text()).toContain('cannot exceed 65')
  })
})

describe('ManufacturerMakeModel component - manufacturer', () => {
  let wrapper

  beforeAll(async () => {
    await store.setAuthRoles(mockedManufacturerAuthRoles)
    await store.setRegistrationType(MhrRegistrationType)
    await store.setUserProductSubscriptionsCodes([ProductCode.MHR, ProductCode.MANUFACTURER])
  })

  beforeEach(async () => {
    wrapper = await createComponent(ManufacturerMakeModel)
  })

  it('renders the component', async () => {
    expect(wrapper.findComponent(ManufacturerMakeModel).exists()).toBe(true)
    expect(wrapper.findComponent(ManufacturedYearInput).exists()).toBe(false)
    expect(wrapper.findComponent(ManufacturedYearSelect).exists()).toBe(true)

    wrapper.find(getTestId('manufacturer-name')).exists()
    expect(wrapper.find(getTestId('manufacture-year')).exists()).toBe(false)
    expect(wrapper.find(getTestId('manufacture-year-select')).exists()).toBe(true)
    expect(wrapper.find(getTestId('circa-year-checkbox')).exists()).toBe(false)
    expect(wrapper.find(getTestId('circa-year-tooltip')).exists()).toBe(false)
    wrapper.find(getTestId('manufacturer-make')).exists()
    wrapper.find(getTestId('manufacturer-model')).exists()
  })

  it('verifies Name of Manufacturer field is disabled', async () => {
    expect(wrapper.find('#manufacturer-name').attributes().disabled).toBeDefined()
  })

  it('show error messages for Manufacturer Make Model inputs', async () => {
    await wrapper.find('#manufacturer-make').setValue('x'.repeat(70))
    await wrapper.find('#manufacturer-model').setValue('x'.repeat(70))
    await nextTick()

    const messages = wrapper.findAll(ERROR_MSG)
    expect(messages.length).toBe(2)
  })

  it('checks year of manufacturer select works as expected', async () => {
    const yearSelect = wrapper.findComponent(ManufacturedYearSelect)
    const select = await yearSelect.findComponent('.v-select')
    const currentYear = new Date().getFullYear()

    expect(select.vm.items).toStrictEqual([currentYear + 1, currentYear, currentYear - 1])
  })
})
