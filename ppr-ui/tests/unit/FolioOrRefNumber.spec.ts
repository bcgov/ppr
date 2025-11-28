import { createComponent, getLastEvent, getTestId } from './utils'
import { nextTick } from 'vue'
import { FolioOrReferenceNumber, FormField } from '@/components/common'
import { folioOrRefConfig } from '@/resources'

const folioOrRefSectionId = 'folio-or-reference-number'

const folioOrRefProps = {
  sectionId: folioOrRefSectionId,
  sectionNumber: null,
  validate: false
}

describe('Attention', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(FolioOrReferenceNumber, folioOrRefProps)
    await nextTick()
  })

  it('renders the component properly', () => {
    expect(wrapper.findComponent(FolioOrReferenceNumber).exists()).toBe(true)
    expect(wrapper.findComponent(FormField).exists()).toBe(true)
    expect(wrapper.find(getTestId(`${folioOrRefSectionId}-title`)).exists()).toBe(true)
    expect(wrapper.find(getTestId(`${folioOrRefSectionId}-description`)).exists()).toBe(true)
    expect(wrapper.find(getTestId(`${folioOrRefSectionId}-form`)).exists()).toBe(true)
    expect(wrapper.find(getTestId(`${folioOrRefSectionId}-label`)).exists()).toBe(true)
    expect(wrapper.find(getTestId(`${folioOrRefSectionId}-text-field`)).exists()).toBe(true)
  })
  it('adds a section number to title', async () => {
    wrapper = await createComponent(FolioOrReferenceNumber, { ...folioOrRefProps, sectionNumber: 1 })

    const title = wrapper.find(getTestId(`${folioOrRefSectionId}-title`))
    expect(title.text()).toBe(`1. ${folioOrRefConfig.title}`)
  })
  it('has the right configurations', () => {
    const description = wrapper.find(getTestId(`${folioOrRefSectionId}-description`))
    const title = wrapper.find(getTestId(`${folioOrRefSectionId}-title`))
    const label = wrapper.find(getTestId(`${folioOrRefSectionId}-label`))
    const inputLabel = wrapper.find('.v-label')

    expect(description.text()).toBe(folioOrRefConfig.description)
    expect(title.text()).toBe(folioOrRefConfig.title)
    expect(label.text()).toBe(folioOrRefConfig.inputTitle)
    expect(inputLabel.text()).toBe(folioOrRefConfig.inputLabel)
  })

  it('validates folioOrRefNumber', async () => {
    wrapper = await createComponent(FolioOrReferenceNumber, { sectionId: folioOrRefSectionId, validate: true })
    const input = await wrapper.findComponent(getTestId(`${folioOrRefSectionId}-text-field`))

    await input.setValue('a'.repeat(30))
    await nextTick()
    let messages = wrapper.findAll('.v-input--error .v-messages__message')
    expect(messages.length).toBe(0)
    expect(getLastEvent(wrapper, 'isFolioOrRefNumValid')).toBe(true)

    await input.setValue('a'.repeat(55))
    await nextTick()
    messages = wrapper.findAll('.v-input--error .v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 50 characters')
    expect(getLastEvent(wrapper, 'isFolioOrRefNumValid')).toBe(false)
  })
})
