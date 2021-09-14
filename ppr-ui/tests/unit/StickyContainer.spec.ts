// Libraries
import Vue from 'vue'
import Vuetify from 'vuetify'
import { getVuexStore } from '@/store'
import CompositionApi from '@vue/composition-api'
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
const store = getVuexStore()

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
  localVue.use(CompositionApi)
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')

  return mount(StickyContainer, {
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
    expect(wrapper.vm.$data.feeType).toBe(FeeSummaryTypes.NEW)
    expect(wrapper.findComponent(FeeSummary).vm.$props.setFeeType).toBe(FeeSummaryTypes.NEW)
    expect(wrapper.vm.$data.registrationLength).toEqual(registrationLength)
    expect(wrapper.findComponent(FeeSummary).vm.$props.setRegistrationLength).toEqual(registrationLength)
    expect(wrapper.vm.$data.registrationType).toBe(UIRegistrationTypes.SECURITY_AGREEMENT)
    expect(wrapper.findComponent(FeeSummary).vm.$props.setRegistrationType).toBe(UIRegistrationTypes.SECURITY_AGREEMENT)

    // updates fee summary with registration length chages
    const newRegistrationLength: RegistrationLengthI = {
      lifeInfinite: false,
      lifeYears: 6
    }
    await wrapper.setProps({
      setRegistrationLength: newRegistrationLength
    })
    
    expect(wrapper.vm.$props.setRegistrationLength).toEqual(newRegistrationLength)
    expect(wrapper.vm.$data.registrationLength).toEqual(newRegistrationLength)
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
    expect(wrapper.vm.$data.backBtn).toBe(back)
    expect(wrapper.findComponent(ButtonsStacked).vm.$props.setBackBtn).toBe(back)
    expect(wrapper.vm.$data.cancelBtn).toBe(cancel)
    expect(wrapper.findComponent(ButtonsStacked).vm.$props.setCancelBtn).toBe(cancel)
    expect(wrapper.vm.$data.submitBtn).toBe(submit)
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
})
