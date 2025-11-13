import { nextTick } from 'vue'
import { beforeEach } from 'vitest'
import { createComponent, getLastEvent, getTestId } from './utils'
import { Attention, FormField } from '@/components/common'
import { useStore } from '@/store/store'
import { attentionConfig, attentionConfigManufacturer } from '@/resources'

const store = useStore()

const sectionId = 'attention'

const attentionProps = {
  sectionId,
  sectionNumber: null,
  validate: false
}

describe('Attention', () => {
  let wrapper
  beforeEach(async () => {
    wrapper = await createComponent(Attention, attentionProps)
  })

  it('renders the component properly', async () => {
    expect(wrapper.findComponent(Attention).exists()).toBe(true)
    expect(wrapper.findComponent(FormField).exists()).toBe(true)
    expect(wrapper.find(getTestId(`${sectionId}-title`)).exists()).toBe(true)
    expect(wrapper.find(getTestId(`${sectionId}-description`)).exists()).toBe(true)
    expect(wrapper.find(getTestId(`${sectionId}-form`)).exists()).toBe(true)
    expect(wrapper.find(getTestId(`${sectionId}-label`)).exists()).toBe(true)
    expect(wrapper.find(getTestId(`${sectionId}-text-field`)).exists()).toBe(true)
  })

  it('adds a section number to title', async () => {
    wrapper = await createComponent(Attention, { ...attentionProps, sectionNumber: 1 })
    await nextTick()
    const title = wrapper.find(getTestId(`${sectionId}-title`))
    expect(title.text()).toBe(`1. ${attentionConfig.title}`)
  })

  it('has the right configurations for staff', async () => {
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
    const wrapper = await createComponent(Attention, { ...attentionProps, configOverride: attentionConfigManufacturer })

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
    wrapper = await createComponent(Attention, { ...attentionProps, validate: true })
    const input = wrapper.findComponent(getTestId(`${sectionId}-text-field`))

    await input.setValue('a'.repeat(41))
    await nextTick()
    let messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 40 characters')
    expect(getLastEvent(wrapper, 'isAttentionValid')).toBe(false)

    await input.setValue('a'.repeat(40))
    await nextTick()
    messages = wrapper.findAll('.v-messages__message')
    expect(messages.length).toBe(1)
    expect(getLastEvent(wrapper, 'isAttentionValid')).toBe(true)
  })
})
