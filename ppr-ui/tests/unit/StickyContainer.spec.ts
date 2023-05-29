// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'

import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'

// Components
import { ButtonsStacked, StickyContainer } from '@/components/common'
import { FeeSummary } from '@/composables/fees'
// unit test stuff
import { getLastEvent } from './utils'
import { FeeSummaryTypes } from '@/composables/fees/enums'
import { RegistrationLengthI } from '@/composables/fees/interfaces'
import { UIRegistrationTypes } from '@/enums'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()

// selectors
const errMsg = '.err-msg'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<any> object with the given parameters.
 */
function createComponent (
  showButtons: boolean,
  showFeeSummary: boolean,
  feeType: FeeSummaryTypes,
  registrationLength: RegistrationLengthI,
  registrationType: UIRegistrationTypes,
  backBtn: string,
  cancelBtn: string,
  submitBtn: string
): Wrapper<any> {
  const localVue = createLocalVue()

  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')

  return mount((StickyContainer as any), {
    localVue,
    propsData: {
      setShowButtons: showButtons,
      setShowFeeSummary: showFeeSummary,
      setFeeType: feeType,
      setRegistrationLength: registrationLength,
      setRegistrationType: registrationType,
      setBackBtn: backBtn,
      setCancelBtn: cancelBtn,
      setSubmitBtn: submitBtn
    },
    store,
    vuetify
  })
}

describe('Sticky Container component tests', () => {
  let wrapper: any

  const registrationLength: RegistrationLengthI = {
    lifeInfinite: false,
    lifeYears: 0
  }

  beforeEach(async () => {
  })

  afterEach(() => {
    wrapper.destroy()
  })

  it('renders component with default null values', async () => {
    // default blank
    wrapper = createComponent(false, false, null, null, null, '', '', '')
    await flushPromises()

    expect(wrapper.findComponent(StickyContainer).exists()).toBe(true)
    expect(wrapper.findComponent(FeeSummary).exists()).toBe(false)
    expect(wrapper.findComponent(ButtonsStacked).exists()).toBe(false)
    expect(wrapper.findAll(errMsg).length).toBe(0)
  })

  it('renders component with given fee summary values', async () => {
    wrapper = createComponent(
      false, // showButtons
      true, // showFeeSummary
      FeeSummaryTypes.NEW, // feeType
      { ...registrationLength }, // reg length
      UIRegistrationTypes.SECURITY_AGREEMENT, // reg type
      '', // back btn
      '', // cancel btn
      '' // submit btn
    )
    await flushPromises()

    expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
    expect(wrapper.findComponent(ButtonsStacked).exists()).toBe(false)
    expect(wrapper.props().setFeeType).toBe(FeeSummaryTypes.NEW)
    expect(wrapper.findComponent(FeeSummary).vm.$props.setFeeType).toBe(FeeSummaryTypes.NEW)
    expect(wrapper.vm.registrationLength).toEqual(registrationLength)
    expect(wrapper.findComponent(FeeSummary).vm.$props.setRegistrationLength).toEqual(registrationLength)
    expect(wrapper.vm.registrationType).toBe(UIRegistrationTypes.SECURITY_AGREEMENT)
    expect(wrapper.findComponent(FeeSummary).vm.$props.setRegistrationType).toBe(UIRegistrationTypes.SECURITY_AGREEMENT)
    // default has no fee override
    expect(store.getStateModel.userInfo.feeSettings).toBe(null)
    expect(wrapper.findComponent(FeeSummary).vm.$props.setFeeOverride).toBeNull()
    // updates fee summary when user is non billable
    await store.setUserInfo({ feeSettings: { isNonBillable: true, serviceFee: 2.5 } })
    const expectedFeeOveride = { feeAmount: 0, processingFee: null, quantity: null, serviceFee: 2.5 }
    expect(wrapper.findComponent(FeeSummary).vm.$props.setFeeOverride).toEqual(expectedFeeOveride)

    // updates fee summary with registration length chages
    const newRegistrationLength: RegistrationLengthI = {
      lifeInfinite: false,
      lifeYears: 6
    }
    await wrapper.setProps({
      setRegistrationLength: newRegistrationLength
    })

    expect(wrapper.vm.$props.setRegistrationLength).toEqual(newRegistrationLength)
    expect(wrapper.vm.registrationLength).toEqual(newRegistrationLength)
    expect(wrapper.findComponent(FeeSummary).vm.$props.setRegistrationLength).toEqual(newRegistrationLength)
  })

  it('renders component with given button stacked values', async () => {
    const back = 'back'
    const cancel = 'cancel'
    const submit = 'submit'
    wrapper = createComponent(
      true, // showButtons
      false, // showFeeSummary
      null, // feeType
      null, // reg length
      null, // reg type
      back, // back btn
      cancel, // cancel btn
      submit // submit btn
    )
    await flushPromises()

    expect(wrapper.findComponent(FeeSummary).exists()).toBe(false)
    expect(wrapper.findComponent(ButtonsStacked).exists()).toBe(true)
    expect(wrapper.findComponent(ButtonsStacked).vm.$props.setBackBtn).toBe(back)
    expect(wrapper.vm.cancelBtn).toBe(cancel)
    expect(wrapper.findComponent(ButtonsStacked).vm.$props.setCancelBtn).toBe(cancel)
    expect(wrapper.findComponent(ButtonsStacked).vm.$props.setSubmitBtn).toBe(submit)
  })

  it('renders both fee summary and buttons when needed', async () => {
    wrapper = createComponent(
      true, // showButtons
      true, // showFeeSummary
      FeeSummaryTypes.NEW, // feeType
      { ...registrationLength }, // reg length
      UIRegistrationTypes.SECURITY_AGREEMENT, // reg type
      'back', // back btn
      'cancel', // cancel btn
      'submit' // submit btn
    )
    await flushPromises()

    expect(wrapper.findComponent(FeeSummary).exists()).toBe(true)
    expect(wrapper.findComponent(ButtonsStacked).exists()).toBe(true)
  })

  it('emits button actions', async () => {
    wrapper = createComponent(
      true, // showButtons
      true, // showFeeSummary
      FeeSummaryTypes.NEW, // feeType
      { ...registrationLength }, // reg length
      UIRegistrationTypes.SECURITY_AGREEMENT, // reg type
      'back', // back btn
      'cancel', // cancel btn
      'submit' // submit btn
    )
    await flushPromises()

    await wrapper.findComponent(ButtonsStacked).vm.$emit('back')
    expect(getLastEvent(wrapper, 'back')).toBe(true)
    await wrapper.findComponent(ButtonsStacked).vm.$emit('cancel')
    expect(getLastEvent(wrapper, 'cancel')).toBe(true)
    await wrapper.findComponent(ButtonsStacked).vm.$emit('submit')
    expect(getLastEvent(wrapper, 'submit')).toBe(true)
  })

  it('displays err message when given', async () => {
    wrapper = createComponent(false, false, null, null, null, '', '', '')
    expect(wrapper.findAll(errMsg).length).toBe(0)
    const msg = 'test error msg'
    await wrapper.setProps({ setErrMsg: msg })
    expect(wrapper.findAll(errMsg).length).toBe(1)
    expect(wrapper.findAll(errMsg).at(0).text()).toBe(msg)
  })
})
