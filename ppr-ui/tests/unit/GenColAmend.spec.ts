// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import { TiptapVuetifyPlugin, TiptapVuetify } from 'tiptap-vuetify'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { GenColAmend } from '@/components/collateral'
import { RegistrationFlowType } from '@/enums'
import { getLastEvent } from './utils'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
Vue.use(TiptapVuetifyPlugin, {
  // the next line is important! You need to provide the Vuetify Object to this place.
  vuetify, // same as "vuetify: vuetify"
  // optional, default to 'md' (default vuetify icons before v2.0.0)
  iconsGroup: 'mdi'
})
setActivePinia(createPinia())
const store = useStore()

// Input field selectors / buttons
const doneButtonSelector: string = '#done-btn-gen-col'
const deleteDescriptionTxt = '#general-collateral-delete-desc'
const addDescriptionTxt = '#general-collateral-add-desc'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (
  showInvalid: boolean
): Wrapper<any> {
  const localVue = createLocalVue()

  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount((GenColAmend as any), {
    localVue,
    propsData: { showInvalid: showInvalid },
    store,
    vuetify
  })
}

describe('GenColAmend tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
    await store.setGeneralCollateral([])
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders default', async () => {
    wrapper = createComponent(false)
    expect(wrapper.findComponent(GenColAmend).exists()).toBe(true)
    expect(wrapper.vm.addDesc).toBe('')
    expect(wrapper.vm.delDesc).toBe('')
    expect(wrapper.vm.generalCollateral).toEqual([])
    expect(wrapper.findComponent(TiptapVuetify).exists()).toBe(true)
  })

  it('shows saved general collateral', async () => {
    await store.setGeneralCollateral([{ descriptionAdd: 'addexample', descriptionDelete: 'othertest' }])

    wrapper = createComponent(false)
    expect(wrapper.vm.addDesc).toBe('addexample')
    expect(wrapper.vm.delDesc).toBe('othertest')
  })

  it('does not show existing general collateral from previous amendment', async () => {
    await store.setGeneralCollateral(
      [{ descriptionAdd: 'addexample', descriptionDelete: 'othertest', addedDateTime: '2021-10-13' }])

    wrapper = createComponent(false)
    expect(wrapper.vm.addDesc).toBe('')
    expect(wrapper.vm.delDesc).toBe('')
  })

  it('updates general collateral', async () => {
    await store.setGeneralCollateral([])
    wrapper = createComponent(false)
    wrapper.vm.delDesc = 'JOE'
    wrapper.vm.addDesc = 'SCHMOE'
    wrapper.find(doneButtonSelector).trigger('click')
    expect(getLastEvent(wrapper, 'closeGenColAmend')).toBeTruthy()
    await flushPromises()
    // store should have 1 item now
    expect(store.getAddCollateral.generalCollateral.length).toBe(1)
  })

  it('saves amended general collateral over the previous one', async () => {
    await store.setGeneralCollateral(
      [{ descriptionAdd: 'addexample', descriptionDelete: 'othertest' }])
    wrapper = createComponent(false)
    wrapper.vm.delDesc = 'JOE'
    wrapper.vm.addDesc = 'SCHMOE'
    wrapper.find(doneButtonSelector).trigger('click')
    expect(getLastEvent(wrapper, 'closeGenColAmend')).toBeTruthy()
    await flushPromises()
    // store should still have 1 item now (replaced the last one)
    expect(store.getAddCollateral.generalCollateral.length).toBe(1)
    expect(store.getAddCollateral.generalCollateral[0].descriptionAdd).toBe('SCHMOE')
  })
})
