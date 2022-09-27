import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import { getTestId } from './utils'
import { ManufacturerMakeModel } from '@/components/mhrRegistration'

Vue.use(Vuetify)
const store = getVuexStore()

/**
 * Creates and mounts a component, so that it can be tested.
 * @returns a Wrapper object with the given parameters.
 */
function createComponent (): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  return mount(ManufacturerMakeModel, {
    localVue,
    store
  })
}

// Error message class selector
const ERROR_MSG = '.error--text .v-messages__message'

describe('Other Information component', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    wrapper = createComponent()
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component', async () => {
    const manufacturerSection = wrapper.findComponent(ManufacturerMakeModel)
    expect(manufacturerSection.exists()).toBe(true)

    manufacturerSection.find(getTestId('manufacturer-name')).exists()
    manufacturerSection.find(getTestId('manufacture-year')).exists()
    manufacturerSection.find(getTestId('circa-year-checkbox')).exists()
    manufacturerSection.find(getTestId('circa-year-tooltip')).exists()
    manufacturerSection.find(getTestId('manufacturer-make')).exists()
    manufacturerSection.find(getTestId('manufacturer-model')).exists()
  })

  it('show error messages for Name of Manufacturer field', async () => {
    const manufacturerSection = wrapper.findComponent(ManufacturerMakeModel)
    manufacturerSection.find(getTestId('manufacturer-name')).setValue('x')
    await Vue.nextTick()
    await Vue.nextTick()
    manufacturerSection.find(getTestId('manufacturer-name')).setValue('')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(manufacturerSection.findAll(ERROR_MSG).length).toBe(1)
    expect(manufacturerSection.findAll(ERROR_MSG).at(0).text()).toContain('Enter a manufacturer')
  })

  it('show error messages for Manufacturer Make Model inputs', async () => {
    const manufacturerSection = wrapper.findComponent(ManufacturerMakeModel)
    manufacturerSection.find(getTestId('manufacturer-name')).setValue('x'.repeat(70))
    manufacturerSection.find(getTestId('manufacture-year')).setValue('x'.repeat(6))
    manufacturerSection.find(getTestId('manufacturer-make')).setValue('x'.repeat(70))
    manufacturerSection.find(getTestId('manufacturer-model')).setValue('x'.repeat(70))
    await Vue.nextTick()
    await Vue.nextTick()
    const messages = manufacturerSection.findAll(ERROR_MSG)
    expect(messages.length).toBe(4)
  })

  it('show error messages for Year of Manufacture field', async () => {
    const manufacturerSection = wrapper.findComponent(ManufacturerMakeModel)
    const yearInputField = manufacturerSection.find(getTestId('manufacture-year'))

    yearInputField.setValue('1899')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(manufacturerSection.findAll(ERROR_MSG).length).toBe(1)
    expect(manufacturerSection.findAll(ERROR_MSG).at(0).text()).toContain('19 or 20')

    yearInputField.setValue('')
    yearInputField.setValue('1955')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(manufacturerSection.findAll(ERROR_MSG).length).toBe(0)

    yearInputField.setValue('')
    yearInputField.setValue('20')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(manufacturerSection.findAll(ERROR_MSG).at(0).text()).toContain('Minimum 4')

    yearInputField.setValue('')
    yearInputField.setValue('200000')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(manufacturerSection.findAll(ERROR_MSG).at(0).text()).toContain('Maximum 4')

    yearInputField.setValue('')
    yearInputField.setValue('20aa')
    await Vue.nextTick()
    await Vue.nextTick()
    expect(manufacturerSection.findAll(ERROR_MSG).at(0).text()).toContain('numbers only')

    yearInputField.setValue('')
    yearInputField.setValue('2033') // Enter grater number than year + 1
    await Vue.nextTick()
    await Vue.nextTick()
    expect(manufacturerSection.findAll(ERROR_MSG).at(0).text()).toContain('more than 1')
  })

  it('show error messages for Make and Model fields', async () => {
    const manufacturerSection = wrapper.findComponent(ManufacturerMakeModel)
    manufacturerSection.find(getTestId('manufacturer-make')).setValue('x'.repeat(30))
    manufacturerSection.find(getTestId('manufacturer-model')).setValue('x'.repeat(30))
    await Vue.nextTick()
    await Vue.nextTick()
    expect(manufacturerSection.findAll(ERROR_MSG).length).toBe(0)

    // Enter more than 65 chars into Make and Model field to
    // exceed the limit for combined field length
    manufacturerSection.find(getTestId('manufacturer-make')).setValue('x'.repeat(35))
    manufacturerSection.find(getTestId('manufacturer-model')).setValue('x'.repeat(35))
    await Vue.nextTick()
    await Vue.nextTick()
    expect(manufacturerSection.findAll(ERROR_MSG).length).toBe(2)
    expect(manufacturerSection.findAll(ERROR_MSG).at(0).text()).toContain('cannot exceed 65')
    expect(manufacturerSection.findAll(ERROR_MSG).at(1).text()).toContain('cannot exceed 65')
  })
})
