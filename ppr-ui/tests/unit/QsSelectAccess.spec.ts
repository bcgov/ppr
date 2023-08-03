import { QsSelectAccess } from '@/views'
import { FormCard, SubProductSelector } from '@/components/common'
import { setupMockUser } from './utils'
import { mount, Wrapper } from '@vue/test-utils'
import { defaultFlagSet } from '@/utils'

describe('QsSelectAccess', () => {
  let wrapper: Wrapper<any>
  defaultFlagSet['mhr-user-access-enabled'] = true
  setupMockUser()

  beforeEach(async () => {
    wrapper = await mount(QsSelectAccess as any)
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the "Qualified Supplier Access Type" section', () => {
    const section = wrapper.find('#qs-select-access')
    expect(section.exists()).toBe(true)

    const heading = section.find('h2')
    expect(heading.exists()).toBe(true)
    expect(heading.text()).toBe('Qualified Supplier Access Type')

    const description = section.find('p')
    expect(description.exists()).toBe(true)
    // Add more assertions for the content of the description if needed.
  })

  it('renders the "Select Access Type" FormCard component', () => {
    const formCard = wrapper.findComponent(FormCard)
    expect(formCard.exists()).toBe(true)
  })

  it('renders the SubProductSelector component inside the FormCard', () => {
    const subProductSelector = wrapper.findComponent(SubProductSelector)
    expect(subProductSelector.exists()).toBe(true)
  })
})
