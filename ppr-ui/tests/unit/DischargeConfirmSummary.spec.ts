// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'

// Components
import { DischargeConfirmSummary } from '@/components/common'

// enums, etc.
import { UIRegistrationTypes } from '@/enums'

// test stuff
import { getLastEvent } from './utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
const store = getVuexStore()

// selectors
const summaryInfo = '.summary-info'
const checkboxTxtNormal = '.copy-normal p'
const checkboxTxtError = '.check-box-error p'
const checkboxId1 = '#discharge-confirm-checkbox-1'
const checkboxId2 = '#discharge-confirm-checkbox-2'
const checkboxId3 = '#discharge-confirm-checkbox-3'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchedResultPPR> object with the given parameters.
 */
function createComponent (
  setRegNum: string,
  setRegType: String,
  setCollateralSummary: String,
  setShowErrors: Boolean
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')

  return mount(DischargeConfirmSummary, {
    localVue,
    propsData: {
      setRegNum: setRegNum,
      setRegType: setRegType,
      setCollateralSummary: setCollateralSummary,
      setShowErrors: setShowErrors
    },
    store,
    vuetify
  })
}

describe('Discharge confirm summary component tests', () => {
  let wrapper: any
  const regNum = '123456B'
  const regType = UIRegistrationTypes.SECURITY_AGREEMENT
  const colSummary = 'General Collateral and 3 Vehicles'
  const showErrors = false

  beforeEach(async () => {
    wrapper = createComponent(regNum, regType, colSummary, showErrors)
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders component with given props', () => {
    const component = wrapper.findComponent(DischargeConfirmSummary)
    expect(component.exists()).toBe(true)
    expect(component.vm.$data.checkbox1).toBe(false)
    expect(component.vm.$data.checkbox2).toBe(false)
    expect(component.vm.$data.checkbox3).toBe(false)
    expect(component.vm.valid).toBe(false)
    const info = wrapper.findAll(summaryInfo)
    expect(info.length).toBe(1)
    expect(info.at(0).text()).toContain(`Base Registration Number: ${regNum}`)
    expect(info.at(0).text()).toContain(`Registration Type: ${regType}`)
    expect(info.at(0).text()).toContain(`Collateral: ${colSummary}`)
    expect(wrapper.findAll(checkboxId1).length).toBe(1)
    expect(wrapper.findAll(checkboxId2).length).toBe(1)
    expect(wrapper.findAll(checkboxId3).length).toBe(1)
    const checkboxTxt = wrapper.findAll(checkboxTxtNormal)
    expect(checkboxTxt.length).toBe(3)
    expect(checkboxTxt.at(0).text()).toContain('discharge this registration.')
    expect(checkboxTxt.at(1).text()).toContain('all collateral on this registration will be released.')
    expect(checkboxTxt.at(2).text()).toContain('all Secured Parties will be notified.')
    expect(wrapper.findAll(checkboxTxtError).length).toBe(0)
  })

  it('validates with checkboxes', async () => {
    const checkbox1 = wrapper.findAll(checkboxId1)
    checkbox1.trigger('click')
    await flushPromises()
    expect(wrapper.vm.$data.checkbox1).toBe(true)
    // still not valid (1/3)
    expect(wrapper.vm.valid).toBe(false)
    expect(getLastEvent(wrapper, 'valid')).toBeNull()
    const checkbox2 = wrapper.findAll(checkboxId2)
    checkbox2.trigger('click')
    await flushPromises()
    expect(wrapper.vm.$data.checkbox2).toBe(true)
    // still not valid (2/3)
    expect(wrapper.vm.valid).toBe(false)
    expect(getLastEvent(wrapper, 'valid')).toBeNull()
    const checkbox3 = wrapper.findAll(checkboxId3)
    checkbox3.trigger('click')
    await flushPromises()
    expect(wrapper.vm.$data.checkbox3).toBe(true)
    // should be valid now (3/3)
    expect(wrapper.vm.valid).toBe(true)
    expect(getLastEvent(wrapper, 'valid')).toBe(true)

    checkbox2.trigger('click')
    await flushPromises()
    expect(wrapper.vm.$data.checkbox2).toBe(false)
    // should be invalid again
    expect(wrapper.vm.valid).toBe(false)
    expect(getLastEvent(wrapper, 'valid')).toBe(false)
  })

  it('shows validation when asked by prop', async () => {
    expect(wrapper.findAll(checkboxTxtNormal).length).toBe(3)
    expect(wrapper.findAll(checkboxTxtError).length).toBe(0)
    await wrapper.setProps({ setShowErrors: true })
    expect(wrapper.findAll(checkboxTxtNormal).length).toBe(0)
    expect(wrapper.findAll(checkboxTxtError).length).toBe(3)
    const checkbox1 = wrapper.findAll(checkboxId1)
    checkbox1.trigger('click')
    await flushPromises()
    expect(wrapper.findAll(checkboxTxtNormal).length).toBe(1)
    expect(wrapper.findAll(checkboxTxtError).length).toBe(2)
    const checkbox2 = wrapper.findAll(checkboxId2)
    checkbox2.trigger('click')
    await flushPromises()
    expect(wrapper.findAll(checkboxTxtNormal).length).toBe(2)
    expect(wrapper.findAll(checkboxTxtError).length).toBe(1)
    const checkbox3 = wrapper.findAll(checkboxId3)
    checkbox3.trigger('click')
    await flushPromises()
    expect(wrapper.findAll(checkboxTxtNormal).length).toBe(3)
    expect(wrapper.findAll(checkboxTxtError).length).toBe(0)

    checkbox2.trigger('click')
    await flushPromises()
    expect(wrapper.findAll(checkboxTxtNormal).length).toBe(2)
    expect(wrapper.findAll(checkboxTxtError).length).toBe(1)
    expect(wrapper.findAll(checkboxTxtError).at(0).text()).toContain(
      'all collateral on this registration will be released.'
    )
  })
})
