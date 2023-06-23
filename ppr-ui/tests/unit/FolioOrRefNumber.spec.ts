// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'

// Components
import { FolioOrReferenceNumber } from '@/components/mhrRegistration/ReviewConfirm'
import { FormField } from '@/components/common'

// Utilities
import { getLastEvent, getTestId } from './utils'
import { useStore } from '@/store/store'
import { setActivePinia, createPinia } from 'pinia'

// Resources
import { folioOrRefConfig } from '@/resources/attnRefConfigs'

Vue.use(Vuetify)
const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<Any> object with the given parameters.
 */
function createComponent (propsData: any): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)

  return mount((FolioOrReferenceNumber as any), {
    localVue,
    propsData,
    store,
    vuetify
  })
}

const folioOrRefSectionId = 'folio-or-reference-number'

const folioOrRefProps = {
  sectionId: folioOrRefSectionId,
  sectionNumber: null,
  validate: false
}

describe('Attention', () => {
  it('renders the component properly', () => {
    const wrapper: Wrapper<any> = createComponent(folioOrRefProps)
    expect(wrapper.findComponent(FolioOrReferenceNumber).exists()).toBe(true)
    expect(wrapper.findComponent(FormField).exists()).toBe(true)
    expect(wrapper.find(getTestId(`${folioOrRefSectionId}-title`)).exists()).toBe(true)
    expect(wrapper.find(getTestId(`${folioOrRefSectionId}-description`)).exists()).toBe(true)
    expect(wrapper.find(getTestId(`${folioOrRefSectionId}-form`)).exists()).toBe(true)
    expect(wrapper.find(getTestId(`${folioOrRefSectionId}-label`)).exists()).toBe(true)
    expect(wrapper.find(getTestId(`${folioOrRefSectionId}-text-field`)).exists()).toBe(true)
  })
  it('adds a section number to title', () => {
    const wrapper: Wrapper<any> = createComponent({ ...folioOrRefProps, sectionNumber: 1 })
    const title = wrapper.find(getTestId(`${folioOrRefSectionId}-title`))
    expect(title.text()).toBe(`1. ${folioOrRefConfig.title}`)
  })
  it('has the right configurations', () => {
    const wrapper: Wrapper<any> = createComponent(folioOrRefProps)
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
    const wrapper: Wrapper<any> = createComponent({ sectionId: folioOrRefSectionId, validate: true })
    const input = wrapper.find(getTestId(`${folioOrRefSectionId}-text-field`))

    await input.setValue('a'.repeat(30))
    await nextTick()
    let messages = wrapper.findAll('.v-messages__message')
    expect(wrapper.find('.error-text').exists()).toBe(false)
    expect(messages.length).toBe(0)
    expect(getLastEvent(wrapper, 'isFolioOrRefNumValid')).toBe(true)

    await input.setValue('a'.repeat(31))
    await nextTick()
    messages = wrapper.findAll('.v-messages__message')
    expect(wrapper.find('.error-text').exists()).toBe(true)
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 30 characters')
    expect(getLastEvent(wrapper, 'isFolioOrRefNumValid')).toBe(false)
  })
})
