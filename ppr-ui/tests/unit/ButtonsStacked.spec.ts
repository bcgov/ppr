// Libraries
import Vue, { nextTick } from 'vue'
import Vuetify from 'vuetify'
import VueRouter from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { useStore } from '../../src/store/store'
import { mount, createLocalVue, Wrapper } from '@vue/test-utils'
import flushPromises from 'flush-promises'

// Components
import { ButtonsStacked } from '@/components/common'
// Other
import { RouteNames } from '@/enums'
// unit test stuff
import { getLastEvent } from './utils'

Vue.use(Vuetify)

const vuetify = new Vuetify({})
setActivePinia(createPinia())
const store = useStore()
// selectors
const backBtn = '#btn-stacked-back'
const cancelBtn = '#btn-stacked-cancel'
const submitBtn = '#btn-stacked-submit'

/**
 * Creates and mounts a component, so that it can be tested.
 *
 * @returns a Wrapper<SearchedResultPpr> object with the given parameters.
 */
function createComponent (
  backBtn: string,
  cancelBtn: string,
  submitBtn: string,
  disabledSubmit: boolean
): Wrapper<any> {
  const localVue = createLocalVue()
  localVue.use(Vuetify)
  document.body.setAttribute('data-app', 'true')

  return mount((ButtonsStacked as any), {
    localVue,
    propsData: {
      setBackBtn: backBtn,
      setCancelBtn: cancelBtn,
      setSubmitBtn: submitBtn,
      setDisableSubmitBtn: disabledSubmit
    },
    store,
    vuetify
  })
}

describe('ButtonsStacked component tests', () => {
  let wrapper: any
  const { assign } = window.location

  beforeEach(async () => {
    // mock the window.location.assign function
    delete window.location
    window.location = { assign: jest.fn() } as any
  })

  afterEach(() => {
    window.location.assign = assign
    wrapper.destroy()
  })

  it('renders ButtonsStacked component with 2 buttons / proper text', () => {
    const backBtnTxt = ''
    const cancelBtnTxt = 'Test1 Cancel'
    const submitBtnTxt = 'Test1 Confirm and Complete'
    wrapper = createComponent(backBtnTxt, cancelBtnTxt, submitBtnTxt, false)
    expect(wrapper.findComponent(ButtonsStacked).exists()).toBe(true)
    const back = wrapper.findAll(backBtn)
    expect(back.length).toBe(0)
    const cancel = wrapper.findAll(cancelBtn)
    expect(cancel.length).toBe(1)
    expect(cancel.at(0).text()).toBe(cancelBtnTxt)
    const submit = wrapper.findAll(submitBtn)
    expect(submit.length).toBe(1)
    expect(submit.at(0).text()).toBe(submitBtnTxt)
  })

  it('renders ButtonsStacked component with 3 buttons / proper text', () => {
    const backBtnTxt = 'Test2 Back'
    const cancelBtnTxt = 'Test2 Cancel'
    const submitBtnTxt = 'Test2 Confirm and Complete'
    wrapper = createComponent(backBtnTxt, cancelBtnTxt, submitBtnTxt, false)
    expect(wrapper.findComponent(ButtonsStacked).exists()).toBe(true)
    const back = wrapper.findAll(backBtn)
    expect(back.length).toBe(1)
    expect(back.at(0).text()).toBe(backBtnTxt)
    const cancel = wrapper.findAll(cancelBtn)
    expect(cancel.length).toBe(1)
    expect(cancel.at(0).text()).toBe(cancelBtnTxt)
    const submit = wrapper.findAll(submitBtn)
    expect(submit.length).toBe(1)
    expect(submit.at(0).text()).toBe(submitBtnTxt)
  })

  it('emits on button clicks', async () => {
    const backBtnTxt = 'Test3 Back'
    const cancelBtnTxt = 'Test3 Cancel'
    const submitBtnTxt = 'Test3 Confirm and Complete'
    wrapper = createComponent(backBtnTxt, cancelBtnTxt, submitBtnTxt, false)
    const back = wrapper.find(backBtn)
    back.trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, 'back')).toBe(true)
    const cancel = wrapper.find(cancelBtn)
    cancel.trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, 'cancel')).toBe(true)
    const submit = wrapper.find(submitBtn)
    submit.trigger('click')
    await flushPromises()
    expect(getLastEvent(wrapper, 'submit')).toBe(true)
  })

  it('disables the submit button', async () => {
    const backBtnTxt = 'Test4 Back'
    const cancelBtnTxt = 'Test4 Cancel'
    const submitBtnTxt = 'Test4 Confirm and Complete'
    wrapper = createComponent(backBtnTxt, cancelBtnTxt, submitBtnTxt, true)

    const submit = wrapper.find(submitBtn)
    expect(submit.attributes('disabled')).toBe('disabled')
  })
})
