import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import { getTestId } from './utils'
import { ManufacturerMakeModel, ManufacturedYearInput, ManufacturedYearSelect } from '@/components/mhrRegistration'
import { MhrRegistrationType } from '@/resources'
import { mockedManufacturerAuthRoles } from './test-data'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

setActivePinia(createPinia())
const store = useStore()

/**
 * Creates and mounts a component, so that it can be tested.
 * @returns a Wrapper object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)

  return mount((ManufacturerMakeModel as any), {
    localVue,
    store,
    vuetify
  })
}

// Error message class selector
const ERROR_MSG = '.error--text .v-messages__message'

describe('ManufacturerMakeModel component - staff', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
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

  it('verifes Name of Manufactuer field is not disabled', async () => {
    expect(wrapper.find(getTestId('manufacturer-name')).attributes('disabled')).toBe(undefined)
  })

  it('show error messages for Name of Manufacturer field', async () => {
    wrapper.find(getTestId('manufacturer-name')).setValue('x')
    await nextTick()
    wrapper.find(getTestId('manufacturer-name')).setValue('')
    await nextTick()
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(1)
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('Enter a manufacturer')
  })

  it('show error messages for Manufacturer Make Model inputs', async () => {
    wrapper.find(getTestId('manufacturer-name')).setValue('x'.repeat(70))
    wrapper.find(getTestId('manufacture-year')).setValue('x'.repeat(6))
    wrapper.find(getTestId('manufacturer-make')).setValue('x'.repeat(70))
    wrapper.find(getTestId('manufacturer-model')).setValue('x'.repeat(70))
    await nextTick()
    const messages = wrapper.findAll(ERROR_MSG)
    expect(messages.length).toBe(4)
  })

  it('show error messages for Year of Manufacture field', async () => {
    const yearInputField = wrapper.find(getTestId('manufacture-year'))

    yearInputField.setValue('1899')
    await nextTick()
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(1)
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('19 or 20')

    yearInputField.setValue('')
    yearInputField.setValue('1955')
    await nextTick()
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(0)

    yearInputField.setValue('')
    yearInputField.setValue('20')
    await nextTick()
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('Minimum 4')

    yearInputField.setValue('')
    yearInputField.setValue('200000')
    await nextTick()
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('Maximum 4')

    yearInputField.setValue('')
    yearInputField.setValue('20aa')
    await nextTick()
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('numbers only')

    yearInputField.setValue('')
    yearInputField.setValue('2033') // Enter grater number than year + 1
    await nextTick()
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('more than 1')
  })

  it('show error messages for Make and Model fields', async () => {
    wrapper.find(getTestId('manufacturer-make')).setValue('x'.repeat(30))
    wrapper.find(getTestId('manufacturer-model')).setValue('x'.repeat(30))
    await nextTick()
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(0)

    // Enter more than 65 chars into Make and Model field to
    // exceed the limit for combined field length
    wrapper.find(getTestId('manufacturer-make')).setValue('x'.repeat(35))
    wrapper.find(getTestId('manufacturer-model')).setValue('x'.repeat(35))
    await nextTick()
    await nextTick()
    expect(wrapper.findAll(ERROR_MSG).length).toBe(2)
    expect(wrapper.findAll(ERROR_MSG).at(0).text()).toContain('cannot exceed 65')
    expect(wrapper.findAll(ERROR_MSG).at(1).text()).toContain('cannot exceed 65')
  })
})

describe('ManufacturerMakeModel component - manufacturer', () => {
  let wrapper: Wrapper<any>

  beforeAll(async () => {
    await store.setAuthRoles(mockedManufacturerAuthRoles)
    await store.setRegistrationType(MhrRegistrationType)
  })

  beforeEach(async () => {
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  afterAll(async () => {
    await store.setAuthRoles(null)
    await store.setRegistrationType(null)
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

  it('verifes Name of Manufacturer field is disabled', async () => {
    expect(wrapper.find(getTestId('manufacturer-name')).attributes('disabled')).toBe('disabled')
  })

  it('show error messages for Manufacturer Make Model inputs', async () => {
    wrapper.find(getTestId('manufacturer-make')).setValue('x'.repeat(70))
    wrapper.find(getTestId('manufacturer-model')).setValue('x'.repeat(70))
    await nextTick()
    const messages = wrapper.findAll(ERROR_MSG)
    expect(messages.length).toBe(2)
  })

  it('checks year of manufacturer select works as expected', async () => {
    const yearSelect = wrapper.findComponent(ManufacturedYearSelect)
    const select = yearSelect.find('.v-select')
    const items = select.props('items')
    const currentYear = new Date().getFullYear()
    expect(items).toStrictEqual([currentYear + 1, currentYear, currentYear - 1])
  })
})
