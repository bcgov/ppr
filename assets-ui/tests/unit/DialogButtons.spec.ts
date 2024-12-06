import flushPromises from 'flush-promises'
import { DialogButtons } from '@/components/dialogs/common'
import { createComponent, getLastEvent } from './utils'
import { nextTick } from 'vue'

// emitted events
const proceed: string = 'proceed'

// Input field selectors / buttons
const accept: string = '#accept-btn'
const cancel: string = '#cancel-btn'

describe('Dialog Button tests', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(DialogButtons, {
      setAcceptText: '',
      setCancelText: ''
    })
    await flushPromises()
  })


  it('renders the component', async () => {
    expect(wrapper.findComponent(DialogButtons).exists()).toBe(true)
    expect(wrapper.vm.$props.setAcceptText).toBe('')
    expect(wrapper.vm.$props.setCancelText).toBe('')
    expect(wrapper.findAll(accept).length).toBe(0)
    expect(wrapper.findAll(cancel).length).toBe(0)
  })

  it('shows buttons when given', async () => {
    const newAcceptText = 'accept'
    const newCancelText = 'cancel'
    wrapper = await createComponent(DialogButtons, {
      setAcceptText: newAcceptText,
      setCancelText: newCancelText
    })
    await nextTick()
    expect(wrapper.vm.$props.setAcceptText).toBe(newAcceptText)
    expect(wrapper.vm.$props.setCancelText).toBe(newCancelText)
    expect(wrapper.findAll(accept).length).toBe(1)
    expect(wrapper.find(accept).text()).toContain(newAcceptText)
    expect(wrapper.findAll(cancel).length).toBe(1)
    expect(wrapper.find(cancel).text()).toContain(newCancelText)
  })

  it('Emits the button actions', async () => {
    wrapper = await createComponent(DialogButtons, {
      setAcceptText: 'accept',
      setCancelText: 'cancel'
    })
    await nextTick()
    expect(wrapper.find(accept).exists()).toBe(true)
    await wrapper.find(accept).trigger('click')
    expect(getLastEvent(wrapper, proceed)).toEqual(true)
    expect(wrapper.find(cancel).exists()).toBe(true)
    await wrapper.find(cancel).trigger('click')
    expect(getLastEvent(wrapper, proceed)).toEqual(false)
  })
})
