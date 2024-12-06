import { nextTick } from 'vue'
import { LargeSearchDelayDialog } from '@/components/dialogs'
import {
  largeSearchReportDelay
} from '@/resources/dialogOptions'
import { createComponent, getLastEvent } from './utils'

// emitted events
const proceed: string = 'proceed'

// Input field selectors / buttons
const accept: string = '#accept-btn'
const text: string = '.dialog-text'
const title: string = '.dialog-title'

describe('Delay Dialog', () => {
  let wrapper

  beforeEach(async () => {
    wrapper = await createComponent(LargeSearchDelayDialog, {
      setDisplay: true,
      setOptions: largeSearchReportDelay,
      setNumberRegistrations: 75
    })
    await nextTick()
  })

  it('renders the component with the options', async () => {
    const options = largeSearchReportDelay

    expect(wrapper.findComponent(LargeSearchDelayDialog).exists()).toBe(true)
    expect(wrapper.isVisible()).toBe(true)
    expect(wrapper.find(title).text()).toBe(options.title)
    expect(wrapper.find(text).text()).toContain(options.text)
    expect(wrapper.find(accept).exists()).toBe(true)
    wrapper.find(accept).trigger('click')
    await nextTick()
    expect(getLastEvent(wrapper, proceed)).toEqual(true)
  })
})
