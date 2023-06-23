// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import { defaultFlagSet } from '@/utils'
import { TiptapVuetifyPlugin, TiptapVuetify } from 'tiptap-vuetify'

import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { GenColEdit } from '@/components/collateral'
import { RegistrationFlowType } from '@/enums'

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
const generalCollateralEdit = '#general-collateral'
const newDescriptionTxt = '#general-collateral-new-desc'
const errorMsg = '.v-messages__message'
const showError = '.invalid-message'

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
  return mount((GenColEdit as any), {
    localVue,
    propsData: { showInvalid: showInvalid },
    store,
    vuetify
  })
}

describe('GenColEdit tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    defaultFlagSet['assets-tiptap-enabled'] = false
    await store.setGeneralCollateral([])
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders default with no existing collateral', async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    wrapper = createComponent(false)
    expect(wrapper.findComponent(GenColEdit).exists()).toBe(true)
    expect(wrapper.vm.newDesc).toBe('')
    expect(wrapper.vm.generalCollateral).toEqual([])
    expect(wrapper.vm.showErrorComponent).toBe(false)
    expect(wrapper.findAll(generalCollateralEdit).length).toBe(1)
    expect(wrapper.findComponent(TiptapVuetify).exists()).toBe(true)
    expect(wrapper.findAll(errorMsg).length).toBe(0)
    expect(wrapper.findAll(showError).length).toBe(0)
  })

  it('updates general collateral with new description text', async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    wrapper = createComponent(false)
    wrapper.vm.newDesc = 'new description'
    await nextTick()
    expect(wrapper.vm.generalCollateral).toEqual([{ description: 'new description' }])
  })

  it('updates new description text with existing general collateral txt in new registration', async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    await store.setGeneralCollateral([{ description: 'existing general collateral' }])
    wrapper = createComponent(false)
    expect(wrapper.vm.generalCollateral).toEqual([{ description: 'existing general collateral' }])
    expect(wrapper.vm.newDesc).toBe('existing general collateral')
  })

  it('shows error bar when set', async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    wrapper = createComponent(true)
    expect(wrapper.findAll(generalCollateralEdit).length).toBe(1)
    expect(wrapper.findComponent(TiptapVuetify).exists()).toBe(true)
    expect(wrapper.findAll(errorMsg).length).toBe(0)
    expect(wrapper.findAll(showError).length).toBe(1)
  })
})
