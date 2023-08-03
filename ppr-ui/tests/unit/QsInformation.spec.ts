import { QsInformation } from '@/views'
import { createComponent, setupMockUser } from './utils'
import { Wrapper } from '@vue/test-utils'
import { defaultFlagSet } from '@/utils'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '@/store/store'
import { MhrSubTypes } from '@/enums'
import { nextTick } from 'vue'
import flushPromises from 'flush-promises'

setActivePinia(createPinia())
const store = useStore()

describe('QsInformation', () => {
  let wrapper: Wrapper<any> | any
  const subProduct = MhrSubTypes.LAWYERS_NOTARIES

  beforeAll(async () => {
    defaultFlagSet['mhr-user-access-enabled'] = true
    await store.setMhrSubProduct(MhrSubTypes.LAWYERS_NOTARIES)
    await store.setMhrQsInformation(null)
    await setupMockUser()
    await flushPromises()
    await nextTick()
  })

  beforeEach(async () => {
    wrapper = await createComponent(QsInformation)
    await flushPromises()
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the component', () => {
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the "Qualified Supplier" section with the correct sub-product', () => {
    const qualifiedSupplierSection = wrapper.find('.qs-information-form')
    expect(qualifiedSupplierSection.exists()).toBe(true)

    const heading = qualifiedSupplierSection.find('h2')
    expect(heading.exists()).toBe(true)
    expect(heading.text()).toBe(`Qualified Supplier (${subProduct}) Information`)
  })

  it('renders the "Service Agreement" section', () => {
    const serviceAgreementSection = wrapper.find('.qs-service-agreement')
    expect(serviceAgreementSection.exists()).toBe(true)

    const heading = serviceAgreementSection.find('h2')
    expect(heading.exists()).toBe(true)
    expect(heading.text()).toBe('Service Agreement')

    const downloadBtn = serviceAgreementSection.find('v-btn')
    expect(downloadBtn.exists()).toBe(true)
    // Add more assertions for the content of the section if needed.
  })

  it('renders the "Qualified Supplier - [sub-product]" access information section', () => {
    const introSection = wrapper.find('.qs-information-intro')
    expect(introSection.exists()).toBe(true)

    const strongTag = introSection.find('strong')
    expect(strongTag.exists()).toBe(true)
    expect(strongTag.text()).toBe(`Qualified Supplier - ${subProduct}`)
  })

  // Add more tests for specific behaviors and interactions if needed.
})
