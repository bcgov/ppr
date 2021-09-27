// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import {
  mockedSelectSecurityAgreement
} from './test-data'

// local components
import { GenColEdit, GenColSummary, GeneralCollateral } from '@/components/collateral'
// local types/helpers/etc.
import { APIRegistrationTypes, RegistrationFlowType } from '@/enums'
import { getLastEvent } from './utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

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
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(GeneralCollateral, {
    localVue,
    propsData: {
      isSummary: isSummary,
      setShowInvalid: setShowInvalid
    },
    store,
    vuetify
  })
}

describe('General Collateral tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.NEW)
    await store.dispatch('setAddCollateral', {
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
    // passes validation from edit component
    wrapper.findComponent(GenColEdit).vm.$emit('valid', false)
    expect(getLastEvent(wrapper, 'valid')).toBe(false)
  })
})
