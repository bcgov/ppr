// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'

// Components
import { Attention } from '@/components/mhrRegistration/ReviewConfirm'
import { FormField } from '@/components/common'

// Utilities
import { getLastEvent, getTestId } from './utils'
import { useStore } from '@/store/store'
import { setActivePinia, createPinia } from 'pinia'

// Resources
import { attentionConfig, attentionConfigManufacturer } from '@/resources/attnRefConfigs'
import { mockedManufacturerAuthRoles } from './test-data'

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

  return mount((Attention as any), {
    localVue,
    propsData,
    store,
    vuetify
  })
}

const sectionId = 'attention'

const attentionProps = {
  sectionId,
  sectionNumber: null,
  validate: false
}

describe('Attention', () => {
  it('renders the component properly', () => {
    const wrapper: Wrapper<any> = createComponent(attentionProps)
    expect(wrapper.findComponent(Attention).exists()).toBe(true)
    expect(wrapper.findComponent(FormField).exists()).toBe(true)
    expect(wrapper.find(getTestId(`${sectionId}-title`)).exists()).toBe(true)
    expect(wrapper.find(getTestId(`${sectionId}-description`)).exists()).toBe(true)
    expect(wrapper.find(getTestId(`${sectionId}-form`)).exists()).toBe(true)
    expect(wrapper.find(getTestId(`${sectionId}-label`)).exists()).toBe(true)
    expect(wrapper.find(getTestId(`${sectionId}-text-field`)).exists()).toBe(true)
  })
  it('adds a section number to title', () => {
    const wrapper: Wrapper<any> = createComponent({ ...attentionProps, sectionNumber: 1 })
    const title = wrapper.find(getTestId(`${sectionId}-title`))
    expect(title.text()).toBe(`1. ${attentionConfig.title}`)
  })
  it('has the right configurations for staff', () => {
    const wrapper: Wrapper<any> = createComponent(attentionProps)
    const description = wrapper.find(getTestId(`${sectionId}-description`))
    const title = wrapper.find(getTestId(`${sectionId}-title`))
    const label = wrapper.find(getTestId(`${sectionId}-label`))
    const inputLabel = wrapper.find('.v-label')

    expect(description.text()).toBe(attentionConfig.description)
    expect(title.text()).toBe(attentionConfig.title)
    expect(label.text()).toBe(attentionConfig.inputTitle)
    expect(inputLabel.text()).toBe(attentionConfig.inputLabel)
  })

  it('has the right configurations for manufacturer', async () => {
    await store.setAuthRoles(mockedManufacturerAuthRoles)
    const wrapper: Wrapper<any> = createComponent(attentionProps)

    const description = wrapper.find(getTestId(`${sectionId}-description`))
    const title = wrapper.find(getTestId(`${sectionId}-title`))
    const label = wrapper.find(getTestId(`${sectionId}-label`))
    const inputLabel = wrapper.find('.v-label')

    expect(description.text()).toBe(attentionConfigManufacturer.description)
    expect(title.text()).toBe(attentionConfigManufacturer.title)
    expect(label.text()).toBe(attentionConfigManufacturer.inputTitle)
    expect(inputLabel.text()).toBe(attentionConfigManufacturer.inputLabel)
    await store.setAuthRoles([])
  })

  it('validates the attention', async () => {
    const wrapper: Wrapper<any> = createComponent({ sectionId, validate: true })
    const input = wrapper.find(getTestId(`${sectionId}-text-field`))

    await input.setValue('a'.repeat(40))
    await nextTick()
    let messages = wrapper.findAll('.v-messages__message')
    expect(wrapper.find('.error-text').exists()).toBe(false)
    expect(messages.length).toBe(0)
    expect(getLastEvent(wrapper, 'isAttentionValid')).toBe(true)

    await input.setValue('a'.repeat(41))
    await nextTick()
    messages = wrapper.findAll('.v-messages__message')
    expect(wrapper.find('.error-text').exists()).toBe(true)
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 40 characters')
    expect(getLastEvent(wrapper, 'isAttentionValid')).toBe(false)
  })
})
