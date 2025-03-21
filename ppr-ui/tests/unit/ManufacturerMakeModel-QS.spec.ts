import { mockedManufacturerAuthRoles } from './test-data'
import { MhrRegistrationType } from '../../src/resources'
import { ProductCode } from '../../src/enums'
import { createComponent, getTestId } from './utils'
import {
  ManufacturedYearInput,
  ManufacturedYearSelect,
  ManufacturerMakeModel
} from '../../src/components/mhrRegistration'
import { nextTick } from 'vue'
import { useStore } from '@/store/store'

const store = useStore()

// Error message class selector
const ERROR_MSG = '.v-input--error .v-messages__message'

describe('ManufacturerMakeModel component - manufacturer', () => {
  let wrapper

  beforeAll(async () => {
    await store.setAuthRoles(mockedManufacturerAuthRoles)
    await store.setRegistrationType(MhrRegistrationType)
    await store.setUserProductSubscriptionsCodes([ProductCode.MHR, ProductCode.MANUFACTURER])
  })

  beforeEach(async () => {
    await store.setAuthRoles(mockedManufacturerAuthRoles)
    await store.setRegistrationType(MhrRegistrationType)
    await store.setUserProductSubscriptionsCodes([ProductCode.MHR, ProductCode.MANUFACTURER])

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