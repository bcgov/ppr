// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createLocalVue, mount, Wrapper } from '@vue/test-utils'

// Components
import { Attention } from '@/components/mhrRegistration/ReviewConfirm'
import { FieldForm } from '@/components/common'

// Utilities
import { getTestId } from './utils'
import { useStore } from '@/store/store'
import { setActivePinia, createPinia } from 'pinia'

// Resources
import { attentionConfig, attentionConfigManufacturer } from '@/resources/attnRefConfigs'
import { mockedManufacturerAuthRoles } from './test-data'
import { MhrRegistrationType } from '@/resources'
import { MhrSectVal } from '@/composables/mhrRegistration/enums'
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

const attentionProps = {
  mhrSect: '',
  sectionNumber: null,
  validate: false
}

describe('Attention', () => {
  it('renders the component properly', () => {
    const wrapper: Wrapper<any> = createComponent({ attentionProps })
    expect(wrapper.findComponent(Attention).exists()).toBe(true)
    expect(wrapper.findComponent(FieldForm).exists()).toBe(true)
    expect(wrapper.find(getTestId('mhr-attention-title')).exists()).toBe(true)
    expect(wrapper.find(getTestId('mhr-attention-description')).exists()).toBe(true)
    expect(wrapper.find(getTestId('mhr-attention-form')).exists()).toBe(true)
    expect(wrapper.find(getTestId('mhr-attention-label')).exists()).toBe(true)
    expect(wrapper.find(getTestId('mhr-attention-text-field')).exists()).toBe(true)
  })
  it('adds a section number to title', () => {
    const wrapper: Wrapper<any> = createComponent({ ...attentionProps, sectionNumber: 1 })
    const title = wrapper.find(getTestId('mhr-attention-title'))
    expect(title.text()).toBe(`1. ${attentionConfig.title}`)
  })
  it('has the right configurations for staff', () => {
    const wrapper: Wrapper<any> = createComponent({ attentionProps })
    const description = wrapper.find(getTestId('mhr-attention-description'))
    const title = wrapper.find(getTestId('mhr-attention-title'))
    const label = wrapper.find(getTestId('mhr-attention-label'))
    const inputLabel = wrapper.find('.v-label')

    expect(description.text()).toBe(attentionConfig.description)
    expect(title.text()).toBe(attentionConfig.title)
    expect(label.text()).toBe(attentionConfig.inputTitle)
    expect(inputLabel.text()).toBe(attentionConfig.inputLabel)
  })

  it('has the right configurations for manufacturer', async () => {
    await store.setAuthRoles(mockedManufacturerAuthRoles)
    const wrapper: Wrapper<any> = createComponent({ attentionProps })

    const description = wrapper.find(getTestId('mhr-attention-description'))
    const title = wrapper.find(getTestId('mhr-attention-title'))
    const label = wrapper.find(getTestId('mhr-attention-label'))
    const inputLabel = wrapper.find('.v-label')

    expect(description.text()).toBe(attentionConfigManufacturer.description)
    expect(title.text()).toBe(attentionConfigManufacturer.title)
    expect(label.text()).toBe(attentionConfigManufacturer.inputTitle)
    expect(inputLabel.text()).toBe(attentionConfigManufacturer.inputLabel)
    await store.setAuthRoles([])
  })

  it('validates maxCharacters', async () => {
    await store.setAuthRoles(mockedManufacturerAuthRoles)
    await store.setRegistrationType(MhrRegistrationType)
    const wrapper: Wrapper<any> = createComponent({ mhrSect: MhrSectVal.REVIEW_CONFIRM_VALID, validate: true })
    const input = wrapper.find(getTestId('mhr-attention-text-field'))

    await input.setValue('a'.repeat(40))
    await nextTick()
    let messages = wrapper.findAll('.v-messages__message')
    expect(wrapper.find('.error-text').exists()).toBe(false)
    expect(messages.length).toBe(0)
    expect(store.getStateModel.mhrValidationManufacturerState.reviewConfirmValid?.attentionValid).toBe(true)

    await input.setValue('a'.repeat(256))
    await nextTick()
    messages = wrapper.findAll('.v-messages__message')
    expect(wrapper.find('.error-text').exists()).toBe(true)
    expect(messages.length).toBe(1)
    expect(messages.at(0).text()).toBe('Maximum 40 characters')
    expect(store.getStateModel.mhrValidationManufacturerState.reviewConfirmValid?.attentionValid).toBe(false)

    await store.setAuthRoles([])
    await store.setRegistrationType(null)
  })
})
