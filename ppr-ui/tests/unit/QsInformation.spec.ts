import { QsInformation } from '@/pages'
import { createComponent, getTestId, setupMockUser } from './utils'
import { defaultFlagSet } from '@/utils'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '@/store/store'
import { MhrSubTypes } from '@/enums'
import { nextTick } from 'vue'
import flushPromises from 'flush-promises'
import { useUserAccess } from "@/composables"

vi.mock('@/utils/mhr-api-helper', async (importOriginal) => {
  const mod = await importOriginal<any>()
  return {
    ...mod,
    getQsServiceAgreements: vi.fn().mockResolvedValue(new Blob(['test'], { type: 'application/pdf' }))
  }
})

setActivePinia(createPinia())
const store = useStore()

const subProducts: MhrSubTypes[] = [MhrSubTypes.LAWYERS_NOTARIES, MhrSubTypes.MANUFACTURER, MhrSubTypes.DEALERS]
for (const subProduct of subProducts) {
  describe(`${subProduct}: QsInformation`, () => {
    let wrapper
    const { setQsInformationModel } = useUserAccess()

    beforeAll(async () => {
      await store.setMhrSubProduct(subProduct)
      await setQsInformationModel(subProduct)
      await setupMockUser()
      await flushPromises()
      await nextTick()
    })

    beforeEach(async () => {
      wrapper = await createComponent(QsInformation)
      await flushPromises()
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
      expect(heading.text()).toBe('Qualified Suppliers’ Agreement')

      expect(serviceAgreementSection.find(getTestId('download-agreement-btn')).exists()).toBe(true)
    })

    it('renders the "Qualified Supplier - [sub-product]" access information section', () => {
      const introSection = wrapper.find('.qs-information-intro')
      expect(introSection.exists()).toBe(true)

      const strongTag = introSection.find('strong')
      expect(strongTag.exists()).toBe(true)
      expect(strongTag.text()).toBe(`Qualified Supplier - ${subProduct}`)
    })

    it('renders the DBA field when applicable', async () => {
      const partyForm = await wrapper.find('#party-form')
      expect(partyForm.exists()).toBe(true)

      const dbaField = await wrapper.find('#dba-name')
      expect(dbaField.exists()).toBe([MhrSubTypes.MANUFACTURER, MhrSubTypes.DEALERS].includes(subProduct))
    })

    it('renders the home location component for manufacturers/dealers', async () => {
      const homeLocationForm = await wrapper.find('.manufacturer-home-location-form')
      expect(homeLocationForm.exists()).toBe([MhrSubTypes.MANUFACTURER, MhrSubTypes.DEALERS].includes(subProduct))
    })
  })
}
