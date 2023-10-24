// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// local components
import { GenColEdit, GenColSummary, GeneralCollateral, GenColAmend } from '@/components/collateral'
// local types/helpers/etc.
import { RegistrationFlowType } from '@/enums'

Vue.use(Vuetify)
const vuetify = new Vuetify({})

setActivePinia(createPinia())
const store = useStore()

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (
  isSummary: boolean,
  setShowInvalid: boolean
): Wrapper<any> {
  const localVue = createLocalVue()

  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount((GeneralCollateral as any), {
    localVue,
    propsData: {
      isSummary,
      setShowInvalid
    },
    store,
    vuetify
  })
}

describe('General Collateral tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.NEW)
    await store.setAddCollateral({
      generalCollateral: [],
      vehicleCollateral: [],
      valid: false,
      showInvalid: false
    })
  })
  afterEach(() => {
    wrapper.destroy()
  })

  it('renders summary view when prop set', async () => {
    wrapper = createComponent(true, false)
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(true)
    expect(wrapper.findComponent(GenColSummary).exists()).toBe(true)
    expect(wrapper.findComponent(GenColEdit).exists()).toBe(false)
  })

  it('renders edit view when prop set', async () => {
    wrapper = createComponent(false, false)
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(true)
    expect(wrapper.findComponent(GenColSummary).exists()).toBe(false)
    expect(wrapper.findComponent(GenColEdit).exists()).toBe(true)
    expect(wrapper.findComponent(GenColEdit).vm.$props.showInvalid).toBe(false)
    // updates showInvalid on change
    await wrapper.setProps({ setShowInvalid: true })
    expect(wrapper.findComponent(GenColEdit).vm.$props.showInvalid).toBe(true)
  })

  it('renders amendment view for amendments', async () => {
    await store.setRegistrationFlowType(RegistrationFlowType.AMENDMENT)
    wrapper = createComponent(true, false)
    wrapper.vm.$data.amendMode = true
    expect(wrapper.findComponent(GeneralCollateral).exists()).toBe(true)
    expect(wrapper.findComponent(GenColAmend).exists()).toBe(false)
  })
})
