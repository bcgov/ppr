// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { useStore } from '@/store/store'
import { createPinia, setActivePinia } from 'pinia'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { AmendmentDescription } from '@/components/registration'
import { getLastEvent } from './utils'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

setActivePinia(createPinia())
const store = useStore()

// Input field selectors / buttons
const amendmentDescrption = '#amendment-detail-description'
const descriptionTxt = '#amendment-description'
const errorMsg = '.v-messages__message'
const showError = '.invalid-message'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (showInvalid: boolean, summaryView: boolean): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount((AmendmentDescription as any), {
    localVue,
    propsData: { setShowErrors: showInvalid, isSummary: summaryView },
    store,
    vuetify
  })
}

describe('Amendment Detail Description tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.setAmendmentDescription('')
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders default with no existing description', async () => {
    wrapper = createComponent(false, false)
    expect(wrapper.findComponent(AmendmentDescription).exists()).toBe(true)
    expect(wrapper.vm.detailDescription).toBe('')
    expect(wrapper.vm.amendmentDescription).toBe('')
    expect(wrapper.vm.showErrorComponent).toBe(false)
    expect(wrapper.vm.valid).toBe(true)
    expect(wrapper.findAll(descriptionTxt).length).toBe(1)
    expect(wrapper.findAll(errorMsg).length).toBe(0)
    expect(wrapper.findAll(showError).length).toBe(0)
  })

  it('updates amendment with new description text valid length', async () => {
    wrapper = createComponent(false, false)
    await wrapper.find(descriptionTxt).setValue('valid amendment description')
    expect(wrapper.vm.summaryView).toBe(false)
    expect(wrapper.vm.detailDescription).toBe('valid amendment description')
    expect(wrapper.vm.amendmentDescription).toBe('valid amendment description')
    expect(wrapper.vm.valid).toBe(true)
    expect(getLastEvent(wrapper, 'valid')).toBe(true)
  })

  it('updates amendment with new description text invalid length', async () => {
    wrapper = createComponent(false, false)
    const invalidLengthTxt = 'x'.repeat(4001)
    await wrapper.find(descriptionTxt).setValue(invalidLengthTxt)
    expect(wrapper.vm.summaryView).toBe(false)
    expect(wrapper.vm.valid).toBe(false)
    expect(getLastEvent(wrapper, 'valid')).toBe(false)
    await wrapper.find(descriptionTxt).setValue('valid amendment description')
    expect(wrapper.vm.detailDescription).toBe('valid amendment description')
    expect(wrapper.vm.valid).toBe(true)
    expect(getLastEvent(wrapper, 'valid')).toBe(true)
  })
})

describe('Amendment Detail Description summary view tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.setAmendmentDescription('test')
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the summary view of the amendment description', async () => {
    wrapper = createComponent(false, true)
    expect(wrapper.findComponent(AmendmentDescription).exists()).toBe(true)
    expect(wrapper.vm.summaryView).toBe(true)
    expect(wrapper.vm.detailDescription).toBe('test')
    expect(wrapper.vm.amendmentDescription).toBe('test')
    expect(wrapper.vm.showErrorComponent).toBe(false)
    expect(wrapper.vm.valid).toBe(true)
  })
})
