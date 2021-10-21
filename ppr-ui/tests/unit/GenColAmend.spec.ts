// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { GenColAmend } from '@/components/collateral'
import { RegistrationFlowType } from '@/enums'
import { getLastEvent } from './utils'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

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
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(GenColAmend, {
    localVue,
    propsData: { showInvalid: showInvalid },
    store,
    vuetify
  })
}

describe('GenColAmend tests', () => {
  let wrapper: Wrapper<any>

  beforeEach(async () => {
    await store.dispatch('setRegistrationFlowType', RegistrationFlowType.AMENDMENT)
    await store.dispatch('setGeneralCollateral', [])
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
    expect(wrapper.findAll(deleteDescriptionTxt).length).toBe(1)
    expect(wrapper.findAll(addDescriptionTxt).length).toBe(1)

  })

  it('shows saved general collateral', async () => {
   
    await store.dispatch('setGeneralCollateral', [{ descriptionAdd: 'addexample', descriptionDelete: 'othertest' }])
    
    wrapper = createComponent(false)
    expect(wrapper.vm.addDesc).toBe('addexample')
    expect(wrapper.vm.delDesc).toBe('othertest')
  })

  it('does not show existing general collateral from previous amendment', async () => {
   
    await store.dispatch('setGeneralCollateral',
    [{ descriptionAdd: 'addexample', descriptionDelete: 'othertest', addedDateTime: '2021-10-13' }])
    
    wrapper = createComponent(false)
    expect(wrapper.vm.addDesc).toBe('')
    expect(wrapper.vm.delDesc).toBe('')
  })

  it('updates general collateral', async () => {
    await store.dispatch('setGeneralCollateral', [])
    wrapper = createComponent(false)
    wrapper.find('#general-collateral-delete-desc').setValue('JOE')
    wrapper.find('#general-collateral-add-desc').setValue('SCHMOE')
    wrapper.find(doneButtonSelector).trigger('click')
    expect(getLastEvent(wrapper, 'closeGenColAmend')).toBeTruthy()
    await flushPromises()
    // store should have 1 item now
    expect(store.getters.getAddCollateral.generalCollateral.length).toBe(1)
  })

})
