// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import CompositionApi from '@vue/composition-api'
import { getVuexStore } from '@/store'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'

// Components
import { CertifyInformation } from '@/components/common'
import { CertifyIF } from '@/interfaces'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()
const certifyInitial: CertifyIF = {
  valid: false,
  certified: false,
  legalName: ''
}
const certifyValid: CertifyIF = {
  valid: true,
  certified: true,
  legalName: 'legal name'
}

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (
  showErrors: boolean
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')
  return mount(CertifyInformation, {
    localVue,
    propsData: { setShowErrors: showErrors },
    store,
    vuetify
  })
}

// Prevent the warning "[Vuetify] Unable to locate target [data-app]"
document.body.setAttribute('data-app', 'true')

describe('Certify Information on the confirmation page', () => {
  let wrapper: any

  beforeEach(async () => {
    await store.dispatch('setCertifyInformation', certifyInitial)
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders the view with text box, checkbox', () => {
    wrapper = createComponent(false)
    expect(wrapper.findComponent(CertifyInformation).exists()).toBe(true)
    expect(wrapper.find('#txt-legal-name').exists()).toBe(true)
    expect(wrapper.find('#checkbox-certified').exists()).toBe(true)
  })

  it('renders the certify information valid data from the store', async () => {
    await store.dispatch('setCertifyInformation', certifyValid)
    wrapper = createComponent(false)
    const certifyInfo:CertifyIF = wrapper.vm.certifyInformation
    expect(certifyInfo.legalName).toEqual('legal name')
    expect(certifyInfo.certified).toBeTruthy()
    expect(certifyInfo.valid).toBeTruthy()
    expect(wrapper.vm.legalName).toEqual('legal name')
    expect(wrapper.vm.valid).toBeTruthy()
    expect(wrapper.vm.legalNameMessage).toEqual('')
    expect(wrapper.vm.checkboxMessage).toEqual('')
    expect(wrapper.vm.showErrors).toBeFalsy()
    expect(wrapper.vm.showErrorComponent).toBeFalsy()
  })

  it('renders the certify information invalid data from the store', async () => {
    wrapper = createComponent(true)
    const certifyInfo:CertifyIF = wrapper.vm.certifyInformation
    expect(certifyInfo.legalName).toEqual('')
    expect(certifyInfo.certified).toBeFalsy()
    expect(certifyInfo.valid).toBeFalsy()
    expect(wrapper.vm.legalName).toEqual('')
    expect(wrapper.find('#txt-legal-name').element.value).toBe('')
    expect(wrapper.vm.certified).toBeFalsy()
    expect(wrapper.find('#checkbox-certified').element.value).toBeFalsy()
    expect(wrapper.vm.valid).toBeFalsy()
    expect(wrapper.vm.legalNameMessage.length).toBeGreaterThan(0)
    expect(wrapper.vm.checkboxMessage.length).toBeGreaterThan(0)
    expect(wrapper.vm.showErrors).toBeTruthy()
    expect(wrapper.vm.showErrorComponent).toBeTruthy()
  })

  it('renders the certify information transition from initial to valid state', async () => {
    wrapper = createComponent(true)
    wrapper.find('#checkbox-certified').trigger('click')
    wrapper.find('#txt-legal-name').setValue('Valid name')
    await Vue.nextTick()
    await Vue.nextTick()
    await Vue.nextTick()
    expect(wrapper.vm.valid).toBeTruthy()
    expect(wrapper.emitted().certifyValid).toBeTruthy()
    expect(wrapper.vm.showErrorComponent).toBeFalsy()
  })

  it('sets the validity to false when legal name > 100 characters', async () => {
    wrapper = createComponent(false)
    wrapper.find('#checkbox-certified').trigger('click')
    wrapper.find('#txt-legal-name').setValue('Valid name')
    await Vue.nextTick()
    await Vue.nextTick()
    await Vue.nextTick()
    expect(wrapper.vm.valid).toBeTruthy()
    const invalidLengthTxt = 'x'.repeat(101)
    wrapper.find('#txt-legal-name').setValue(invalidLengthTxt)
    await Vue.nextTick()
    await Vue.nextTick()
    await Vue.nextTick()
    expect(wrapper.vm.valid).toBeFalsy()
    expect(wrapper.emitted().certifyValid).toBeTruthy()
  })
})
