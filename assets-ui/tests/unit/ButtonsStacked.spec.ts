import { createComponent, getLastEvent } from './utils'
import { nextTick } from 'vue'
import { ButtonsStacked } from '@/components/common'
import flushPromises from 'flush-promises'

// selectors
const backBtn = '#btn-stacked-back'
const cancelBtn = '#btn-stacked-cancel'
const submitBtn = '#btn-stacked-submit'

describe('ButtonsStacked component tests', () => {
  let wrapper: any

  it('renders ButtonsStacked component with 2 buttons / proper text', async () => {
    const backBtnTxt = ''
    const cancelBtnTxt = 'Test1 Cancel'
    const submitBtnTxt = 'Test1 Confirm and Complete'
    wrapper = await createComponent(ButtonsStacked, {
      setBackBtn: backBtnTxt,
      setCancelBtn: cancelBtnTxt,
      setSubmitBtn: submitBtnTxt,
      setDisableSubmitBtn: false
    })
    await nextTick()

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

  it('renders ButtonsStacked component with 3 buttons / proper text', async () => {
    const backBtnTxt = 'Test2 Back'
    const cancelBtnTxt = 'Test2 Cancel'
    const submitBtnTxt = 'Test2 Confirm and Complete'
    wrapper = await createComponent(ButtonsStacked, {
      setBackBtn: backBtnTxt,
      setCancelBtn: cancelBtnTxt,
      setSubmitBtn: submitBtnTxt,
      setDisableSubmitBtn: false
    })
    await nextTick()

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
    wrapper = await createComponent(ButtonsStacked, {
      setBackBtn: backBtnTxt,
      setCancelBtn: cancelBtnTxt,
      setSubmitBtn: submitBtnTxt,
      setDisableSubmitBtn: false
    })
    await nextTick()

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
    wrapper = await createComponent(ButtonsStacked, {
      setBackBtn: backBtnTxt,
      setCancelBtn: cancelBtnTxt,
      setSubmitBtn: submitBtnTxt,
      setDisableSubmitBtn: true
    })
    await nextTick()

    const submit = wrapper.find(submitBtn)
    expect(submit.attributes().disabled).toBeDefined()
  })
})
